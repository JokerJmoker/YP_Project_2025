from typing import Dict, Any
from psycopg2.extras import DictCursor
import sys
import os
import json
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.motherboard import MotherboardModel

def extract_pcie_version(interface_str: str) -> float:
    match = re.search(r'PCIe\s*(\d+(\.\d+)?)', interface_str, re.IGNORECASE)
    return float(match.group(1)) if match else 0.0

def extract_highest_pcie_version(slots_description: str) -> float:
    if not slots_description:
        return 0.0
    matches = re.findall(r'PCIe\s*(\d+\.\d+)', slots_description, re.IGNORECASE)
    return max(float(ver) for ver in matches) if matches else 0.0

def parse_power_phases(phases_str: str) -> int:
    if not phases_str:
        return 0
    try:
        return int(phases_str.split('+')[0])
    except (ValueError, AttributeError):
        return 0

def extract_number(value: Any) -> int:
    if isinstance(value, int):
        return value
    if not value:
        return 0
    try:
        match = re.search(r'\d+', str(value))
        return int(match.group()) if match else 0
    except (ValueError, AttributeError):
        return 0

def check_memory_compatibility(dimm: Dict[str, Any], mb: Dict[str, Any]) -> bool:
    if dimm["memory_type"] != mb["memory_type"]:
        return False
    if dimm["modules_count"] > extract_number(mb["memory_slots"]):
        return False
    if extract_number(dimm["total_memory"]) > extract_number(mb["max_memory"]):
        return False
    
    base_freq = extract_number(mb["base_memory_frequency"])
    oc_freqs = [extract_number(f) for f in mb["oc_memory_frequency"].split(",")] if mb["oc_memory_frequency"] else []
    max_supported_freq = max([base_freq] + oc_freqs)
    
    return extract_number(dimm["frequency"]) <= max_supported_freq

def check_ssd_m2_compatibility(ssd_data: Dict[str, Any], mb: Dict[str, Any]) -> bool:
    ssd_interface = ssd_data.get("interface", "")
    ssd_form_factor = ssd_data.get("form_factor", "")
    ssd_pcie_version = extract_pcie_version(ssd_interface)
    
    if ssd_pcie_version > 0:
        mb_pcie_version = extract_pcie_version(mb.get("nvme_pcie_version", ""))
        if mb_pcie_version == 0.0:
            mb_pcie_version = max(
                extract_pcie_version(mb.get("m2_cpu_slots", "")),
                extract_pcie_version(mb.get("m2_chipset_slots", ""))
            )
        if mb_pcie_version > 0 and ssd_pcie_version > mb_pcie_version:
            return False
    
    if check_m2_slot(mb.get("m2_cpu_slots", ""), ssd_form_factor, ssd_interface):
        return True
    if check_m2_slot(mb.get("m2_chipset_slots", ""), ssd_form_factor, ssd_interface):
        return True
    
    return False

def check_m2_slot(slots_info: str, form_factor: str, ssd_interface: str) -> bool:
    if not slots_info or not form_factor:
        return False
    
    slot_matches = re.finditer(
        r'(\d+)\s*x\s*(\d{4}(?:\/\d{4})*)\s*\((.*?)\)', 
        slots_info
    )
    
    for match in slot_matches:
        supported_sizes = match.group(2).split('/')
        slot_desc = match.group(3)
        
        if form_factor not in supported_sizes:
            continue
            
        if "PCIe" in ssd_interface and "PCIe" in slot_desc:
            return True
        if "SATA" in ssd_interface and "SATA" in slot_desc:
            return True
    
    return False

def find_compatible_motherboard(
    cpu_data: Dict[str, Any], 
    gpu_data: Dict[str, Any],
    dimm_data: Dict[str, Any],
    ssd_m2_data: Dict[str, Any]
) -> Dict[str, Any]:
    socket = cpu_data.get("socket", "").strip()
    cpu_pcie_str = cpu_data.get("pci_express", "")
    required_cpu_pcie_version = extract_pcie_version(cpu_pcie_str)
    
    gpu_interface = gpu_data.get("interface", "")
    gpu_slot_width = gpu_data.get("slot_width", "")
    required_gpu_pcie_version = extract_pcie_version(gpu_interface)

    dimm_memory_type = dimm_data["memory_type"]
    dimm_modules_count = dimm_data["modules_count"]
    dimm_total_memory = extract_number(dimm_data["total_memory"])
    dimm_freq = dimm_data["frequency"]

    query = """
        SELECT * FROM pc_components.motherboard
        WHERE socket = %(socket)s
        AND memory_type = %(memory_type)s
        AND COALESCE(CAST(NULLIF(REGEXP_REPLACE(memory_slots, '[^0-9]', '', 'g'), '') AS INTEGER), 0) >= %(modules_count)s
        AND COALESCE(CAST(NULLIF(REGEXP_REPLACE(max_memory, '[^0-9]', '', 'g'), '') AS INTEGER), 0) >= %(total_memory)s
    """

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, {
                "socket": socket,
                "memory_type": dimm_memory_type,
                "modules_count": dimm_modules_count,
                "total_memory": dimm_total_memory
            })
            results = cursor.fetchall()
            
            if not results:
                raise ValueError(f"Не найдено плат с сокетом '{socket}' и поддержкой RAM")

            compatible = []
            for row in results:
                max_pcie_version = extract_highest_pcie_version(row.get("pcie_x16_slots", ""))
                cpu_ok = max_pcie_version >= required_cpu_pcie_version
                
                gpu_ok = False
                if gpu_slot_width == "PCIe x16":
                    gpu_ok = "x16" in row.get("pcie_x16_slots", "").lower()
                
                ram_ok = True
                if "base_memory_frequency" in row and "oc_memory_frequency" in row:
                    base_freq = extract_number(row["base_memory_frequency"])
                    oc_freqs = [extract_number(f) for f in row["oc_memory_frequency"].split(",")] if row["oc_memory_frequency"] else []
                    max_supported_freq = max([base_freq] + oc_freqs)
                    ram_ok = dimm_freq <= max_supported_freq
                
                ssd_m2_ok = check_ssd_m2_compatibility(ssd_m2_data, row)
                
                if cpu_ok and gpu_ok and ram_ok and ssd_m2_ok:
                    compatible.append(row)

            if not compatible:
                raise ValueError("Нет полностью совместимых плат с заданными компонентами")

            best_match = max(
                compatible,
                key=lambda x: (
                    extract_highest_pcie_version(x.get("pcie_x16_slots", "")),
                    parse_power_phases(x.get("power_phases", "")),
                    -float(x.get("price", 0))
                )
            )
            
            return MotherboardModel.from_orm(best_match).model_dump()
            
def run_motherboard_selection_test(
    cpu_data: Dict[str, Any], 
    gpu_data: Dict[str, Any],
    dimm_data: Dict[str, Any],
    ssd_m2_data: Dict[str, Any]
) -> None:
    try:
        motherboard_info = find_compatible_motherboard(cpu_data, gpu_data, dimm_data, ssd_m2_data)
        print("Найдена совместимая материнская плата:")
        print(json.dumps(motherboard_info, indent=4, ensure_ascii=False))
    except ValueError as e:
        print(f"Ошибка: {e}")

chosen_cpu = {
    "id": 176,
    "name": "Процессор Intel Core i7-14700KF BOX",
    "price": 34999,
    "socket": "LGA 1700",
    "tdp": 253,
    "base_tdp": 125,
    "cooler_included": True,
    "total_cores": 20,
    "performance_cores": 8,
    "efficiency_cores": 12,
    "max_threads": 28,
    "base_frequency": 3.4,
    "turbo_frequency": 5.6,
    "unlocked_multiplier": True,
    "memory_type": "DDR4, DDR5",
    "max_memory": 192,
    "memory_channels": 2,
    "memory_frequency": 5600,
    "integrated_graphics": False,
    "gpu_model": "",
    "pci_express": "PCIe 5.0",
    "pci_lanes": 20,
    "benchmark_rate": 33.02
}
chosen_gpu = {
    "id": 293,
    "name": "Видеокарта KFA2 GeForce RTX 5070Ti ROCK(X) 3FAN RGB WHITE [57IZN6MDBVGK]",
    "price": 99999,
    "interface": "PCIe 5.0",
    "slot_width": "PCIe x16",
    "low_profile": False,
    "slots": "2.5",
    "length": 322,
    "width": 130,
    "thickness": 52,
    "tdp": 300,
    "power_connectors": "16 pin (12V-2x6)",
    "recommended_psu": 750,
    "gpu_model": "GeForce RTX 5070 Ti",
    "architecture": "NVIDIA Blackwell",
    "vram_size": 16,
    "vram_type": "GDDR7",
    "bus_width": 256,
    "base_clock": 2295,
    "boost_clock": 2512,
    "cuda_cores": 8960,
    "ray_tracing": True,
    "tensor_cores": 2,
    "video_outputs": "3 x DisplayPort, HDMI",
    "max_resolution": "7680x4320 (8K Ultra HD)",
    "benchmark_rate": 81.21
}
chosen_ssd_m2 = {
    "id": 358,
    "name": "2000 ГБ M.2 NVMe накопитель MSI SPATIUM M470 PRO [S78-440Q990-P83]",
    "price": 11499,
    "capacity": "2000",
    "form_factor": "2280",
    "interface": "PCIe 4.0 x4",
    "m2_key": "M",
    "nvme": True,
    "controller": "Phison E27T",
    "cell_type": "",
    "memory_structure": "3D NAND",
    "has_dram": False,
    "dram_size": "",
    "max_read_speed": 6000,
    "max_write_speed": 5000,
    "random_read_iops": 950000,
    "random_write_iops": 950000,
    "length": 80,
    "width": 22,
    "thickness": 215,
    "weight": 12,
    "heatsink_included": False
}
chosen_dimm = {
    "id": 750,
    "name": "Оперативная память Kingston Fury Renegade White [KF576C38RWK2-32] 32 ГБ",
    "price": 22799,
    "memory_type": "DDR5",
    "module_type": "UDIMM",
    "total_memory": 32,
    "modules_count": 2,
    "frequency": 7600,
    "ecc_memory": False,
    "registered_memory": False,
    "cas_latency": 38,
    "ras_to_cas_delay": 46,
    "row_precharge_delay": 46,
    "activate_to_precharge_delay": False,
    "voltage": 1.45,
    "intel_xmp": "6800 МГц (36-42-42), 7200 MHz (38-44-44), 7600 MHz (38-46-46)",
    "amd_expo": "нет",
    "height": 392,
    "low_profile": False
}


# Пример запуска:
run_motherboard_selection_test(cpu_data=chosen_cpu, gpu_data=chosen_gpu, dimm_data=chosen_dimm, ssd_m2_data=chosen_ssd_m2)
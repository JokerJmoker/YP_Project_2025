from typing import Dict, Any
from psycopg2.extras import DictCursor
import sys
import os
import json
# Добавляем корневой путь проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.motherboard import MotherboardModel
import re


def extract_pcie_version(interface_str: str) -> float:
    """
    Извлекает версию PCIe из строки, например 'PCIe 5.0' -> 5.0
    Если не удаётся определить, возвращает 0.0
    """
    match = re.search(r'PCIe\s*(\d+(\.\d+)?)', interface_str, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 0.0

def extract_highest_pcie_version(slots_description: str) -> float:
    """
    Извлекает максимальную версию PCIe из строки с описанием слотов.
    Пример: "1 x PCIe 3.0 (x4), 1 x PCIe 5.0 (x16)" -> 5.0
    """
    if not slots_description:
        return 0.0
    
    matches = re.findall(r'PCIe\s*(\d+\.\d+)', slots_description, re.IGNORECASE)
    if not matches:
        return 0.0
    
    versions = [float(ver) for ver in matches]
    return max(versions)
def extract_highest_pcie_version(slots_description: str) -> float:
    """Извлекает максимальную версию PCIe из описания слотов"""
    if not slots_description:
        return 0.0
    matches = re.findall(r'PCIe\s*(\d+\.\d+)', slots_description, re.IGNORECASE)
    return max(float(ver) for ver in matches) if matches else 0.0

def parse_power_phases(phases_str: str) -> int:
    """Преобразует строку фаз питания в число (например '7+1+1' -> 7)"""
    if not phases_str:
        return 0
    try:
        return int(phases_str.split('+')[0])
    except (ValueError, AttributeError):
        return 0

def find_compatible_motherboard(cpu_data: Dict[str, Any], gpu_data: Dict[str, Any]) -> Dict[str, Any]:
    socket = cpu_data.get("socket", "").strip()
    cpu_pcie_str = cpu_data.get("pci_express", "")
    required_cpu_pcie_version = extract_pcie_version(cpu_pcie_str)
    
    gpu_interface = gpu_data.get("interface", "")
    gpu_slot_width = gpu_data.get("slot_width", "")
    required_gpu_pcie_version = extract_pcie_version(gpu_interface)

    query = """
        SELECT * FROM pc_components.motherboard
        WHERE socket = %(socket)s
    """

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, {"socket": socket})
            results = cursor.fetchall()
            
            if not results:
                raise ValueError(f"Не найдено плат с сокетом '{socket}'")

            compatible = []
            for row in results:
                slots_info = row.get("pcie_x16_slots", "")
                
                # Проверяем совместимость с CPU
                max_pcie_version = extract_highest_pcie_version(slots_info)
                cpu_ok = max_pcie_version >= required_cpu_pcie_version
                
                # Проверяем совместимость с GPU
                gpu_ok = False
                if gpu_slot_width == "PCIe x16":
                    # Простая проверка наличия x16 в слотах
                    gpu_ok = "x16" in slots_info.lower()
                
                if cpu_ok and gpu_ok:
                    compatible.append(row)

            if not compatible:
                raise ValueError(
                    f"Нет плат с сокетом '{socket}', поддерживающих "
                    f"PCIe CPU ≥{required_cpu_pcie_version} и слот x16 для GPU"
                )

            # Выбираем плату с лучшими характеристиками
            best_match = max(
                compatible,
                key=lambda x: (
                    extract_highest_pcie_version(x.get("pcie_x16_slots", "")),
                    parse_power_phases(x.get("power_phases", "")),
                    -float(x.get("price", 0))
                )
            )
            
            motherboard = MotherboardModel.from_orm(best_match)
            return motherboard.model_dump()

def run_motherboard_selection_test(cpu_data: Dict[str, Any], gpu_data: Dict[str, Any]) -> None:
    try:
        motherboard_info = find_compatible_motherboard(cpu_data, gpu_data)
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
run_motherboard_selection_test(cpu_data=chosen_cpu, gpu_data=chosen_gpu)
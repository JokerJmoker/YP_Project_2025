from typing import Dict, Any, Optional
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
import logging

# Настройка логгера — обычно это делают один раз в основном файле приложения
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def find_compatible_motherboard(
    input_data_2nd_stage: dict,
    cpu_data: dict,
    gpu_data: dict,
    dimm_data: dict,
    ssd_m2_data: dict
) -> dict:
    print("===== ТЕСТИРОВАНИЕ ПОДБОРА МАТЕРИНСКОЙ ПЛАТЫ =====")

    user_request = input_data_2nd_stage["user_request"]
    method = user_request["allocations"]["mandatory"]["method"]
    logger.info(f"Метод выделения бюджета для материнской платы: {method}")

    if method == "fixed_price_based":
        max_price = user_request["allocations"]["mandatory"][method]["motherboard_max_price"]
        logger.info(f"Максимальная цена платы (фиксированная): {max_price}")
    elif method == "percentage_based":
        total_budget = user_request["budget"]["amount"]
        mb_percentage = user_request["allocations"]["mandatory"][method]["motherboard_percentage"]
        max_price = round((mb_percentage / 100) * total_budget)
        logger.info(f"Бюджет пользователя: {total_budget}, процент на материнскую плату: {mb_percentage}%, максимальная цена платы: {max_price}")
    else:
        logger.error(f"Неподдерживаемый метод выделения бюджета: {method}")
        raise ValueError(f"Unsupported allocation method: {method}")

    mb_preference = user_request["components"]["mandatory"]["motherboard"]
    logger.info(f"Предпочтения пользователя по материнской плате: {mb_preference}")

    if mb_preference != "any":
        logger.info(f"Ищем материнскую плату с названием, содержащим '{mb_preference}', по цене до {max_price}")
        with Database() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(
                    "SELECT * FROM pc_components.motherboard WHERE name ILIKE %s AND price <= %s",
                    (f"%{mb_preference}%", max_price)
                )
                result = cursor.fetchone()
                if result:
                    logger.info(f"Найдена материнская плата по предпочтению: {result['name']}")
                    return MotherboardModel.from_orm(result).model_dump()
                logger.info("Материнская плата по предпочтению не найдена, продолжаем поиск по совместимости")

    socket = cpu_data.get("socket", "").strip()
    required_cpu_pcie_version = extract_pcie_version(cpu_data.get("pci_express", ""))
    gpu_interface = gpu_data.get("interface", "")
    gpu_slot_width = gpu_data.get("slot_width", "")
    required_gpu_pcie_version = extract_pcie_version(gpu_interface)

    logger.info(f"Параметры CPU: сокет {socket}, требуемая версия PCIe: {required_cpu_pcie_version}")
    logger.info(f"Параметры GPU: интерфейс {gpu_interface}, слот {gpu_slot_width}")
    logger.info(f"Параметры памяти DIMM: тип {dimm_data['memory_type']}, количество модулей {dimm_data['modules_count']}, общий объем {dimm_data['total_memory']}, частота {dimm_data['frequency']}")

    query = """
        SELECT *, 
               pcie_version as pcie_version,
               nvme_pcie_version as nvme_pcie_version,
               m2_cpu_slots as m2_cpu_slots,
               m2_chipset_slots as m2_chipset_slots,
               pcie_x16_slots as pcie_x16_slots
        FROM pc_components.motherboard
        WHERE socket = %(socket)s
        AND memory_type = %(memory_type)s
        AND COALESCE(CAST(NULLIF(REGEXP_REPLACE(memory_slots, '[^0-9]', '', 'g'), '') AS INTEGER), 0) >= %(modules_count)s
        AND COALESCE(CAST(NULLIF(REGEXP_REPLACE(max_memory, '[^0-9]', '', 'g'), '') AS INTEGER), 0) >= %(total_memory)s
        AND price <= %(max_price)s
    """

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            logger.info(f"Поиск материнских плат с параметрами: сокет={socket}, тип памяти={dimm_data['memory_type']}, модули памяти>={dimm_data['modules_count']}, объем памяти>={extract_number(dimm_data['total_memory'])}, цена<={max_price}")
            cursor.execute(query, {
                "socket": socket,
                "memory_type": dimm_data["memory_type"],
                "modules_count": dimm_data["modules_count"],
                "total_memory": extract_number(dimm_data["total_memory"]),
                "max_price": max_price
            })
            results = cursor.fetchall()
            
            if not results:
                logger.error(f"Не найдено материнских плат с сокетом '{socket}', поддержкой памяти и в рамках бюджета")
                raise ValueError(f"No motherboards found with socket '{socket}', RAM support, and within budget")

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
                    ram_ok = dimm_data["frequency"] <= max_supported_freq

                ssd_m2_ok = check_ssd_m2_compatibility(ssd_m2_data, row)

                #logger.info(f"Материнская плата '{row['name']}' - CPU PCIe OK: {cpu_ok}, GPU PCIe OK: {gpu_ok}, RAM OK: {ram_ok}, SSD M.2 OK: {ssd_m2_ok}")

                if cpu_ok and gpu_ok and ram_ok and ssd_m2_ok:
                    compatible.append(row)

            if not compatible:
                logger.error("Не найдено полностью совместимых материнских плат с заданными компонентами и бюджетом")
                raise ValueError("No fully compatible motherboards found with the given components and budget")

            best_match = max(
                compatible,
                key=lambda x: (
                    extract_highest_pcie_version(x.get("pcie_x16_slots", "")),
                    parse_power_phases(x.get("power_phases", "")),
                    -float(x.get("price", 0))
                )
            )
            
            logger.info(f"Выбрана материнская плата {best_match['name']} стоимостью {best_match['price']}")
            logger.info("Подбор материнской платы завершён успешно")
            return MotherboardModel.from_orm(best_match).model_dump()

    
def run_motherboard_selection_test(
    input_data_2nd_stage: Dict[str, Any],
    cpu_data: Dict[str, Any], 
    gpu_data: Dict[str, Any],
    dimm_data: Dict[str, Any],
    ssd_m2_data: Dict[str, Any]
)  -> Optional[Dict[str, Any]]:
    try:
        motherboard_info = find_compatible_motherboard(input_data_2nd_stage, cpu_data, gpu_data, dimm_data, ssd_m2_data)
        print("\nНайдена совместимая материнская плата:")
        print(json.dumps(motherboard_info, indent=4, ensure_ascii=False))
        return motherboard_info
    except ValueError as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    input_data_2nd_stage = {
    "status": "success",
    "message": "Данные пользователя успешно разобраны.",
    "user_request": {
        "game": {
        "title": "cyberpunk_2077",
        "graphics": {
            "quality": "ultra",
            "target_fps": 60,
            "resolution": "2160",
            "ray_tracing": False,
            "dlss": "performance",
            "fsr": "disabled"
        }
        },
        "budget": {
        "amount": 200000,
        "allocation_method": "fixed_price_based"
        },
        "components": {
        "mandatory": {
            "cpu": "any",
            "gpu": "any",
            "dimm": "any",
            "ssd_m2": "any",
            "motherboard": "any",
            "power_supply": "any"
        },
        "optional": {
            "cooling": "any",
            "pc_case": "normal_size",
            "cpu_cooler": "included_with_cpu"
        }
        },
        "allocations": {
        "mandatory": {
            "method": "fixed_price_based",
            "fixed_price_based": {
            "cpu_max_price": 40000,
            "gpu_max_price": 120000,
            "dimm_max_price": 15000,
            "ssd_m2_max_price": 12000,
            "motherboard_max_price": 33000,
            "power_supply_max_price": 15000
            }
        },
        "optional": {
            "method": "fixed_price_based",
            "fixed_price_based": {
            "cooling_max_price": 10000,
            "pc_case_max_price": 8000,
            "cpu_cooler_max_price": 0
            }
        }
        }
    }
    }

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
    run_motherboard_selection_test(input_data_2nd_stage,cpu_data=chosen_cpu, gpu_data=chosen_gpu, dimm_data=chosen_dimm, ssd_m2_data=chosen_ssd_m2)
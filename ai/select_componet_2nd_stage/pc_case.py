from typing import Dict, Any, Union, List
from psycopg2.extras import DictCursor
import sys
import os
import json
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.pc_case import PcCaseModel
def select_pc_case(
    input_data_2nd_stage: Dict[str, Any],
    chosen_gpu: Dict[str, Any],
    chosen_cpu_cooler: Dict[str, Any],
    chosen_motherboard: Dict[str, Any],
    chosen_power_supply: Dict[str, Any],
    chosen_case_fan: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Подбирает корпус на основе:
    1. Бюджета (с постепенным снижением требований)
    2. Длины видеокарты
    3. Поддержки кулера (воздушного или водяного)
    4. Форм-фактора материнской платы
    5. Форм-фактора и длины блока питания
    6. Поддержки вентиляторов корпуса (±5 мм)
    """
    print("\n[DEBUG] ===== НАЧАЛО ПОДБОРА КОРПУСА =====")
    
    # 1. Рассчитываем максимальный бюджет
    user_request = input_data_2nd_stage["user_request"]
    if user_request["allocations"]["optional"]["method"] == "percentage_based":
        pc_case_percentage = user_request["allocations"]["optional"]["percentage_based"]["pc_case_percentage"]
        original_max_price = round((pc_case_percentage / 100) * user_request["budget"]["amount"])
    else:
        original_max_price = user_request["allocations"]["optional"]["fixed_price_based"]["pc_case_max_price"]
    
    print(f"[DEBUG] Исходный максимальный бюджет: {original_max_price} руб.")

    # 2. Получаем параметры компонентов
    gpu_length = chosen_gpu.get("length", 0)
    mb_form_factor = chosen_motherboard.get("form_factor", "")
    psu_form_factor = chosen_power_supply.get("form_factor", "ATX")
    psu_length = chosen_power_supply.get("length", 0)
    fan_size = chosen_case_fan.get("fan_size", 120)
    
    print(f"[DEBUG] Длина видеокарты: {gpu_length} мм")
    print(f"[DEBUG] Форм-фактор материнской платы: {mb_form_factor}")
    print(f"[DEBUG] Блок питания: {psu_form_factor}, длина={psu_length} мм")
    print(f"[DEBUG] Размер вентиляторов: {fan_size} мм")

    # 3. Обрабатываем тип охлаждения
    cooler_type = user_request["components"]["optional"]["cpu_cooler"]
    cpu_cooler_height = 0
    radiator_size = None
    found_case = None
    
    print(f"[DEBUG] Определён тип охлаждения: {cooler_type}")

    def parse_sizes(size_str: str) -> List[int]:
        """Парсит размеры из строки (120 мм, 140мм и т.д.)"""
        if not size_str:
            return []
        return list(set(int(size) for size in re.findall(r'(\d+)\s*мм', size_str)))

    def check_support(support_data: Union[str, List[int], int], target: int) -> bool:
        """Проверяет поддержку конкретного размера"""
        if not support_data:
            return False
        sizes = parse_sizes(support_data) if isinstance(support_data, str) else (
            [support_data] if isinstance(support_data, int) else support_data
        )
        return target in sizes

    # Пытаемся найти корпус с постепенным снижением требований
    for attempt in range(1, 4):
        current_max_price = original_max_price * (1.0 - 0.1 * (attempt - 1))  # Уменьшаем бюджет на 10% с каждой попыткой
        print(f"\n[DEBUG] Попытка #{attempt}: максимальная цена {current_max_price:.0f} руб.")
        
        if cooler_type == "water_cooling":
            print(f"[DEBUG] Выбрана СЖО: {chosen_cpu_cooler}")
            radiator_str = chosen_cpu_cooler.get("radiator_size", "")
            radiator_match = re.search(r'(\d+)\s*мм', radiator_str)
            if radiator_match:
                radiator_size = int(radiator_match.group(1))
                print(f"[DEBUG] Размер радиатора: {radiator_size} мм")
                
                query = """
                    SELECT id, name, price, max_gpu_length, liquid_cooling_support,
                    motherboard_form_factors, psu_form_factor, max_psu_length,
                    front_radiator_support, rear_radiator_support, top_radiator_support,
                    bottom_radiator_support, side_radiator_support,
                    front_fan_support, rear_fan_support, top_fan_support,
                    bottom_fan_support, side_fan_support
                    FROM pc_components.pc_case
                    WHERE price <= %s
                    AND CAST(SUBSTRING(max_gpu_length FROM '[0-9]+') AS INTEGER) >= %s
                    AND liquid_cooling_support = TRUE
                    AND (%s = ANY(string_to_array(REPLACE(REPLACE(motherboard_form_factors, ' ', ''), ',', ','), ',')))
                    AND (psu_form_factor = %s OR psu_form_factor LIKE '%%' || %s || '%%')
                    AND CAST(SUBSTRING(max_psu_length FROM '[0-9]+') AS INTEGER) >= %s
                    ORDER BY price DESC
                    LIMIT 1
                """
                
                try:
                    with Database() as conn:
                        with conn.cursor(cursor_factory=DictCursor) as cursor:
                            print(f"[DEBUG] Выполняем запрос для водяного охлаждения")
                            
                            cursor.execute(query, (
                                current_max_price, gpu_length, mb_form_factor, 
                                psu_form_factor, psu_form_factor, psu_length
                            ))
                            found_case = cursor.fetchone()
                            
                            if found_case:
                                print(f"[DEBUG] Найден корпус: {found_case['name']}")
                                break
                except Exception as e:
                    print(f"[ERROR] Ошибка SQL запроса: {e}")
                    continue

        elif cooler_type in ["air_cooler", "included_with_cpu"]:
            cpu_cooler_height = chosen_cpu_cooler.get("height", 80 if cooler_type == "included_with_cpu" else 0)
            print(f"[DEBUG] Высота кулера: {cpu_cooler_height} мм")
            
            query = """
                SELECT id, name, price, max_gpu_length, max_cpu_cooler_height, liquid_cooling_support,
                    motherboard_form_factors, psu_form_factor, max_psu_length,
                    front_fan_support, rear_fan_support, top_fan_support,
                    bottom_fan_support, side_fan_support
                FROM pc_components.pc_case
                WHERE price <= %s
                AND CAST(SUBSTRING(max_gpu_length FROM '[0-9]+') AS INTEGER) >= %s
                AND CAST(SUBSTRING(max_cpu_cooler_height FROM '[0-9]+') AS INTEGER) >= %s
                AND (%s = ANY(string_to_array(REPLACE(REPLACE(motherboard_form_factors, ' ', ''), ',', ','), ',')))
                AND (psu_form_factor = %s OR psu_form_factor LIKE '%%' || %s || '%%')
                AND CAST(SUBSTRING(max_psu_length FROM '[0-9]+') AS INTEGER) >= %s
                ORDER BY price DESC
                LIMIT 1
            """

            try:
                with Database() as conn:
                    with conn.cursor(cursor_factory=DictCursor) as cursor:
                        print(f"[DEBUG] Выполняем запрос для воздушного охлаждения")
                        
                        cursor.execute(query, (
                            current_max_price, 
                            gpu_length, 
                            cpu_cooler_height,
                            mb_form_factor, 
                            psu_form_factor, 
                            psu_form_factor, 
                            psu_length
                        ))
                        found_case = cursor.fetchone()
                        
                        if found_case:
                            print(f"[DEBUG] Найден корпус: {found_case['name']}")
                            break
            except Exception as e:
                print(f"[ERROR] Ошибка SQL запроса: {e}")
                continue

    if not found_case:
        raise ValueError("Не удалось найти подходящий корпус после нескольких попыток")

    # Формируем результат
    result = {
        "id": found_case["id"],
        "name": found_case["name"],
        "price": found_case["price"],
        "max_gpu_length": found_case["max_gpu_length"],
        "motherboard_form_factors": found_case["motherboard_form_factors"],
        "psu_form_factor": found_case["psu_form_factor"],
        "max_psu_length": found_case["max_psu_length"],
        "fan_support": {
            "size": fan_size,
            "positions": [pos for pos in ['front', 'rear', 'top', 'bottom', 'side'] 
                         if check_support(found_case.get(f"{pos}_fan_support"), fan_size)]
        }
    }

    if cooler_type == "water_cooling":
        result.update({
            "liquid_cooling_support": True,
            "radiator_size": radiator_size,
            "radiator_positions": [pos for pos in ['front', 'top', 'rear', 'bottom', 'side'] 
                                  if check_support(found_case.get(f"{pos}_radiator_support"), radiator_size)]
        })
    else:
        result["max_cpu_cooler_height"] = found_case.get("max_cpu_cooler_height", 0)

    print("\n[DEBUG] ===== РЕЗУЛЬТАТ =====")
    print(f"Корпус: {result['name']}")
    print(f"Цена: {result['price']} руб.")
    if cooler_type == "water_cooling":
        print(f"Поддержка радиатора: {result['radiator_size']}мм в позициях: {', '.join(result['radiator_positions'])}")
    else:
        print(f"Макс. высота кулера: {result['max_cpu_cooler_height']} мм")
    print(f"Поддержка вентиляторов: {fan_size}мм в позициях: {', '.join(result['fan_support']['positions'])}")
    
    return result

def run_pc_case_selection_test(
    input_data_2nd_stage: Dict[str, Any],
    chosen_gpu: Dict[str, Any],
    chosen_cpu_cooler: Dict[str, Any],
    chosen_motherboard: Dict[str, Any],
    chosen_power_supply: Dict[str, Any],
    chosen_case_fan: Dict[str, Any]
) -> None:
    """Тестовая функция для проверки подбора корпуса"""
    print("===== ТЕСТИРОВАНИЕ ПОДБОРА КОРПУСА =====")
    try:
        pc_case_info = select_pc_case(
            input_data_2nd_stage,
            chosen_gpu,
            chosen_cpu_cooler,
            chosen_motherboard,
            chosen_power_supply,
            chosen_case_fan
        )
        print("\nРезультат:")
        print(json.dumps(pc_case_info, indent=2, ensure_ascii=False))
    except ValueError as e:
        print(f"\nОшибка: {e}")

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
            "case_fan": "any",
            "pc_case": "any",
            "cpu_cooler": "water_cooling"
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
            "motherboard_max_price": 20000,
            "power_supply_max_price": 15000
            }
        },
        "optional": {
            "method": "fixed_price_based",
            "fixed_price_based": {
            "case_fan_max_price": 10000,
            "pc_case_max_price": 8000,
            "cpu_cooler_max_price": 0
            }
        }
        }
    }
    }
    chosen_gpu = {
        "id": 191,
        "name": "Видеокарта ASRock AMD Radeon RX 7700 XT Challenger OC [RX7700XT CL 12GO]",
        "price": 44999,
        "interface": "PCIe 4.0",
        "slot_width": "PCIe x16",
        "low_profile": False,
        "slots": "2.5",
        "length": 266,
        "width": 130,
        "thickness": 51,
        "tdp": None,
        "power_connectors": "2 x 8 pin",
        "recommended_psu": 750,
        "gpu_model": "Radeon RX 7700 XT",
        "architecture": "AMD RDNA 3",
        "vram_size": 12,
        "vram_type": "GDDR6",
        "bus_width": 192,
        "base_clock": 1900,
        "boost_clock": 2584,
        "cuda_cores": 3456,
        "ray_tracing": True,
        "tensor_cores": 0,
        "video_outputs": "3 x DisplayPort, HDMI",
        "max_resolution": "7680x4320 (8K Ultra HD)",
        "benchmark_rate": 55.64
    }
    chosen_cpu = {
        "id": 113,
        "name": "Процессор AMD Ryzen 5 7600X OEM",
        "price": 16799,
        "socket": "AM5",
        "tdp": 105,
        "base_tdp": 105,
        "cooler_included": True,
        "total_cores": 6,
        "performance_cores": 6,
        "efficiency_cores": 0,
        "max_threads": 12,
        "base_frequency": 4.7,
        "turbo_frequency": 5.3,
        "unlocked_multiplier": True,
        "memory_type": "DDR5",
        "max_memory": 128,
        "memory_channels": 2,
        "memory_frequency": 5200,
        "integrated_graphics": True,
        "gpu_model": "AMD Radeon Graphics",
        "pci_express": "PCIe 5.0",
        "pci_lanes": 24,
        "benchmark_rate": 17.67
    }

    chosen_cpu_cooler = {
        "id": 402,
        "name": "Кулер для процессора XASTRA AR620 DIGITAL BK [AR620-BKDFPX-GL]",
        "price": 40995349,
        "socket": "AM4, AM5, LGA 1150, LGA 1151, LGA 1151-v2, LGA 1155, LGA 1156, LGA 1200, LGA 1700, LGA 1851",
        "tdp": 260,
        "type_": "кулер для процессора",
        "fan_size": 120120,
        "fan_count": 2,
        "max_rpm": 1800,
        "min_rpm": 800,
        "max_noise_level": 31.6,
        "max_airflow": 73.5,
        "height": 159,
        "width": 126,
        "depth": 135
    }

    chosen_water_cooling = {
        "id": 240,
        "name": "Система охлаждения Valkyrie Jarn 420W Silver White",
        "price": 11999,
        "compatible_sockets": "AM4, AM5, LGA 1150, LGA 1151, LGA 1155, LGA 1156, LGA 1200, LGA 1700, LGA 2011, LGA 2011-v3",
        "fan_airflow": 105.0,
        "radiator_size": "140 мм - три секции",
        "fans_count": 3,
        "fan_max_noise": 32.2,
        "pump_speed": 2500,
        "fan_max_speed": 2500,
        "tube_length": None
    }

    chosen_ssd_m2 = {
        "id": 447,
        "name": "1000 ГБ M.2 NVMe накопитель Samsung 980 PRO [MZ-V8P1T0CW]",
        "price": 13899,
        "capacity": "1000",
        "form_factor": "2280",
        "interface": "PCIe 4.0 x4",
        "m2_key": "M",
        "nvme": True,
        "controller": "Samsung Elpis",
        "cell_type": "3 бит MLC (TLC)",
        "memory_structure": "3D NAND",
        "has_dram": True,
        "dram_size": "1024 МБ",
        "max_read_speed": 7000,
        "max_write_speed": 5000,
        "random_read_iops": 1000000,
        "random_write_iops": 1000000,
        "length": 80,
        "width": 24,
        "thickness": 86,
        "weight": 305,
        "heatsink_included": True
    }
    chosen_dimm = {
        "id": 743,
        "name": "Оперативная память Kingston Fury Renegade White RGB [KF580C38RWAK2-32] 32 ГБ",
        "price": 26599,
        "memory_type": "DDR5",
        "module_type": "UDIMM",
        "total_memory": 32,
        "modules_count": 2,
        "frequency": 8000,
        "ecc_memory": False,
        "registered_memory": False,
        "cas_latency": 38,
        "ras_to_cas_delay": 48,
        "row_precharge_delay": 48,
        "activate_to_precharge_delay": None,
        "voltage": 1.45,
        "intel_xmp": "7200 MHz (38-44-44), 7600 MHz (36-46-46), 8000 MHz (38-48-48)",
        "amd_expo": "нет",
        "height": 44,
        "low_profile": False
    }

    chosen_motherboard = {
        "id": 421,
        "name": "Материнская плата MSI PRO X870-P WIFI",
        "price": 22499,
        "socket": "AM5",
        "chipset": "",
        "power_phases": 1421,
        "form_factor": "Standard-ATX",
        "height": 305,
        "width": 244,
        "memory_type": "DDR5",
        "memory_slots": 4,
        "memory_channels": 2,
        "max_memory": 256,
        "base_memory_freq": 5600,
        "oc_memory_freq": [
            5800,
            6000,
            6200,
            6400,
            6600,
            6800,
            7000,
            7200,
            7400,
            7600,
            7800,
            8000
        ],
        "memory_form_factor": "DIMM",
        "pcie_version": 0.0,
        "pcie_x16_slots": 1,
        "sli_crossfire": False,
        "sli_crossfire_count": 0,
        "nvme_support": True,
        "nvme_pcie_version": 0.0,
        "m2_slots": 3,
        "sata_ports": 4,
        "sata_raid": False,
        "nvme_raid": False,
        "cpu_fan_headers": 14,
        "aio_pump_headers": 1,
        "case_fan_4pin": 6,
        "case_fan_3pin": 0,
        "main_power": "24 pin",
        "cpu_power": "2 x 8 pin"
    }

    chosen_power_supply = {
        "id": 878,
        "name": "Блок питания Thermaltake Toughpower GF A3 Snow 850W - TT Premium Edition [PS-TPD-0850FNFAGE-N] белый",
        "price": 15299,
        "wattage": 850,
        "form_factor": "ATX",
        "cable_management": "полностью модульный",
        "cable_sleeving": False,
        "main_connector": "24 pin",
        "cpu_connectors": "2 x 4+4 pin",
        "pcie_connectors": "5 x 6+2 pin, 16 pin (12VHPWR)",
        "sata_connectors": 8,
        "molex_connectors": 8,
        "floppy_connector": True,
        "cooling_type": "активная",
        "fan_size": 120120,
        "hybrid_mode": True,
        "certification_80plus": "Gold",
        "pfc_type": "активный",
        "length": 140,
        "width": 150,
        "height": 86,
        "weight": 2.89
    }

    chosen_case_fan = {
    "id": 909,
    "name": "Комплект вентиляторов LIAN LI UNI FAN TL 120 [G99.12TL3W.R0]",
    "price": 11999,
    "fan_size": 140,
    "fan_thickness": 28,
    "max_rotation_speed": 2600,
    "min_rotation_speed": 0,
    "max_airflow": 90.1,
    "max_static_pressure": 38.9,
    "max_noise_level": 33.0,
    "min_noise_level": 0.0,
    "power_connector_type": "4 pin, 7 pin (LIAN LI)"
    }
    run_pc_case_selection_test(input_data_2nd_stage, chosen_gpu, chosen_water_cooling, chosen_motherboard,
                               chosen_power_supply, chosen_case_fan)
from typing import Dict, Any
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
    chosen_power_supply: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Подбирает корпус на основе:
    1. Бюджета
    2. Длины видеокарты
    3. Высоты кулера процессора
    4. Форм-фактора материнской платы
    5. Форм-фактора и длины блока питания
    """
    print("\n[DEBUG] ===== НАЧАЛО ПОДБОРА КОРПУСА =====")
    
    # 1. Рассчитываем максимальный бюджет
    user_request = input_data_2nd_stage["user_request"]
    if user_request["allocations"]["optional"]["method"] == "percentage_based":
        pc_case_percentage = user_request["allocations"]["optional"]["percentage_based"]["pc_case_percentage"]
        max_price = round((pc_case_percentage / 100) * user_request["budget"]["amount"])
    else:
        max_price = user_request["allocations"]["optional"]["fixed_price_based"]["pc_case_max_price"]
    
    print(f"[DEBUG] Максимальный бюджет: {max_price} руб.")

    # 2. Получаем длину видеокарты
    gpu_length = chosen_gpu.get("length", 0)
    print(f"[DEBUG] Длина видеокарты: {gpu_length} мм")

    # 3. Получаем высоту кулера процессора
    cpu_cooler_height = chosen_cpu_cooler.get("height", 0)
    print(f"[DEBUG] Высота кулера процессора: {cpu_cooler_height} мм")

    # 4. Получаем форм-фактор материнской платы
    mb_form_factor = chosen_motherboard.get("form_factor", "")
    print(f"[DEBUG] Форм-фактор материнской платы: {mb_form_factor}")

    # 5. Получаем параметры блока питания
    psu_form_factor = chosen_power_supply.get("form_factor", "ATX")
    psu_length = chosen_power_supply.get("length", 0)
    print(f"[DEBUG] Блок питания: форм-фактор={psu_form_factor}, длина={psu_length} мм")

    # 6. Формируем и выполняем основной запрос
    query = """
        SELECT 
            id, name, price,
            max_gpu_length,
            max_cpu_cooler_height,
            motherboard_form_factors,
            psu_form_factor,
            max_psu_length,
            front_fan_support,
            rear_fan_support,
            top_fan_support,
            bottom_fan_support,
            side_fan_support,
            liquid_cooling_support,
            front_radiator_support,
            top_radiator_support,
            rear_radiator_support,
            bottom_radiator_support,
            side_radiator_support
        FROM pc_components.pc_case
        WHERE price <= %s
        AND (
            max_gpu_length ~ '[0-9]+' AND 
            CAST(SUBSTRING(max_gpu_length FROM '[0-9]+') AS INTEGER) >= %s
        )
        AND (
            max_cpu_cooler_height ~ '[0-9]+' AND 
            CAST(SUBSTRING(max_cpu_cooler_height FROM '[0-9]+') AS INTEGER) >= %s
        )
        AND (
            %s = ANY(string_to_array(REPLACE(REPLACE(motherboard_form_factors, ' ', ''), ',', ','), ','))
            OR
            motherboard_form_factors LIKE '%%' || %s || '%%'
        )
        AND (
            psu_form_factor = %s OR
            psu_form_factor LIKE '%%' || %s || '%%'
        )
        AND (
            max_psu_length ~ '[0-9]+' AND 
            CAST(SUBSTRING(max_psu_length FROM '[0-9]+') AS INTEGER) >= %s
        )
        ORDER BY 
            price DESC,
            CASE 
                WHEN %s = ANY(string_to_array(REPLACE(REPLACE(motherboard_form_factors, ' ', ''), ',', ','), ',')) THEN 0
                ELSE 1
            END,
            CAST(SUBSTRING(max_gpu_length FROM '[0-9]+') AS INTEGER) DESC,
            CAST(SUBSTRING(max_cpu_cooler_height FROM '[0-9]+') AS INTEGER) DESC,
            CAST(SUBSTRING(max_psu_length FROM '[0-9]+') AS INTEGER) DESC
        LIMIT 1
    """
    
    print(f"[DEBUG] Выполняем основной запрос с параметрами: "
          f"бюджет={max_price} руб., GPU={gpu_length} мм, "
          f"кулер={cpu_cooler_height} мм, MB={mb_form_factor}, "
          f"PSU={psu_form_factor}/{psu_length}мм")
    
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (
                max_price, 
                gpu_length, 
                cpu_cooler_height,
                mb_form_factor,
                mb_form_factor,
                psu_form_factor,
                psu_form_factor,
                psu_length,
                mb_form_factor
            ))
            result = cursor.fetchone()
            
            if not result:
                # 7. Fallback: если не найдено по основному запросу
                print("[DEBUG] Не найдено по основному запросу, пробуем fallback")
                fallback_query = """
                    SELECT 
                        id, name, price,
                        max_gpu_length,
                        max_cpu_cooler_height,
                        motherboard_form_factors,
                        psu_form_factor,
                        max_psu_length
                    FROM pc_components.pc_case
                    WHERE price <= %s
                    ORDER BY 
                        CASE 
                            WHEN %s = ANY(string_to_array(REPLACE(REPLACE(motherboard_form_factors, ' ', ''), ',', ','), ',')) THEN 0
                            ELSE 1
                        END,
                        CASE WHEN psu_form_factor = %s OR psu_form_factor LIKE '%%' || %s || '%%' THEN 0 ELSE 1 END,
                        CAST(SUBSTRING(max_psu_length FROM '[0-9]+') AS INTEGER) DESC,
                        CAST(SUBSTRING(max_cpu_cooler_height FROM '[0-9]+') AS INTEGER) DESC,
                        CAST(SUBSTRING(max_gpu_length FROM '[0-9]+') AS INTEGER) DESC,
                        price ASC
                    LIMIT 1
                """
                cursor.execute(fallback_query, (
                    max_price, 
                    mb_form_factor,
                    psu_form_factor,
                    psu_form_factor
                ))
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError("Не удалось найти подходящий корпус в рамках бюджета")
                
                print(f"[DEBUG] Найден fallback вариант: {result['name']}") 
            
            # 8. Валидация и преобразование данных через модель
            try:
                case_model = PcCaseModel.from_orm(result)
                actual_max_gpu_length = case_model.max_gpu_length or "0 мм"
                actual_max_cpu_cooler_height = case_model.max_cpu_cooler_height or "0 мм"
                actual_max_psu_length = case_model.max_psu_length or "0 мм"
                mb_support = case_model.motherboard_form_factors or ""
                psu_support = case_model.psu_form_factor or ""
                
                print("\n[DEBUG] ===== РЕЗУЛЬТАТ ПОДБОРА =====")
                print(f"Модель: {case_model.name}")
                print(f"Макс. длина GPU: {actual_max_gpu_length}")
                print(f"Макс. высота кулера: {actual_max_cpu_cooler_height}")
                print(f"Поддерживаемые форм-факторы: {mb_support}")
                print(f"Форм-фактор БП: {psu_support}")
                print(f"Макс. длина БП: {actual_max_psu_length}")
                print(f"Цена: {case_model.price} руб.")
                
                return case_model.model_dump()
            
            except Exception as e:
                raise ValueError(f"Ошибка обработки данных корпуса: {str(e)}")

def run_pc_case_selection_test(
    input_data_2nd_stage: Dict[str, Any],
    chosen_gpu: Dict[str, Any],
    chosen_cpu_cooler: Dict[str, Any],
    chosen_motherboard: Dict[str, Any],
    chosen_power_supply: Dict[str, Any]
) -> None:
    """Тестовая функция для проверки подбора корпуса"""
    print("===== ТЕСТИРОВАНИЕ ПОДБОРА КОРПУСА =====")
    try:
        pc_case_info = select_pc_case(
            input_data_2nd_stage,
            chosen_gpu,
            chosen_cpu_cooler,
            chosen_motherboard,
            chosen_power_supply
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
            "quality": "high",
            "target_fps": 240,
            "resolution": "1080",
            "ray_tracing": False,
            "dlss": "disabled",
            "fsr": "disabled"
        }
        },
        "budget": {
        "amount": 120000,
        "allocation_method": "percentage_based"
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
            "cpu_cooler": "air_cooler"
        }
        },
        "allocations": {
        "mandatory": {
            "method": "percentage_based",
            "percentage_based": {
            "cpu_percentage": 25,
            "gpu_percentage": 40,
            "dimm_percentage": 40,
            "ssd_m2_percentage": 15,
            "motherboard_percentage": 20,
            "power_supply_percentage": 15
            }
        },
        "optional": {
            "method": "percentage_based",
            "percentage_based": {
            "case_fan_percentage": 10,
            "pc_case_percentage": 10,
            "cpu_cooler_percentage": 10
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
    "fan_size": 124,
    "fan_thickness": 28,
    "max_rotation_speed": 2600,
    "min_rotation_speed": 0,
    "max_airflow": 90.1,
    "max_static_pressure": 38.9,
    "max_noise_level": 33.0,
    "min_noise_level": 0.0,
    "power_connector_type": "4 pin, 7 pin (LIAN LI)"
    }
    run_pc_case_selection_test(input_data_2nd_stage, chosen_gpu, chosen_cpu_cooler, chosen_motherboard,
                               chosen_power_supply)
from typing import Dict, Any
from psycopg2.extras import DictCursor
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.cpu import CpuModel
from ai.models.components.dimm import DimmModel


def get_cpu_model_by_name(cpu_name: str) -> CpuModel:
    query = "SELECT * FROM pc_components.cpu WHERE name = %s LIMIT 1"
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (cpu_name,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"CPU '{cpu_name}' not found in database")
            return CpuModel.from_orm(result)


def get_dimm_model_by_name(dimm_name: str) -> DimmModel:
    query = "SELECT * FROM pc_components.dimm WHERE name = %s LIMIT 1"
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (dimm_name,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"DIMM '{dimm_name}' not found in database")
            return DimmModel.from_orm(result)


from ai.models.components.cpu import CpuModel

def find_similar_dimm(
    input_data_1st_stage: Dict[str, Any],
    input_data_2nd_stage: Dict[str, Any],
    chosen_cpu: Dict[str, Any]  # ранее подобранный CPU, на основе которого выбираем DIMM
) -> Dict[str, Any]:
    user_request = input_data_2nd_stage["user_request"]
    method = user_request["allocations"]["mandatory"]["method"]

    if method == "fixed_price_based":
        max_price = user_request["allocations"]["mandatory"][method]["dimm_max_price"]
    elif method == "percentage_based":
        total_budget = user_request["budget"]["amount"]
        dimm_percentage = user_request["allocations"]["mandatory"][method]["dimm_percentage"]
        max_price = round((dimm_percentage / 100) * total_budget)
    else:
        raise ValueError(f"Unsupported allocation method: {method}")

    dimm_name_from_2nd = user_request["components"]["mandatory"]["dimm"]
    dimm_name = (
        input_data_1st_stage.get("dimm") if dimm_name_from_2nd == "any" else dimm_name_from_2nd
    )
    if not dimm_name:
        raise ValueError("DIMM name not specified")

    original_dimm = get_dimm_model_by_name(dimm_name)

    # Используем параметры из выбранного CPU
    cpu = CpuModel(**chosen_cpu)

    memory_types = [mt.strip() for mt in cpu.memory_type.split(",")]
    memory_types.reverse()  # предпочтение DDR5

    target_channels = cpu.memory_channels
    target_ecc = original_dimm.ecc_memory
    target_registered = original_dimm.registered_memory

    total_memory_value = original_dimm.total_memory
    target_total_memory = (
        int("".join(filter(str.isdigit, total_memory_value))) if isinstance(total_memory_value, str) else total_memory_value
    )

    target_freq = original_dimm.frequency
    min_freq = int(target_freq * 0.9)
    max_freq = int(target_freq * 1.1)

    query = """
        WITH parsed_dimm AS (
            SELECT *,
                NULLIF(REGEXP_REPLACE(frequency, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_frequency,
                NULLIF(REGEXP_REPLACE(modules_count, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_modules_count,
                NULLIF(REGEXP_REPLACE(total_memory, '[^0-9]', '', 'g'), '')::INTEGER AS parsed_total_memory
            FROM pc_components.dimm
        )
        SELECT * FROM parsed_dimm
        WHERE price <= %s
        AND memory_type = %s
        AND parsed_frequency BETWEEN %s AND %s
        AND parsed_modules_count = %s
        AND parsed_total_memory = %s
        AND ecc_memory = %s
        AND registered_memory = %s
        ORDER BY price DESC
        LIMIT 1
    """

    query_params_template = (
        max_price,
        None,  # memory_type
        min_freq,
        max_freq,
        target_channels,
        target_total_memory,
        target_ecc,
        target_registered
    )

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            for mem_type in memory_types:
                params = list(query_params_template)
                params[1] = mem_type
                cursor.execute(query, params)
                result = cursor.fetchone()
                if result:
                    similar_dimm = DimmModel.from_orm(result)
                    return similar_dimm.model_dump()

    raise ValueError(f"No similar DIMM found for memory types: {memory_types} within budget and compatibility criteria")

        
def run_dimm_selection_test(
    input_data_1st_stage: Dict[str, Any],
    input_data_2nd_stage: Dict[str, Any],
    chosen_cpu: Dict[str, Any]
) -> None:
    try:
        dimm_info = find_similar_dimm(input_data_1st_stage, input_data_2nd_stage, chosen_cpu)
        print(json.dumps(dimm_info, indent=4, ensure_ascii=False))
    except ValueError as e:
        print(f"Error: {e}")

# Пример вызова
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
                    "cpu": "Процессор Intel Core i7-14700K OEM",
                    "gpu": "any",
                    "dimm": "Оперативная память G.Skill Trident Z5 RGB [F5-7800J3646H16GX2-TZ5RK] 32 ГБ",
                    "ssd_m2": "any",
                    "motherboard": "any",
                    "power_supply": "any"
                },
                "optional": {
                    "cooling": "water_cooling",
                    "pc_case": "small_size",
                    "cpu_cooler": "any"
                }
            },
            "allocations": {
                "mandatory": {
                    "method": "percentage_based",
                    "percentage_based": {
                        "cpu_percentage": 25,
                        "gpu_percentage": 40,
                        "dimm_percentage": 20,
                        "ssd_percentage": 8,
                        "motherboard_percentage": 7,
                        "power_supply_percentage": 5
                    }
                },
                "optional": {
                    "method": "percentage_based",
                    "percentage_based": {
                        "cooling_percentage": 3,
                        "pc_case_percentage": 1,
                        "cpu_cooler_percentage": 1
                    }
                }
            }
        }
    }

    input_data_1st_stage = {
        "game": "cyberpunk_2077",
        "quality": "ultra",
        "cpu": "Процессор Intel Core i7-14700K OEM",
        "gpu": "Видеокарта GIGABYTE GeForce RTX 4080 SUPER GAMING OC [GV-N408SGAMING OC-16GD]",
        "ssd_m2": "2000 ГБ M.2 NVMe накопитель WD Black SN770 [WDS200T3X0E]",
        "dimm": "Оперативная память G.Skill Trident Z5 RGB [F5-7800J3646H16GX2-TZ5RK] 32 ГБ"
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

#run_dimm_selection_test(input_data_1st_stage, input_data_2nd_stage, chosen_cpu)
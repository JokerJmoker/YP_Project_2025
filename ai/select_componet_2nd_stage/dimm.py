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


def find_similar_dimm(input_data_1st_stage: Dict[str, Any], input_data_2nd_stage: Dict[str, Any]) -> Dict[str, Any]:
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
    if dimm_name_from_2nd == "any":
        dimm_name = input_data_1st_stage.get("dimm")
        if not dimm_name:
            raise ValueError("DIMM name not specified in input_data_1st_stage")
    else:
        dimm_name = dimm_name_from_2nd

    cpu_name = input_data_1st_stage.get("cpu") or user_request["components"]["mandatory"]["cpu"]
    if not cpu_name or cpu_name == "any":
        raise ValueError("CPU name must be specified to determine DIMM compatibility")

    cpu = get_cpu_model_by_name(cpu_name)
    original_dimm = get_dimm_model_by_name(dimm_name)

    # Совместимые параметры
    target_memory_type = cpu.memory_type
    target_memory_frequency = cpu.memory_frequency
    target_channels = cpu.memory_channels
    target_ecc = original_dimm.ecc if hasattr(original_dimm, "ecc") else False
    target_registered = original_dimm.registered if hasattr(original_dimm, "registered") else False

    # Основные параметры выбора: совместимость + параметры оригинала
    query = """
        SELECT * FROM pc_components.dimm
        WHERE price <= %s
          AND memory_type = %s
          AND frequency BETWEEN %s AND %s
          AND modules_count = %s
          AND ecc = %s
          AND registered = %s
        ORDER BY ABS(frequency - %s), price ASC
        LIMIT 1
    """

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (
                max_price,
                target_memory_type,
                original_dimm.frequency * 0.9,
                original_dimm.frequency * 1.1,
                target_channels,
                target_ecc,
                target_registered,
                original_dimm.frequency
            ))
            result = cursor.fetchone()
            if not result:
                raise ValueError("No similar DIMM found within budget and compatibility criteria")
            similar_dimm = DimmModel.from_orm(result)
            return similar_dimm.model_dump()


def run_dimm_selection_test(input_data_1st_stage: Dict[str, Any], input_data_2nd_stage: Dict[str, Any]) -> None:
    try:
        dimm_info = find_similar_dimm(input_data_1st_stage, input_data_2nd_stage)
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
                    "ssd": "any",
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
                        "dimm_percentage": 10,
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
        "ssd": "2000 ГБ M.2 NVMe накопитель WD Black SN770 [WDS200T3X0E]",
        "dimm": "Оперативная память G.Skill Trident Z5 RGB [F5-7800J3646H16GX2-TZ5RK] 32 ГБ"
    }

    run_dimm_selection_test(input_data_1st_stage, input_data_2nd_stage)

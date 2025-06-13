from typing import Dict, Any
from psycopg2.extras import DictCursor
import sys
import os
import json

# Добавляем корневой путь проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.ssd_m2 import SsdM2Model


# --- Функции для работы ---

def get_ssd_model_by_name(ssd_name: str) -> SsdM2Model:
    query = """
        SELECT * FROM pc_components.ssd_m2
        WHERE name = %s
        LIMIT 1
    """
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (ssd_name,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"SSD '{ssd_name}' not found in database")
            return SsdM2Model.from_orm(result)


def find_similar_ssd(input_data_1st_stage: Dict[str, Any], input_data_2nd_stage: Dict[str, Any]) -> Dict[str, Any]:
    user_request = input_data_2nd_stage["user_request"]
    method = user_request["allocations"]["mandatory"]["method"]

    if method == "fixed_price_based":
        max_price = user_request["allocations"]["mandatory"][method]["ssd_max_price"]
    elif method == "percentage_based":
        total_budget = user_request["budget"]["amount"]
        ssd_percentage = user_request["allocations"]["mandatory"][method]["ssd_percentage"]
        max_price = round((ssd_percentage / 100) * total_budget)
    else:
        raise ValueError(f"Unsupported allocation method: {method}")

    ssd_name_from_2nd = user_request["components"]["mandatory"]["ssd"]
    if ssd_name_from_2nd == "any":
        ssd_name = input_data_1st_stage.get("ssd")
        if not ssd_name:
            raise ValueError("SSD name not specified in input_data_1st_stage")
    else:
        ssd_name = ssd_name_from_2nd

    original_ssd = get_ssd_model_by_name(ssd_name)

    # Функция для извлечения числа
    def extract_number(value):
        if value is None:
            return 0
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                import re
                match = re.search(r'\d+', value)
                return int(match.group()) if match else 0
            except (ValueError, AttributeError):
                return 0
        return 0

    # Преобразуем параметры
    orig_read_speed = extract_number(original_ssd.max_read_speed)
    orig_write_speed = extract_number(original_ssd.max_write_speed)
    orig_read_iops = extract_number(original_ssd.random_read_iops)
    orig_write_iops = extract_number(original_ssd.random_write_iops)
    capacity_int = extract_number(original_ssd.capacity)

    # Основной запрос
    query = """
        SELECT * FROM pc_components.ssd_m2
        WHERE price <= %s
          AND nvme = %s
          AND has_dram = %s
        ORDER BY (
            ABS(COALESCE(CAST(NULLIF(REGEXP_REPLACE(max_read_speed, '[^0-9]', '', 'g'), '') AS INTEGER), 0) - %s) +
            ABS(COALESCE(CAST(NULLIF(REGEXP_REPLACE(max_write_speed, '[^0-9]', '', 'g'), '') AS INTEGER), 0) - %s) +
            ABS(COALESCE(CAST(NULLIF(REGEXP_REPLACE(random_read_iops, '[^0-9]', '', 'g'), '') AS INTEGER), 0) - %s) / 1000 +
            ABS(COALESCE(CAST(NULLIF(REGEXP_REPLACE(random_write_iops, '[^0-9]', '', 'g'), '') AS INTEGER), 0) - %s) / 1000 +
            ABS(COALESCE(CAST(NULLIF(REGEXP_REPLACE(capacity, '[^0-9]', '', 'g'), '') AS INTEGER), 0) - %s) * 10
        ), price DESC
        LIMIT 1
    """

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (
                max_price,
                original_ssd.nvme,
                original_ssd.has_dram,
                orig_read_speed,
                orig_write_speed,
                orig_read_iops,
                orig_write_iops,
                capacity_int
            ))
            
            result = cursor.fetchone()
            if result:
                return SsdM2Model.from_orm(result).model_dump()

    # Резервный запрос
    fallback_query = """
        SELECT * FROM pc_components.ssd_m2
        WHERE price <= %s
        ORDER BY (
            (CASE WHEN nvme = %s THEN 0 ELSE 100000 END) +
            (CASE WHEN has_dram = %s THEN 0 ELSE 50000 END) +
            ABS(COALESCE(CAST(NULLIF(REGEXP_REPLACE(max_read_speed, '[^0-9]', '', 'g'), '') AS INTEGER), 0) - %s) +
            ABS(COALESCE(CAST(NULLIF(REGEXP_REPLACE(max_write_speed, '[^0-9]', '', 'g'), '') AS INTEGER), 0) - %s) +
            ABS(COALESCE(CAST(NULLIF(REGEXP_REPLACE(random_read_iops, '[^0-9]', '', 'g'), '') AS INTEGER), 0) - %s) / 1000 +
            ABS(COALESCE(CAST(NULLIF(REGEXP_REPLACE(random_write_iops, '[^0-9]', '', 'g'), '') AS INTEGER), 0) - %s) / 1000 +
            ABS(COALESCE(CAST(NULLIF(REGEXP_REPLACE(capacity, '[^0-9]', '', 'g'), '') AS INTEGER), 0) - %s) * 10
        ), price DESC
        LIMIT 1
    """

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(fallback_query, (
                max_price,
                original_ssd.nvme,
                original_ssd.has_dram,
                orig_read_speed,
                orig_write_speed,
                orig_read_iops,
                orig_write_iops,
                capacity_int
            ))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError("No similar SSD found within budget and criteria")
            return SsdM2Model.from_orm(result).model_dump()  
        
def run_ssd_selection_test(input_data_1st_stage: Dict[str, Any], input_data_2nd_stage: Dict[str, Any]) -> None:
    try:
        ssd_info = find_similar_ssd(input_data_1st_stage, input_data_2nd_stage)
        print(json.dumps(ssd_info, indent=4, ensure_ascii=False))
    except ValueError as e:
        print(f"Error: {e}")


# --- Пример запуска ---

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
        "ssd": "2000 ГБ M.2 NVMe накопитель WD Black SN770 [WDS200T3X0E]",
        "dimm": "Оперативная память G.Skill Trident Z5 RGB [F5-7800J3646H16GX2-TZ5RK] 32 ГБ"
    }

    run_ssd_selection_test(input_data_1st_stage, input_data_2nd_stage)

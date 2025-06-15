from typing import Dict, Any, Optional
from psycopg2.extras import DictCursor
import sys
import os
import json

# Добавляем корневой путь проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.ssd_m2 import SsdM2Model


# --- Функции для работы ---

def get_ssd_m2_model_by_name(ssd_m2_name: str) -> SsdM2Model:
    query = """
        SELECT * FROM pc_components.ssd_m2
        WHERE name = %s
        LIMIT 1
    """
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (ssd_m2_name,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"ssd_m2 '{ssd_m2_name}' not found in database")
            return SsdM2Model.from_orm(result)


def find_similar_ssd_m2(input_data_1st_stage: Dict[str, Any], input_data_2nd_stage: Dict[str, Any]) -> Dict[str, Any]:
    user_request = input_data_2nd_stage["user_request"]
    method = user_request["allocations"]["mandatory"]["method"]

    if method == "fixed_price_based":
        max_price = user_request["allocations"]["mandatory"][method]["ssd_m2_max_price"]
    elif method == "percentage_based":
        total_budget = user_request["budget"]["amount"]
        ssd_m2_percentage = user_request["allocations"]["mandatory"][method]["ssd_m2_percentage"]
        max_price = round((ssd_m2_percentage / 100) * total_budget)
    else:
        raise ValueError(f"Unsupported allocation method: {method}")

    ssd_m2_name_from_2nd = user_request["components"]["mandatory"]["ssd_m2"]
    if ssd_m2_name_from_2nd == "any":
        ssd_m2_name = input_data_1st_stage.get("ssd_m2")
        if not ssd_m2_name:
            raise ValueError("ssd_m2 name not specified in input_data_1st_stage")
    else:
        ssd_m2_name = ssd_m2_name_from_2nd

    original_ssd_m2 = get_ssd_m2_model_by_name(ssd_m2_name)

    # Выбираем кандидатов из БД по цене <= max_price
    query = """
        SELECT * FROM pc_components.ssd_m2
        WHERE price <= %s
    """

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (max_price,))
            candidates_raw = cursor.fetchall()

    candidates = [SsdM2Model.from_orm(row) for row in candidates_raw]

    # Функция оценки "близости" ssd_m2 к оригинальному
    def ssd_m2_score(ssd_m2: SsdM2Model):
        score = 0
        # Чем меньше разница в скорости чтения/записи — тем лучше
        score += abs((ssd_m2.max_read_speed or 0) - (original_ssd_m2.max_read_speed or 0))
        score += abs((ssd_m2.max_write_speed or 0) - (original_ssd_m2.max_write_speed or 0))
        # Разница в IOPS
        score += abs((ssd_m2.random_read_iops or 0) - (original_ssd_m2.random_read_iops or 0)) / 1000
        score += abs((ssd_m2.random_write_iops or 0) - (original_ssd_m2.random_write_iops or 0)) / 1000
        # Разница в объеме (capacity в ГБ — строки, нужно перевести в int)
        try:
            capacity_int = int(ssd_m2.capacity) if ssd_m2.capacity else 0
            orig_capacity_int = int(original_ssd_m2.capacity) if original_ssd_m2.capacity else 0
            score += abs(capacity_int - orig_capacity_int) * 10
        except Exception:
            pass
        # Серьезный штраф, если NVMe не совпадает
        if ssd_m2.nvme != original_ssd_m2.nvme:
            score += 100000
        # Штраф, если DRAM не совпадает
        if ssd_m2.has_dram != original_ssd_m2.has_dram:
            score += 50000
        # Чем дешевле, тем лучше (отрицательное влияние цены для сортировки)
        score -= ssd_m2.price / 1000
        return score

    best_ssd_m2 = min(candidates, key=ssd_m2_score, default=None)
    if best_ssd_m2 is None:
        raise ValueError("No similar ssd_m2 found within budget and criteria")

    return best_ssd_m2.model_dump()


def run_ssd_m2_selection_test(input_data_1st_stage: Dict[str, Any], input_data_2nd_stage: Dict[str, Any])  -> Optional[Dict[str, Any]]:
    try:
        ssd_m2_info = find_similar_ssd_m2(input_data_1st_stage, input_data_2nd_stage)
        print(json.dumps(ssd_m2_info, indent=4, ensure_ascii=False))
        return ssd_m2_info
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
                        "ssd_m2_percentage": 8,
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

    run_ssd_m2_selection_test(input_data_1st_stage, input_data_2nd_stage)

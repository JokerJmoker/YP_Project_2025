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

import logging
import json
from typing import Optional, Dict, Any

def find_similar_ssd_m2(input_data_1st_stage: Dict[str, Any], input_data_2nd_stage: Dict[str, Any]) -> Dict[str, Any]:
    logging.info("Запуск поиска похожего SSD M.2")
    user_request = input_data_2nd_stage["user_request"]
    method = user_request["allocations"]["mandatory"]["method"]
    logging.info(f"Метод распределения бюджета: {method}")

    if method == "fixed_price_based":
        max_price = user_request["allocations"]["mandatory"][method]["ssd_m2_max_price"]
    elif method == "percentage_based":
        total_budget = user_request["budget"]["amount"]
        ssd_m2_percentage = user_request["allocations"]["mandatory"][method]["ssd_m2_percentage"]
        max_price = round((ssd_m2_percentage / 100) * total_budget)
    else:
        logging.error(f"Неподдерживаемый метод: {method}")
        raise ValueError(f"Unsupported allocation method: {method}")
    logging.info(f"Максимальная цена SSD M.2: {max_price}")

    ssd_m2_name_from_2nd = user_request["components"]["mandatory"]["ssd_m2"]
    if ssd_m2_name_from_2nd == "any":
        ssd_m2_name = input_data_1st_stage.get("ssd_m2")
        if not ssd_m2_name:
            logging.error("Не указано имя SSD M.2 ни в первом, ни во втором этапе")
            raise ValueError("ssd_m2 name not specified in input_data_1st_stage")
    else:
        ssd_m2_name = ssd_m2_name_from_2nd
    logging.info(f"Исходное имя SSD M.2: {ssd_m2_name}")

    original_ssd_m2 = get_ssd_m2_model_by_name(ssd_m2_name)
    logging.info(f"Получена модель оригинального SSD M.2: {original_ssd_m2.name}")

    query = """
        SELECT * FROM pc_components.ssd_m2
        WHERE price <= %s
    """

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (max_price,))
            candidates_raw = cursor.fetchall()
    logging.info(f"Найдено кандидатов по цене: {len(candidates_raw)}")

    candidates = [SsdM2Model.from_orm(row) for row in candidates_raw]

    def ssd_m2_score(ssd_m2: SsdM2Model):
        score = 0
        score += abs((ssd_m2.max_read_speed or 0) - (original_ssd_m2.max_read_speed or 0))
        score += abs((ssd_m2.max_write_speed or 0) - (original_ssd_m2.max_write_speed or 0))
        score += abs((ssd_m2.random_read_iops or 0) - (original_ssd_m2.random_read_iops or 0)) / 1000
        score += abs((ssd_m2.random_write_iops or 0) - (original_ssd_m2.random_write_iops or 0)) / 1000
        try:
            capacity_int = int(ssd_m2.capacity) if ssd_m2.capacity else 0
            orig_capacity_int = int(original_ssd_m2.capacity) if original_ssd_m2.capacity else 0
            score += abs(capacity_int - orig_capacity_int) * 10
        except Exception as e:
            logging.warning(f"Ошибка при вычислении capacity: {e}")
        if ssd_m2.nvme != original_ssd_m2.nvme:
            score += 100000
        if ssd_m2.has_dram != original_ssd_m2.has_dram:
            score += 50000
        score -= ssd_m2.price / 1000
        return score

    best_ssd_m2 = min(candidates, key=ssd_m2_score, default=None)
    if best_ssd_m2 is None:
        logging.error("Не найден подходящий SSD M.2 по заданным критериям")
        raise ValueError("No similar ssd_m2 found within budget and criteria")

    logging.info(f"Выбран SSD M.2: {best_ssd_m2.name} с ценой {best_ssd_m2.price}")
    return best_ssd_m2.model_dump()


def run_ssd_m2_selection_test(input_data_1st_stage: Dict[str, Any], input_data_2nd_stage: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    print("===== ТЕСТИРОВАНИЕ ПОДБОРА SSD M.2 =====")

    try:
        ssd_m2_info = find_similar_ssd_m2(input_data_1st_stage, input_data_2nd_stage)
        print("Результат подбора SSD M.2:")
        print(json.dumps(ssd_m2_info, indent=4, ensure_ascii=False))
        return ssd_m2_info
    except ValueError as e:
        logging.error(f"Ошибка подбора SSD M.2: {e}")
        print(f"[ОШИБКА] {e}")
        return None



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

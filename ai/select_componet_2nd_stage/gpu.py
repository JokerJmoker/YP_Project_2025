from typing import Dict, Any, Optional
from psycopg2.extras import DictCursor
import sys
import os
import json
import logging
# Добавляем корневой путь проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.gpu import GpuModel


def get_gpu_model_by_name(gpu_name: str) -> GpuModel:
    logging.info(f"Запрос GPU по имени: {gpu_name}")
    query = """
        SELECT * FROM pc_components.gpu 
        WHERE name = %s
        LIMIT 1
    """
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (gpu_name,))
            result = cursor.fetchone()
            if not result:
                logging.error(f"GPU '{gpu_name}' не найден в базе данных")
                raise ValueError(f"GPU '{gpu_name}' not found in database")
            logging.info(f"Найден GPU: {result['name']}")
            return GpuModel.from_orm(result)

def find_similar_gpu(input_data_1st_stage: Dict[str, Any], input_data_2nd_stage: Dict[str, Any]) -> Dict[str, Any]:
    logging.info("Начат поиск похожей видеокарты")
    user_request = input_data_2nd_stage["user_request"]
    method = user_request["allocations"]["mandatory"]["method"]
    logging.info(f"Используемый метод выделения бюджета: {method}")

    if method == "fixed_price_based":
        max_price = user_request["allocations"]["mandatory"][method]["gpu_max_price"]
        logging.info(f"Максимальная цена для GPU из fixed_price_based: {max_price}")
    elif method == "percentage_based":
        total_budget = user_request["budget"]["amount"]
        gpu_percentage = user_request["allocations"]["mandatory"][method]["gpu_percentage"]
        max_price = round((gpu_percentage / 100) * total_budget)
        logging.info(f"Максимальная цена для GPU из percentage_based: {max_price} (от бюджета {total_budget} и процента {gpu_percentage}%)")
    else:
        logging.error(f"Неизвестный метод выделения бюджета: {method}")
        raise ValueError(f"Unsupported allocation method: {method}")

    gpu_name_from_2nd = user_request["components"]["mandatory"]["gpu"]
    if gpu_name_from_2nd == "any":
        gpu_name = input_data_1st_stage.get("gpu")
        logging.info(f"GPU в 2-ой стадии = 'any', берем из 1-ой стадии: {gpu_name}")
        if not gpu_name:
            logging.error("Имя GPU не указано в input_data_1st_stage")
            raise ValueError("GPU name not specified in input_data_1st_stage")
    else:
        gpu_name = gpu_name_from_2nd
        logging.info(f"GPU указана явно: {gpu_name}")

    original_gpu = get_gpu_model_by_name(gpu_name)
    target_benchmark = original_gpu.benchmark_rate
    logging.info(f"Бенчмарк исходного GPU: {target_benchmark}")

    query = """
        SELECT * FROM pc_components.gpu 
        WHERE price <= %s
        ORDER BY ABS(benchmark_rate - %s), price DESC
        LIMIT 1
    """

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (max_price, target_benchmark))
            result = cursor.fetchone()
            if not result:
                logging.error("Не найдена похожая видеокарта в заданном бюджете")
                raise ValueError("No similar GPU found within budget and criteria")
            similar_gpu = GpuModel.from_orm(result)
            logging.info(f"Найдена похожая видеокарта: {similar_gpu.name}")
            return similar_gpu.model_dump()

def run_gpu_selection_test(input_data_1st_stage: Dict[str, Any], input_data_2nd_stage: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    print("\n===== ТЕСТИРОВАНИЕ ПОДБОРА ВИДЕОКАРТЫ =====")
    try:
        gpu_info = find_similar_gpu(input_data_1st_stage, input_data_2nd_stage)
        print("\nРезультат подбора видеокарты:")
        print(json.dumps(gpu_info, indent=4, ensure_ascii=False))
        return gpu_info
    except ValueError as e:
        print(f"\n[ОШИБКА] {e}")
        return None


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
                    "cpu": "any",
                    "gpu": "any",
                    "dimm": "any",
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
        "ssd_m2": "2000 ГБ M.2 NVMe накопитель WD Black SN770 [WDS200T3X0E]",
        "dimm": "Оперативная память G.Skill Trident Z5 RGB [F5-7800J3646H16GX2-TZ5RK] 32 ГБ"
    }

    run_gpu_selection_test(input_data_1st_stage, input_data_2nd_stage)

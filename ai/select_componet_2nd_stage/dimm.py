from typing import Dict, Any, Optional
from psycopg2.extras import DictCursor
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.cpu import CpuModel
from ai.models.components.dimm import DimmModel


import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S"
)

def get_cpu_model_by_name(cpu_name: str) -> CpuModel:
    logger.info(f"Запрос CPU по имени: {cpu_name}")
    query = "SELECT * FROM pc_components.cpu WHERE name = %s LIMIT 1"
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (cpu_name,))
            result = cursor.fetchone()
            if not result:
                logger.error(f"CPU '{cpu_name}' не найден в базе")
                raise ValueError(f"CPU '{cpu_name}' not found in database")
            logger.info(f"Найден CPU: {result['name']}")
            return CpuModel.from_orm(result)


def get_dimm_model_by_name(dimm_name: str) -> DimmModel:
    logger.info(f"Запрос DIMM по имени: {dimm_name}")
    query = "SELECT * FROM pc_components.dimm WHERE name = %s LIMIT 1"
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (dimm_name,))
            result = cursor.fetchone()
            if not result:
                logger.error(f"DIMM '{dimm_name}' не найден в базе")
                raise ValueError(f"DIMM '{dimm_name}' not found in database")
            logger.info(f"Найден DIMM: {result['name']}")
            return DimmModel.from_orm(result)


def find_similar_dimm(
    input_data_1st_stage: Dict[str, Any],
    input_data_2nd_stage: Dict[str, Any],
    chosen_cpu: Dict[str, Any]
) -> Dict[str, Any]:
    logger.info("Начинаем подбор похожего DIMM")
    user_request = input_data_2nd_stage["user_request"]
    method = user_request["allocations"]["mandatory"]["method"]
    logger.info(f"Метод выделения бюджета для DIMM: {method}")

    if method == "fixed_price_based":
        max_price = user_request["allocations"]["mandatory"][method]["dimm_max_price"]
        logger.info(f"Максимальная цена DIMM: {max_price}")
    elif method == "percentage_based":
        total_budget = user_request["budget"]["amount"]
        dimm_percentage = user_request["allocations"]["mandatory"][method]["dimm_percentage"]
        max_price = round((dimm_percentage / 100) * total_budget)
        logger.info(f"Процент бюджета для DIMM: {dimm_percentage}%, максимальная цена: {max_price}")
    else:
        logger.error(f"Неподдерживаемый метод выделения бюджета: {method}")
        raise ValueError(f"Unsupported allocation method: {method}")

    dimm_name_from_2nd = user_request["components"]["mandatory"]["dimm"]
    dimm_name = (
        input_data_1st_stage.get("dimm") if dimm_name_from_2nd == "any" else dimm_name_from_2nd
    )
    logger.info(f"Исходное имя DIMM: {dimm_name}")
    if not dimm_name:
        logger.error("Имя DIMM не указано")
        raise ValueError("DIMM name not specified")

    original_dimm = get_dimm_model_by_name(dimm_name)

    cpu = CpuModel(**chosen_cpu)
    memory_types = [mt.strip() for mt in cpu.memory_type.split(",")]
    memory_types.reverse()  # предпочтение DDR5
    logger.info(f"Поддерживаемые типы памяти CPU (с приоритетом DDR5): {memory_types}")

    target_channels = cpu.memory_channels
    target_ecc = original_dimm.ecc_memory
    target_registered = original_dimm.registered_memory

    total_memory_value = original_dimm.total_memory
    if isinstance(total_memory_value, str):
        target_total_memory = int("".join(filter(str.isdigit, total_memory_value)))
    else:
        target_total_memory = total_memory_value
    logger.info(f"Параметры DIMM для поиска - каналы: {target_channels}, ECC: {target_ecc}, зарегистрированная память: {target_registered}, общий объем: {target_total_memory}")

    target_freq = original_dimm.frequency
    min_freq = int(target_freq * 0.9)
    max_freq = int(target_freq * 1.1)
    logger.info(f"Диапазон частоты памяти для поиска: {min_freq} - {max_freq}")

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
                logger.info(f"Выполняем запрос с memory_type={mem_type}, params={params}")
                cursor.execute(query, params)
                result = cursor.fetchone()
                if result:
                    logger.info(f"Найден подходящий DIMM: {result['name']} по цене {result['price']}")
                    similar_dimm = DimmModel.from_orm(result)
                    return similar_dimm.model_dump()

    logger.error(f"Подходящий DIMM не найден для типов памяти: {memory_types} в рамках бюджета и критериев совместимости")
    raise ValueError(f"No similar DIMM found for memory types: {memory_types} within budget and compatibility criteria")


def run_dimm_selection_test(
    input_data_1st_stage: Dict[str, Any],
    input_data_2nd_stage: Dict[str, Any],
    chosen_cpu: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    print("===== ТЕСТИРОВАНИЕ ПОДБОРА DIMM =====")
    try:
        dimm_info = find_similar_dimm(input_data_1st_stage, input_data_2nd_stage, chosen_cpu)
        print("\nРезультат подбора DIMM")
        print(json.dumps(dimm_info, indent=4, ensure_ascii=False))
        return dimm_info
    except ValueError as e:
        logger.error(f"Ошибка при подборе DIMM: {e}")
        print(f"Error: {e}")
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
    run_dimm_selection_test(input_data_1st_stage, input_data_2nd_stage, chosen_cpu)
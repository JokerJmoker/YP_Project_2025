from typing import Dict, Any, Optional
from psycopg2.extras import DictCursor
import sys
import os
import json
import logging
import re
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Добавляем корневой путь проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.cpu_cooler import CpuCoolerModel


def find_compatible_cpu_cooler(
    input_data: Dict[str, Any],
    chosen_cpu: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Находит совместимый кулер для процессора с учетом:
    - Явного указания "cpu_cooler": "false" в запросе
    - Наличия BOX-версии процессора (включенного кулера)
    - Сокета и TDP процессора
    - Бюджета (сортировка по близости к заданной цене)
    """
    # Проверка необходимости подбора кулера
    if input_data["user_request"]["components"]["optional"].get("cpu_cooler", "any") == "false":
        return None
    
    # Проверка BOX-версии процессора
    if "box" in chosen_cpu.get("name", "").lower() and chosen_cpu.get("included_with_cpu", False):
        return None

    # Основные параметры процессора
    cpu_socket = chosen_cpu.get("socket")
    cpu_tdp = chosen_cpu.get("tdp")
    
    if not cpu_socket or not cpu_tdp:
        raise ValueError("Не указаны сокет или TDP процессора")
    if chosen_cpu.get("included_with_cpu", False):
        return None

    # Получение бюджета
    try:
        budget_data = input_data["user_request"]["allocations"]["optional"]["fixed_price_based"]
        target_price = budget_data.get("cpu_cooler_target_price")
        max_price = budget_data.get("cpu_cooler_max_price")
        target_price = target_price if target_price is not None else max_price
    except Exception:
        target_price = None
        max_price = None

    # Формирование SQL запроса
    query = """
        SELECT 
            id, name, price, socket, tdp, type, fan_size, fan_count,
            max_rpm, min_rpm, max_noise_level, max_airflow, height, width, depth
        FROM pc_components.cpu_cooler
        WHERE CAST(NULLIF(REGEXP_REPLACE(tdp, '[^0-9]', '', 'g'), '') AS INTEGER) >= %s
          AND %s = ANY (string_to_array(socket, ', '))
          {price_filter}
        ORDER BY 
            ABS(price - %s) ASC,
            CAST(NULLIF(REGEXP_REPLACE(tdp, '[^0-9]', '', 'g'), '') AS INTEGER) DESC,
            price ASC
        LIMIT 1
    """

    params = [cpu_tdp, cpu_socket, target_price if target_price is not None else 0]
    price_filter = "AND (price IS NULL OR price <= %s)" if max_price is not None else ""
    
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                # Основной запрос
                cursor.execute(query.format(price_filter=price_filter), 
                             tuple(params + ([max_price] if max_price is not None else [])))
                result = cursor.fetchone()

                if not result:
                    # Запасной запрос без учета TDP
                    cursor.execute(f"""
                        SELECT * FROM pc_components.cpu_cooler
                        WHERE %s = ANY (string_to_array(socket, ', '))
                        {price_filter}
                        ORDER BY ABS(price - %s) ASC, price ASC
                        LIMIT 1
                    """.format(price_filter=price_filter), 
                    (cpu_socket, target_price if target_price is not None else 0) + 
                    ((max_price,) if max_price is not None else ()))
                    
                    result = cursor.fetchone()
                    if not result:
                        raise ValueError("Не найдено подходящих кулеров")

                return CpuCoolerModel.from_orm(dict(result)).model_dump()

            except Exception as e:
                raise ValueError(f"Ошибка при поиске кулера: {str(e)}")

def run_cpu_cooler_selection_test(input_data: Dict[str, Any], chosen_cpu: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    logging.info("=== Тест подбора кулера ===")
    try:
        cooler_info = find_compatible_cpu_cooler(input_data, chosen_cpu)
        print(json.dumps(cooler_info, indent=4, ensure_ascii=False))
        return cooler_info
    except ValueError as e:
        logging.error("Ошибка подбора кулера: %s", e)
        return None
    except Exception as e:
        logging.exception("Неожиданная ошибка")
        return None


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
                    "cpu_cooler": "true"
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
                        "cpu_cooler_max_price": 9000
                    }
                }
            }
        }
    }

    chosen_cpu = {
        "id": 176,
        "name": "Процессор Intel Core i7-14700KF OEM",
        "price": 34999,
        "socket": "LGA 1700",
        "tdp": 253,
        "base_tdp": 125,
        "included_with_cpu": False,
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

    run_cpu_cooler_selection_test(input_data_2nd_stage, chosen_cpu)

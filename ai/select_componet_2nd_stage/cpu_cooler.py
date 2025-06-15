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


from typing import Dict, Any, Optional
from psycopg2.extras import DictCursor
import sys
import os
import json
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.cpu_cooler import CpuCoolerModel
from ai.models.components.water_cooling import WaterCoolingModel


def get_required_fan_airflow(tdp: int) -> float:
    if tdp <= 50:
        return 25.5
    elif tdp <= 100:
        return 38.25
    elif tdp <= 150:
        return 51.0
    elif tdp <= 200:
        return 63.75
    elif tdp <= 250:
        return 76.5
    else:
        return 89.25

from typing import Dict, Any, Optional
from psycopg2.extras import DictCursor
import sys
import os
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
from ai.models.components.water_cooling import WaterCoolingModel


def get_required_fan_airflow(tdp: int) -> float:
    if tdp <= 50:
        return 25.5
    elif tdp <= 100:
        return 38.25
    elif tdp <= 150:
        return 51.0
    elif tdp <= 200:
        return 63.75
    elif tdp <= 250:
        return 76.5
    else:
        return 89.25


def find_compatible_cpu_cooler(
    input_data: Dict[str, Any],
    chosen_cpu: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    cooler_type = input_data["user_request"]["components"]["optional"].get("cpu_cooler", "any")
    logging.info(f"Выбран тип кулера: {cooler_type}")

    if cooler_type == "false":
        logging.info("Кулер явно не требуется (false). Возврат None.")
        return None

    # Проверяем, нужно ли возвращать стандартный кулер (включен в комплект или box в названии)
    is_box_cpu = "box" in chosen_cpu.get("name", "").lower()
    has_included_cooler = chosen_cpu.get("included_with_cpu", False)
    
    if cooler_type == "included_with_cpu" or (is_box_cpu and has_included_cooler):
        logging.info("Возврат стандартного коробочного кулера (included_with_cpu или box в названии)")
        return {
            "name": "Stock CPU Cooler (Included with CPU)",
            "type": "air_cooler",
            "price": 0,
            "image_url": "https://c.dns-shop.ru/thumb/st1/fit/500/500/0037a3b9f4278404a0fccd74d4e790ad/4444db819930e984aa9e661d33a9c0714109e3da84d606173805182a22b223ac.jpg",
            "socket": chosen_cpu.get("socket", ""),
            "height": 70,  # Примерная высота стандартного кулера
            "tdp": chosen_cpu.get("tdp", 65),  # Примерное значение TDP
            "noise_level": "30-40 dB",  # Примерный уровень шума
            "material": "Aluminum + Plastic",
            "features": "Basic stock cooler included with CPU"
        }

    cpu_socket = chosen_cpu.get("socket")
    cpu_tdp = chosen_cpu.get("tdp")
    if not cpu_socket or not cpu_tdp:
        logging.error("Не указаны сокет или TDP процессора")
        raise ValueError("Не указаны сокет или TDP процессора")

    try:
        budget_data = input_data["user_request"]["allocations"]["optional"]["fixed_price_based"]
        target_price = budget_data.get("cpu_cooler_target_price")
        max_price = budget_data.get("cpu_cooler_max_price")
        target_price = target_price if target_price is not None else max_price
        logging.info(f"Целевая цена кулера: {target_price}, Максимальная цена: {max_price}")
    except Exception:
        target_price = None
        max_price = None
        logging.warning("Не удалось получить бюджет на кулер, цены не заданы")

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            try:
                if cooler_type == "air_cooler":
                    price_filter = "AND price <= %s" if target_price is not None else ""
                    query = """
                        SELECT * FROM pc_components.cpu_cooler
                        WHERE %s = ANY (string_to_array(socket, ', '))
                        {}
                        ORDER BY price DESC, ABS(price - %s) ASC
                        LIMIT 1
                    """.format(price_filter)
                    params = [cpu_socket]
                    if target_price is not None:
                        params.append(target_price)
                    params.append(target_price if target_price is not None else 0)

                    logging.info(f"Выполнение запроса для воздушного кулера с параметрами: {params}")
                    cursor.execute(query, tuple(params))
                    result = cursor.fetchone()

                    if not result:
                        logging.error("Не найдено подходящих воздушных кулеров")
                        raise ValueError("Не найдено подходящих воздушных кулеров")

                    logging.info(f"Найден воздушный кулер: {result['name']}")
                    return CpuCoolerModel.from_orm(dict(result)).model_dump()

                elif cooler_type == "water_cooling":
                    required_fan_airflow = get_required_fan_airflow(cpu_tdp)
                    price_filter = "AND price <= %s" if target_price is not None else ""
                    query = """
                        SELECT 
                            id, name, price, image_url, compatible_sockets, fan_airflow, radiator_size, fans_count,
                            fan_max_noise, pump_speed, fan_max_speed, tube_length
                        FROM pc_components.water_cooling
                        WHERE 
                            REGEXP_REPLACE(fan_airflow, '[^0-9.]', '', 'g') <> ''
                            AND CAST(REGEXP_REPLACE(fan_airflow, '[^0-9.]', '', 'g') AS FLOAT) >= %s
                            AND %s = ANY (string_to_array(compatible_sockets, ', '))
                            {}
                        ORDER BY 
                            price DESC,
                            CAST(REGEXP_REPLACE(fan_airflow, '[^0-9.]', '', 'g') AS FLOAT) DESC
                        LIMIT 1
                    """.format(price_filter)
                    params = [required_fan_airflow, cpu_socket]
                    if target_price is not None:
                        params.append(target_price)

                    logging.info(f"Выполнение запроса для водяного кулера с параметрами: {params}")
                    cursor.execute(query, tuple(params))
                    result = cursor.fetchone()

                    if not result:
                        logging.error("Не найдено подходящих водяных кулеров")
                        raise ValueError("Не найдено подходящих водяных кулеров")

                    logging.info(f"Найден водяной кулер: {result['name']}")
                    return WaterCoolingModel.from_orm(dict(result)).model_dump()

                else:
                    logging.error(f"Неизвестный тип кулера: {cooler_type}")
                    raise ValueError(f"Неизвестный тип кулера: {cooler_type}")

            except Exception as e:
                logging.error(f"Ошибка при поиске кулера: {str(e)}")
                raise ValueError(f"Ошибка при поиске кулера: {str(e)}")


def run_cpu_cooler_selection_test(
    input_data: Dict[str, Any], 
    chosen_cpu: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Тест подбора кулера CPU, просто возвращает результат find_compatible_cpu_cooler"""
    logging.info("=== Тест подбора кулера ===")
    try:
        cooler_info = find_compatible_cpu_cooler(input_data, chosen_cpu)
        if cooler_info is not None:
            print(json.dumps(cooler_info, indent=4, ensure_ascii=False))
        return cooler_info
    except Exception:
        logging.exception("Ошибка подбора кулера")
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
                        "motherboard_max_price": 33000,
                        "power_supply_max_price": 15000
                    }
                },
                "optional": {
                    "method": "fixed_price_based",
                    "fixed_price_based": {
                        "cooling_max_price": 10000,
                        "pc_case_max_price": 8000,
                        "cpu_cooler_max_price": 12000
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

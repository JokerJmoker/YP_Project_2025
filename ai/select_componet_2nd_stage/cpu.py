from typing import Dict, Any, Optional
from psycopg2.extras import DictCursor
import sys
import os
import json
import logging
# Добавляем корневой путь проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.cpu import CpuModel


def get_cpu_model_by_name(cpu_name: str) -> CpuModel:
    query = """
        SELECT * FROM pc_components.cpu 
        WHERE name = %s
        LIMIT 1
    """
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (cpu_name,))
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"CPU '{cpu_name}' not found in database")
            return CpuModel.from_orm(result)

import logging

def find_similar_cpu(
    input_data_1st_stage: Dict[str, Any], 
    input_data_2nd_stage: Dict[str, Any], 
    gpu_data: Dict[str, Any]
) -> Dict[str, Any]:
    logging.info("=== Начало поиска похожего CPU ===")

    user_request = input_data_2nd_stage["user_request"]
    method = user_request["allocations"]["mandatory"]["method"]
    logging.info(f"Метод распределения бюджета: {method}")

    if method == "fixed_price_based":
        max_price = user_request["allocations"]["mandatory"][method]["cpu_max_price"]
        logging.info(f"Максимальная цена CPU из fixed_price_based: {max_price}")
    elif method == "percentage_based":
        total_budget = user_request["budget"]["amount"]
        cpu_percentage = user_request["allocations"]["mandatory"][method]["cpu_percentage"]
        max_price = round((cpu_percentage / 100) * total_budget)
        logging.info(f"Максимальная цена CPU из percentage_based: {max_price} (от бюджета {total_budget} и процента {cpu_percentage}%)")
    else:
        logging.error(f"Неподдерживаемый метод распределения: {method}")
        raise ValueError(f"Unsupported allocation method: {method}")

    included_with_cpu = user_request["components"]["optional"].get("cpu_cooler") == "included_with_cpu"
    logging.info(f"Использование коробочного кулера включено: {included_with_cpu}")

    cpu_name_from_2nd = user_request["components"]["mandatory"]["cpu"]
    if cpu_name_from_2nd == "any":
        cpu_name = input_data_1st_stage.get("cpu")
        if not cpu_name:
            logging.error("CPU не указан ни в первом, ни во втором этапе данных")
            raise ValueError("CPU name not specified in input_data_1st_stage")
        logging.info(f"CPU выбран из первого этапа: {cpu_name}")
    else:
        cpu_name = cpu_name_from_2nd
        logging.info(f"CPU выбран из второго этапа: {cpu_name}")

    original_cpu = get_cpu_model_by_name(cpu_name)
    logging.info(f"Исходный CPU: {original_cpu.name}, Benchmark: {original_cpu.benchmark_rate}")

    target_benchmark = original_cpu.benchmark_rate
    suffix = "BOX" if included_with_cpu else "OEM"
    logging.info(f"Ищем CPU с суффиксом '{suffix}'")

    gpu_pcie_version = gpu_data.get("interface")
    if not gpu_pcie_version:
        logging.error("Не указана версия PCIe у GPU")
        raise ValueError("GPU PCIe interface version not specified")
    logging.info(f"Версия PCIe GPU: {gpu_pcie_version}")

    query = """
        SELECT * FROM pc_components.cpu
        WHERE price <= %s
          AND name ILIKE %s
          AND pci_express >= %s
        ORDER BY ABS(benchmark_rate - %s), price DESC
        LIMIT 1
    """

    logging.info("Выполняется запрос к БД для поиска похожего CPU...")
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (max_price, f"%{suffix}%", gpu_pcie_version, target_benchmark))
            result = cursor.fetchone()

            if not result:
                logging.error("Не найден подходящий CPU по критериям бюджета, суффикса и PCIe версии")
                raise ValueError("No similar CPU found within budget, criteria and PCIe version")

            similar_cpu = CpuModel.from_orm(result)
            logging.info(f"Найден похожий CPU: {similar_cpu.name}, цена: {similar_cpu.price}, benchmark: {similar_cpu.benchmark_rate}")

            return similar_cpu.model_dump()


import logging
import json
from typing import Dict, Any, Optional

def run_cpu_selection_test(
    input_data_1st_stage: Dict[str, Any], 
    input_data_2nd_stage: Dict[str, Any], 
    gpu_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    # Настройка логирования, чтобы видеть логи из find_similar_cpu в консоли
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S"
    )

    print("\n===== ТЕСТИРОВАНИЕ ПОДБОРА ПРОЦЕССОРА =====")
    try:
        cpu_info = find_similar_cpu(input_data_1st_stage, input_data_2nd_stage, gpu_data)
        print("\nРезультат подбора процессора:")
        print(json.dumps(cpu_info, indent=4, ensure_ascii=False))
        return cpu_info  
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
    "tdp": 12,
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
    run_cpu_selection_test(input_data_1st_stage, input_data_2nd_stage, chosen_gpu)

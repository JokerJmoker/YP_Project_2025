from typing import Dict, Any
from psycopg2.extras import DictCursor
import sys
import os
import json
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

def find_similar_cpu(input_data_2nd_stage: Dict[str, Any], input_data_1st_stage: Dict[str, Any]) -> Dict[str, Any]:
    user_request = input_data_2nd_stage["user_request"]
    method = user_request["allocations"]["mandatory"]["method"]
    max_price = user_request["allocations"]["mandatory"][method]["cpu_max_price"]
    included_with_cpu = user_request["components"]["optional"].get("cpu_cooler") == "included_with_cpu"

    cpu_name_from_2nd = user_request["components"]["mandatory"]["cpu"]
    if cpu_name_from_2nd == "any":
        cpu_name = input_data_1st_stage.get("cpu")
        if not cpu_name:
            raise ValueError("CPU name not specified in input_data_1st_stage")
    else:
        cpu_name = cpu_name_from_2nd

    original_cpu = get_cpu_model_by_name(cpu_name)
    target_benchmark = original_cpu.benchmark_rate

    suffix = "BOX" if included_with_cpu else "OEM"

    query = """
        SELECT * FROM pc_components.cpu 
        WHERE price <= %s AND name ILIKE %s
        ORDER BY ABS(benchmark_rate - %s), price ASC
        LIMIT 1
    """

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (max_price, f"%{suffix}%", target_benchmark))
            result = cursor.fetchone()
            if not result:
                raise ValueError("No similar CPU found within budget and criteria")
            similar_cpu = CpuModel.from_orm(result)
            return similar_cpu.model_dump()

json_data = '''
{
"status": "success",
"message": "Данные пользователя успешно разобраны.",
"user_request": {
    "game": {
    "title": "cyberpunk_2077",
    "graphics": {
        "quality": "ultra",
        "target_fps": 60,
        "resolution": "2160",
        "ray_tracing": false,
        "dlss": "performance",
        "fsr": "disabled"
    }
    },
    "budget": {
    "amount": 200000,
    "currency": "RUB",
    "allocation_method": "fixed_price_based"
    },
    "components": {
    "mandatory": {
        "cpu": "any",
        "gpu": "any",
        "dimm": "any",
        "ssd": "any",
        "motherboard": "any",
        "power_supply": "any"
    },
    "optional": {
        "cooling": "any",
        "pc_case": "normal_size",
        "cpu_cooler": "included_with_cpu"
    }
    },
    "allocations": {
    "mandatory": {
        "method": "fixed_price_based",
        "fixed_price_based": {
        "cpu_max_price": 30000,
        "gpu_max_price": 120000,
        "dimm_max_price": 15000,
        "ssd_max_price": 12000,
        "motherboard_max_price": 20000,
        "power_supply_max_price": 15000
        }
    },
    "optional": {
        "method": "fixed_price_based",
        "fixed_price_based": {
        "cooling_max_price": 10000,
        "pc_case_max_price": 8000,
        "cpu_cooler_max_price": 0
        }
    }
    }
}
}
'''
input_data_1st_stage = {
        "game": "cyberpunk_2077",
        "quality": "ultra",
        "cpu": "Процессор Intel Core i7-14700K OEM",
        "gpu": "Видеокарта GIGABYTE GeForce RTX 4080 SUPER GAMING OC [GV-N408SGAMING OC-16GD]",
        "ssd": "2000 ГБ M.2 NVMe накопитель WD Black SN770 [WDS200T3X0E]",
        "dimm": "Оперативная память G.Skill Trident Z5 RGB [F5-7800J3646H16GX2-TZ5RK] 32 ГБ"
    }

if __name__ == "__main__":
    import json

    input_data_2nd_stage = json.loads(json_data)

    try:
        cpu_info = find_similar_cpu(input_data_2nd_stage, input_data_1st_stage)
        print(cpu_info)
    except ValueError as e:
        print(f"Error: {e}")

from typing import Dict, Any
from psycopg2.extras import DictCursor
import sys
import os

# Добавляем корневой путь проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.cpu import CpuModel

def get_cpu_model_by_name(input_data: Dict[str, Any]) -> CpuModel:
    """
    Получает объект CpuModel по имени CPU из input_data.
    Вызывает исключение ValueError, если CPU не найден или не указан.
    """
    cpu_name = input_data.get('cpu')
    if not cpu_name:
        raise ValueError("CPU name not found in input data")

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

def process_cpu_lookup(input_data: Dict[str, Any]) -> None:
    """
    Оборачивает вызов функции получения CPU-модели с выводом результата или ошибки.
    """
    try:
        cpu_specs = get_cpu_model_by_name(input_data)
        print(cpu_specs.model_dump())
    except ValueError as e:
        print(f"Error: {e}")

# Пример использования
if __name__ == "__main__":
    input_data_1st_stage = {
        "game": "cyberpunk_2077",
        "quality": "ultra",
        "cpu": "Процессор Intel Core i7-14700K OEM",
        "gpu": "Видеокарта GIGABYTE GeForce RTX 4080 SUPER GAMING OC [GV-N408SGAMING OC-16GD]",
        "ssd": "2000 ГБ M.2 NVMe накопитель WD Black SN770 [WDS200T3X0E]",
        "dimm": "Оперативная память G.Skill Trident Z5 RGB [F5-7800J3646H16GX2-TZ5RK] 32 ГБ"
    }

    process_cpu_lookup(input_data_1st_stage)

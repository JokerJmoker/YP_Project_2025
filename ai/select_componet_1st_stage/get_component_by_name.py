from typing import Dict, Any, Type
from psycopg2.extras import DictCursor
import sys
import os

# Добавляем корневой путь проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.cpu import CpuModel
from ai.models.components.gpu import GpuModel
from ai.models.components.ssd_m2 import SsdM2Model
from ai.models.components.dimm import DimmModel

# Сопоставление ключа с моделью
COMPONENT_MODELS: Dict[str, Type] = {
    "cpu": CpuModel,
    "gpu": GpuModel,
    "ssd_m2": SsdM2Model,
    "dimm": DimmModel
}

def get_component_model_by_name(
    input_data: Dict[str, Any],
    key: str,
    model_class: Type,
    schema: str = 'pc_components',
    table: str = ''
):
    """
    Универсальная функция получения ORM-модели компонента по его имени.
    """
    component_name = input_data.get(key)
    if not component_name:
        raise ValueError(f"{key.upper()} name not found in input data")

    if not table:
        table = key  # Таблица совпадает с ключом по умолчанию

    query = f"""
        SELECT * FROM {schema}.{table}
        WHERE name = %s
        LIMIT 1
    """

    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (component_name,))
            result = cursor.fetchone()

            if not result:
                raise ValueError(f"{key.upper()} '{component_name}' not found in database")

            return model_class.from_orm(result)

def process_component_lookup(input_data: Dict[str, Any], key: str) -> None:
    """
    Обрабатывает один указанный компонент по ключу ("cpu", "gpu" и тд).
    """
    model_class = COMPONENT_MODELS.get(key)
    if not model_class:
        raise ValueError(f"Unsupported component key: '{key}'")

    try:
        component = get_component_model_by_name(input_data, key, model_class)
        print(f"{key.upper()} Specs:")
        print(component.model_dump())
    except ValueError as e:
        print(f"Error: {e}")

# Пример использования
if __name__ == "__main__":
    input_data_1st_stage = {
        "game": "cyberpunk_2077",
        "quality": "ultra",
        "cpu": "Процессор Intel Core i7-14700K OEM",
        "gpu": "Видеокарта GIGABYTE GeForce RTX 4080 SUPER GAMING OC [GV-N408SGAMING OC-16GD]",
        "ssd_m2": "2000 ГБ M.2 NVMe накопитель WD Black SN770 [WDS200T3X0E]",
        "dimm": "Оперативная память G.Skill Trident Z5 RGB [F5-7800J3646H16GX2-TZ5RK] 32 ГБ"
    }

    # Можно поочерёдно вызвать для любого ключа:
    process_component_lookup(input_data_1st_stage, "cpu")
    process_component_lookup(input_data_1st_stage, "gpu")
    process_component_lookup(input_data_1st_stage, "ssd_m2")
    process_component_lookup(input_data_1st_stage, "dimm")

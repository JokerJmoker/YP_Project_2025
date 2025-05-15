import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.sodimm import SoDimm
from app.extensions import db

import easygui

DEBUG = True

def extract_spec_value(specs, section, key, default=''):
    return specs.get(section, {}).get(key, default)

def str_to_bool(value):
    return value.strip().lower() in ['есть', 'да', 'true']

def load_sodimm_data(filepath=None):
    if filepath is None:
        filepath = easygui.fileopenbox(
            msg="Выберите JSON или JSONL файл с данными SO-DIMM",
            title="Выбор файла",
            default=str(project_root / "app/load_data_to_db_by_model/*.*"),
            filetypes=["*.json", "*.jsonl"]
        )
        if not filepath:
            print("[ERROR] Файл не выбран. Загрузка отменена.")
            return False

    print(f"[INFO] Читаем файл: {filepath}")

    try:
        if filepath.endswith('.jsonl'):
            with open(filepath, 'r', encoding='utf-8') as f:
                data_list = [json.loads(line) for line in f if line.strip()]
        else:
            with open(filepath, 'r', encoding='utf-8') as f:
                data_list = json.load(f)
        print(f"[INFO] Прочитано {len(data_list)} записей из файла")
    except Exception as e:
        print(f"[ERROR] Ошибка чтения файла: {str(e)}")
        return False

    existing_count = db.session.query(SoDimm).count()
    if existing_count > 0:
        print(f"[WARNING] В БД уже есть {existing_count} записей SO-DIMM. Загрузка будет ПРОПУЩЕНА.")
        return False

    loaded_count = 0

    for index, item in enumerate(data_list, 1):
        try:
            specs = item.get('specs', {})

            sodimm = SoDimm()
            sodimm.name = item.get('name', '')
            sodimm.price = item.get('price', '')
            sodimm.image_url = item.get('image_url', '')
            sodimm.image_path = item.get('image_path', '')
            sodimm.warranty = extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца / производителя')
            sodimm.country = extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')
            sodimm.type = extract_spec_value(specs, 'Общие параметры', 'Тип')
            sodimm.model = extract_spec_value(specs, 'Общие параметры', 'Модель')
            sodimm.manufacturer_code = extract_spec_value(specs, 'Общие параметры', 'Код производителя')
            sodimm.memory_type = extract_spec_value(specs, 'Объем и состав комплекта', 'Тип памяти')
            sodimm.total_memory = extract_spec_value(specs, 'Объем и состав комплекта', 'Суммарный объем памяти всего комплекта')
            sodimm.module_memory = extract_spec_value(specs, 'Объем и состав комплекта', 'Объем одного модуля памяти')
            sodimm.module_count = extract_spec_value(specs, 'Объем и состав комплекта', 'Количество модулей в комплекте')
            sodimm.frequency = extract_spec_value(specs, 'Быстродействие', 'Частота')
            sodimm.cas_latency = extract_spec_value(specs, 'Тайминги', 'CAS Latency (CL)')
            sodimm.ras_to_cas_delay = extract_spec_value(specs, 'Тайминги', 'RAS to CAS Delay (tRCD)')
            sodimm.row_precharge_delay = extract_spec_value(specs, 'Тайминги', 'Row Precharge Delay (tRP)')
            sodimm.activate_to_precharge_delay = extract_spec_value(specs, 'Тайминги', 'Activate to Precharge Delay')
            sodimm.double_sided = str_to_bool(extract_spec_value(specs, 'Конструктивные особенности', 'Двухсторонняя установка чипов', 'нет'))
            sodimm.heatsink = str_to_bool(extract_spec_value(specs, 'Конструктивные особенности', 'Радиатор охлаждения', 'нет'))
            sodimm.voltage = extract_spec_value(specs, 'Дополнительная информация', 'Напряжение питания')

            db.session.add(sodimm)
            loaded_count += 1

            if DEBUG:
                print(f"[DEBUG] Добавляем запись: {sodimm.name}")

        except Exception as e:
            print(f"[ERROR] Ошибка обработки записи {index}: {str(e)}")
            db.session.rollback()
            continue

    try:
        db.session.commit()
        print(f"[INFO] Загружено {loaded_count}/{len(data_list)} записей SO-DIMM")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Ошибка коммита в БД: {str(e)}")
        return False

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("=== Начало загрузки данных SO-DIMM ===")

        confirm = easygui.ynbox(
            msg="Добавить новые данные в базу ? "
                "\n\n Если в БД уже есть данные, загрузка будет пропущена.",
            title="Загрузка SO-DIMM",
            choices=["Да", "Нет"]
        )

        if not confirm:
            print("Операция отменена пользователем.")
            sys.exit(0)

        success = load_sodimm_data()
        if success:
            print("Загрузка завершена успешно.")
        else:
            print("Загрузка не выполнена (либо данные уже есть, либо возникли ошибки)")
        print("=====================================")

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.cpu import Cpu
from app.extensions import db

import easygui

DEBUG = True

def extract_spec_value(specs, section, key, default=''):
    return specs.get(section, {}).get(key, default)

def str_to_bool(value):
    return value.strip().lower() in ['есть', 'да', 'true']

def load_cpu_data(filepath=None):
    if filepath is None:
        filepath = easygui.fileopenbox(
            msg="Выберите JSON или JSONL файл с данными CPU",
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

    existing_count = db.session.query(Cpu).count()
    if existing_count > 0:
        print(f"[WARNING] В БД уже есть {existing_count} записей CPU. Загрузка будет ПРОПУЩЕНА.")
        return False

    loaded_count = 0

    for index, item in enumerate(data_list, 1):
        try:
            specs = item.get('specs', {})

            cpu = Cpu()
            cpu.name = item.get('name', '')
            cpu.price = item.get('price', '')
            cpu.image_url = item.get('image_url', '')
            cpu.image_path = item.get('image_path', '')

            cpu.warranty = extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца')
            cpu.country = extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')
            cpu.model = extract_spec_value(specs, 'Общие параметры', 'Модель')
            cpu.socket = extract_spec_value(specs, 'Общие параметры', 'Сокет')
            cpu.manufacturer_code = extract_spec_value(specs, 'Общие параметры', 'Код производителя')
            cpu.release_year = extract_spec_value(specs, 'Общие параметры', 'Год релиза')
            cpu.cooler_included = not str_to_bool(extract_spec_value(specs, 'Общие параметры', 'Система охлаждения в комплекте', 'нет'))
            cpu.thermal_interface_included = not str_to_bool(extract_spec_value(specs, 'Общие параметры', 'Термоинтерфейс в комплекте', 'нет'))

            cpu.total_cores = extract_spec_value(specs, 'Ядро и архитектура', 'Общее количество ядер')
            cpu.performance_cores = extract_spec_value(specs, 'Ядро и архитектура', 'Количество производительных ядер')
            cpu.efficiency_cores = extract_spec_value(specs, 'Ядро и архитектура', 'Количество энергоэффективных ядер')
            cpu.max_threads = extract_spec_value(specs, 'Ядро и архитектура', 'Максимальное число потоков')
            cpu.l2_cache = extract_spec_value(specs, 'Ядро и архитектура', 'Объем кэша L2')
            cpu.l3_cache = extract_spec_value(specs, 'Ядро и архитектура', 'Объем кэша L3')
            cpu.process_technology = extract_spec_value(specs, 'Ядро и архитектура', 'Техпроцесс')
            cpu.core_architecture = extract_spec_value(specs, 'Ядро и архитектура', 'Ядро')

            cpu.base_frequency = extract_spec_value(specs, 'Частота и возможность разгона', 'Базовая частота процессора')
            cpu.turbo_frequency = extract_spec_value(specs, 'Частота и возможность разгона', 'Максимальная частота в турбо режиме')
            cpu.base_efficiency_frequency = extract_spec_value(specs, 'Частота и возможность разгона', 'Базовая частота энергоэффективных ядер')
            cpu.turbo_efficiency_frequency = extract_spec_value(specs, 'Частота и возможность разгона', 'Частота в турбо режиме энергоэффективных ядер')
            cpu.unlocked_multiplier = str_to_bool(extract_spec_value(specs, 'Частота и возможность разгона', 'Свободный множитель', 'нет'))

            cpu.memory_type = extract_spec_value(specs, 'Параметры оперативной памяти', 'Тип памяти')
            cpu.max_memory = extract_spec_value(specs, 'Параметры оперативной памяти', 'Максимально поддерживаемый объем памяти')
            cpu.memory_channels = extract_spec_value(specs, 'Параметры оперативной памяти', 'Количество каналов')
            cpu.memory_frequency = extract_spec_value(specs, 'Параметры оперативной памяти', 'Частота оперативной памяти')
            cpu.ecc_support = str_to_bool(extract_spec_value(specs, 'Параметры оперативной памяти', 'Поддержка режима ECC', 'нет'))

            cpu.tdp = extract_spec_value(specs, 'Тепловые характеристики', 'Тепловыделение (TDP)')
            cpu.base_tdp = extract_spec_value(specs, 'Тепловые характеристики', 'Базовое тепловыделение')
            cpu.max_temperature = extract_spec_value(specs, 'Тепловые характеристики', 'Максимальная температура процессора')

            cpu.integrated_graphics = str_to_bool(extract_spec_value(specs, 'Графическое ядро', 'Интегрированное графическое ядро', 'нет'))
            cpu.gpu_model = extract_spec_value(specs, 'Графическое ядро', 'Модель графического процессора')
            cpu.gpu_frequency = extract_spec_value(specs, 'Графическое ядро', 'Максимальная частота графического ядра')
            cpu.execution_units = extract_spec_value(specs, 'Графическое ядро', 'Исполнительные блоки')
            cpu.shading_units = extract_spec_value(specs, 'Графическое ядро', 'Потоковые процессоры (Shading Units)')

            cpu.pci_express = extract_spec_value(specs, 'Шина и контроллеры', 'Встроенный контроллер PCI Express')
            cpu.pci_lanes = extract_spec_value(specs, 'Шина и контроллеры', 'Число линий PCI Express')

            cpu.virtualization = str_to_bool(extract_spec_value(specs, 'Дополнительная информация', 'Технология виртуализации', 'нет'))
            cpu.features = extract_spec_value(specs, 'Дополнительная информация', 'Особенности, дополнительно')

            db.session.add(cpu)
            loaded_count += 1

            if DEBUG:
                print(f"[DEBUG] Добавляем запись: {cpu.name}")

        except Exception as e:
            print(f"[ERROR] Ошибка обработки записи {index}: {str(e)}")
            db.session.rollback()
            continue

    try:
        db.session.commit()
        print(f"[INFO] Загружено {loaded_count}/{len(data_list)} записей CPU")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Ошибка коммита в БД: {str(e)}")
        return False

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        print("=== Начало загрузки данных CPU ===")

        confirm = easygui.ynbox(
            msg="Добавить новые данные в базу?\n\nЕсли в БД уже есть данные, загрузка будет пропущена.",
            title="Загрузка CPU",
            choices=["Да", "Нет"]
        )

        if not confirm:
            print("Операция отменена пользователем.")
            sys.exit(0)

        success = load_cpu_data()
        if success:
            print("Загрузка завершена успешно.")
        else:
            print("Загрузка не выполнена (либо данные уже есть, либо возникли ошибки)")
        print("=====================================")

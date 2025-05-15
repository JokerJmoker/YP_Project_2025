import json
from pathlib import Path
import easygui
import sys
from abc import ABC, abstractmethod

class BaseDataLoader(ABC):
    def __init__(self, model_class, app, db, debug=True):
        self.model_class = model_class
        self.app = app
        self.db = db
        self.debug = debug
        # Стандартные пути (можно добавить в конфиг или передавать через параметры)
        self.default_paths = [
            Path("/home/jokerjmoker/dev/YP_Project/db/parser/parsed_products"),
            Path.cwd()  # Текущая рабочая директория как fallback
        ]

    def common_fields(self, instance, item):
        instance.name = item.get('name', '')
        instance.price = item.get('price', '')
        instance.image_url = item.get('image_url', '')
        instance.image_path = item.get('image_path', '')

    def get_default_path(self):
        """Возвращает первый существующий путь из списка default_paths"""
        for path in self.default_paths:
            if path.exists():
                return path
        return Path.cwd()  # Fallback

    def extract_spec_value(self, specs, section, key, default=''):
        return specs.get(section, {}).get(key, default)

    def str_to_bool(self, value):
        return value.strip().lower() in ['есть', 'да', 'true']

    def log_debug(self, message):
        if self.debug:
            print(f"[DEBUG] {message}")

    def log_info(self, message):
        print(f"[INFO] {message}")

    def log_warning(self, message):
        print(f"[WARNING] {message}")

    def log_error(self, message):
        print(f"[ERROR] {message}")

    def load_data(self, filepath=None):
        if filepath is None:
            default_path = self.get_default_path()
            filepath = easygui.fileopenbox(
                msg=f"Выберите JSON или JSONL файл с данными {self.model_class.__name__}",
                title="Выбор файла",
                default=str(default_path / "*.*"),
                filetypes=["*.json", "*.jsonl"]
            )
            if not filepath:
                self.log_error("Файл не выбран. Загрузка отменена.")
                return False

        self.log_info(f"Читаем файл: {filepath}")

        try:
            if filepath.endswith('.jsonl'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data_list = [json.loads(line) for line in f if line.strip()]
            else:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data_list = json.load(f)
            self.log_info(f"Прочитано {len(data_list)} записей из файла")
        except Exception as e:
            self.log_error(f"Ошибка чтения файла: {str(e)}")
            return False

        existing_count = self.db.session.query(self.model_class).count()
        if existing_count > 0:
            self.log_warning(f"В БД уже есть {existing_count} записей {self.model_class.__name__}. Загрузка будет ПРОПУЩЕНА.")
            return False

        loaded_count = 0

        for index, item in enumerate(data_list, 1):
            try:
                instance = self.create_instance(item)
                self.db.session.add(instance)
                self.db.session.commit()  # Коммитим по каждой записи

                loaded_count += 1
                self.log_debug(f"Добавлена запись {index}: {getattr(instance, 'name', 'Без имени')}")

            except Exception as e:
                self.db.session.rollback()
                self.log_error(f"Ошибка обработки записи {index}: {str(e)}")
                continue

        self.log_info(f"Загружено {loaded_count}/{len(data_list)} записей {self.model_class.__name__}")
        return loaded_count == len(data_list)
    
    def run_interactive(self):
        """
        Запуск загрузки с выбором файла и подтверждением пользователя.
        Возвращает True, если загрузка прошла успешно, иначе False.
        """
        print(f"=== Начало загрузки данных {self.model_class.__name__} ===")

        confirm = easygui.ynbox(
            msg=f"Добавить новые данные в базу?\n\nЕсли в БД уже есть данные, загрузка будет пропущена.",
            title=f"Загрузка {self.model_class.__name__}",
            choices=["Да", "Нет"]
        )

        if not confirm:
            print("Операция отменена пользователем.")
            sys.exit(0)

        success = self.load_data()

        if success:
            print("Загрузка завершена успешно.")
        else:
            print("Загрузка не выполнена (либо данные уже есть, либо возникли ошибки)")

        print("=====================================")
        return success

    @abstractmethod
    def create_instance(self, item):
        """
        Метод должен быть реализован в дочернем классе для создания экземпляра модели из item.
        """
        pass
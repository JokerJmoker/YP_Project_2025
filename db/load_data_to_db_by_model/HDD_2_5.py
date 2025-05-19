import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.hdd_2_5 import Hdd_2_5
from app.extensions import db

from basedataloader import BaseDataLoader

class HDDDataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        hdd = self.model_class()

        self.common_fields(hdd, item)

        # Заводские данные
        hdd.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца')
        hdd.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')

        # Общие параметры
        hdd.type = self.extract_spec_value(specs, 'Общие параметры', 'Тип')
        hdd.model = self.extract_spec_value(specs, 'Общие параметры', 'Модель')
        hdd.manufacturer_code = self.extract_spec_value(specs, 'Общие параметры', 'Код производителя')

        # Характеристики накопителя
        hdd.capacity = self.extract_spec_value(specs, 'Накопитель', 'Объем HDD')
        hdd.buffer_size = self.extract_spec_value(specs, 'Накопитель', 'Объем буфера')
        hdd.rotation_speed = self.extract_spec_value(specs, 'Накопитель', 'Скорость вращения шпинделя')
        hdd.data_transfer_rate = self.extract_spec_value(specs, 'Накопитель', 'Скорость обмена данными')
        hdd.seek_time = self.extract_spec_value(specs, 'Накопитель', 'Среднее время доступа, чтение')
        hdd.interface = self.extract_spec_value(specs, 'Накопитель', 'Интерфейс')
        hdd.interface_speed = self.extract_spec_value(specs, 'Накопитель', 'Пропускная способность интерфейса')

        # Механика и надежность
        hdd.recording_tech = self.extract_spec_value(specs, 'Механика и надежность', 'Технология записи')
        hdd.shock_resistance = self.extract_spec_value(specs, 'Механика и надежность', 'Ударостойкость при работе')
        hdd.noise_operation = self.extract_spec_value(specs, 'Механика и надежность', 'Уровень шума во время работы')
        hdd.noise_idle = self.extract_spec_value(specs, 'Механика и надежность', 'Уровень шума в простое')
        hdd.load_cycles = self.extract_spec_value(specs, 'Механика и надежность', 'Число циклов позиционирования-парковки')

        # Энергопотребление
        hdd.max_power = self.extract_spec_value(specs, 'Дополнительная информация', 'Максимальное энергопотребление')
        hdd.idle_power = self.extract_spec_value(specs, 'Дополнительная информация', 'Энергопотребление в режиме ожидания')

        # Температурный режим
        hdd.min_temp = self.extract_spec_value(specs, 'Дополнительная информация', 'Минимальная рабочая температура')
        hdd.max_temp = self.extract_spec_value(specs, 'Дополнительная информация', 'Максимальная рабочая температура')

        # Габариты и вес
        hdd.width = self.extract_spec_value(specs, 'Габариты и вес', 'Ширина')
        hdd.length = self.extract_spec_value(specs, 'Габариты и вес', 'Длина')
        hdd.thickness = self.extract_spec_value(specs, 'Габариты и вес', 'Стандартная толщина')
        hdd.weight = self.extract_spec_value(specs, 'Габариты и вес', 'Вес')

        # Метаданные
        hdd.worker_id = item.get('_worker_id', None)
        hdd.url_index = item.get('_url_index', None)

        return hdd

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = HDDDataLoader(Hdd_2_5, app, db)
        loader.run_interactive()
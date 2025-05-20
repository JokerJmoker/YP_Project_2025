import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.ssd_m2 import SsdM2
from app.extensions import db

from basedataloader import BaseDataLoader

class SsdM2DataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        ssd = self.model_class()

        self.common_fields(ssd, item)

        # Заводские данные
        ssd.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца')
        ssd.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')

        # Общие параметры
        ssd.type = self.extract_spec_value(specs, 'Общие параметры', 'Тип')
        ssd.model = self.extract_spec_value(specs, 'Общие параметры', 'Модель')
        ssd.manufacturer_code = self.extract_spec_value(specs, 'Общие параметры', 'Код производителя')

        # Основные характеристики
        ssd.capacity = self.extract_spec_value(specs, 'Основные характеристики', 'Объем накопителя')
        ssd.form_factor = self.extract_spec_value(specs, 'Основные характеристики', 'Форм-фактор')
        ssd.interface = self.extract_spec_value(specs, 'Основные характеристики', 'Физический интерфейс')
        ssd.m2_key = self.extract_spec_value(specs, 'Основные характеристики', 'Ключ M.2 разъема')
        ssd.nvme = self.str_to_bool(self.extract_spec_value(specs, 'Основные характеристики', 'NVMe', 'нет'))

        # Конфигурация накопителя
        ssd.controller = self.extract_spec_value(specs, 'Конфигурация накопителя', 'Контроллер')
        ssd.cell_type = self.extract_spec_value(specs, 'Конфигурация накопителя', 'Количество бит на ячейку')
        ssd.memory_structure = self.extract_spec_value(specs, 'Конфигурация накопителя', 'Структура памяти')
        ssd.has_dram = self.str_to_bool(self.extract_spec_value(specs, 'Конфигурация накопителя', 'DRAM буфер', 'нет'))
        ssd.dram_size = self.extract_spec_value(specs, 'Конфигурация накопителя', 'Объем DRAM буфера')

        # Показатели скорости
        ssd.max_read_speed = self.extract_spec_value(specs, 'Показатели скорости', 'Максимальная скорость последовательного чтения')
        ssd.max_write_speed = self.extract_spec_value(specs, 'Показатели скорости', 'Максимальная скорость последовательной записи')
        ssd.random_read_iops = self.extract_spec_value(specs, 'Показатели скорости', 'Чтение случайных блоков 4 Кбайт (QD32)')
        ssd.random_write_iops = self.extract_spec_value(specs, 'Показатели скорости', 'Запись случайных блоков 4 Кбайт (QD32)')

        # Надежность
        ssd.tbw = self.extract_spec_value(specs, 'Надежность', 'Максимальный ресурс записи (TBW)')
        ssd.dwpd = self.extract_spec_value(specs, 'Надежность', 'DWPD')

        # Дополнительная информация
        ssd.heatsink_included = self.str_to_bool(self.extract_spec_value(specs, 'Дополнительная информация', 'Радиатор в комплекте', 'нет'))
        ssd.power_consumption = self.extract_spec_value(specs, 'Дополнительная информация', 'Энергопотребление')
        ssd.features = self.extract_spec_value(specs, 'Дополнительная информация', 'Особенности, дополнительно')

        # Габариты
        ssd.length = self.extract_spec_value(specs, 'Габариты', 'Длина')
        ssd.width = self.extract_spec_value(specs, 'Габариты', 'Ширина')
        ssd.thickness = self.extract_spec_value(specs, 'Габариты', 'Толщина')
        ssd.weight = self.extract_spec_value(specs, 'Габариты', 'Вес')

        # Метаданные
        ssd.worker_id = item.get('_worker_id', None)
        ssd.url_index = item.get('_url_index', None)

        return ssd

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = SsdM2DataLoader(SsdM2, app, db)
        loader.run_interactive()
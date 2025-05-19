import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.dimm import Dimm
from app.extensions import db

from basedataloader import BaseDataLoader

class DIMMDataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        dimm = self.model_class()

        self.common_fields(dimm, item)

        # Заводские данные
        dimm.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца / производителя')
        dimm.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')

        # Общие параметры
        dimm.type = self.extract_spec_value(specs, 'Общие параметры', 'Тип')
        dimm.model = self.extract_spec_value(specs, 'Общие параметры', 'Модель')
        dimm.manufacturer_code = self.extract_spec_value(specs, 'Общие параметры', 'Код производителя')

        # Объем и состав комплекта
        dimm.memory_type = self.extract_spec_value(specs, 'Объем и состав комплекта', 'Тип памяти')
        dimm.module_type = self.extract_spec_value(specs, 'Объем и состав комплекта', 'Тип модуля памяти')
        dimm.total_memory = self.extract_spec_value(specs, 'Объем и состав комплекта', 'Суммарный объем памяти всего комплекта')
        dimm.single_module_memory = self.extract_spec_value(specs, 'Объем и состав комплекта', 'Объем одного модуля памяти')
        dimm.modules_count = self.extract_spec_value(specs, 'Объем и состав комплекта', 'Количество модулей в комплекте')
        dimm.registered_memory = self.str_to_bool(self.extract_spec_value(specs, 'Объем и состав комплекта', 'Регистровая память', 'нет'))
        dimm.ecc_memory = self.str_to_bool(self.extract_spec_value(specs, 'Объем и состав комплекта', 'ECC-память', 'нет'))

        # Быстродействие
        dimm.frequency = self.extract_spec_value(specs, 'Быстродействие', 'Тактовая частота')
        dimm.amd_expo = self.extract_spec_value(specs, 'Быстродействие', 'Профили AMD EXPO')
        dimm.intel_xmp = self.extract_spec_value(specs, 'Быстродействие', 'Профили Intel XMP')

        # Тайминги
        dimm.cas_latency = self.extract_spec_value(specs, 'Тайминги', 'CAS Latency (CL)')
        dimm.ras_to_cas_delay = self.extract_spec_value(specs, 'Тайминги', 'RAS to CAS Delay (tRCD)')
        dimm.row_precharge_delay = self.extract_spec_value(specs, 'Тайминги', 'Row Precharge Delay (tRP)')
        dimm.activate_to_precharge_delay = self.extract_spec_value(specs, 'Тайминги', 'Activate to Precharge Delay (tRAS)')

        # Конструкция
        dimm.has_heatsink = self.str_to_bool(self.extract_spec_value(specs, 'Конструкция', 'Наличие радиатора', 'нет'))
        dimm.heatsink_color = self.extract_spec_value(specs, 'Конструкция', 'Цвет радиатора')
        dimm.has_lighting = self.str_to_bool(self.extract_spec_value(specs, 'Конструкция', 'Подсветка элементов платы', 'нет'))
        dimm.height = self.extract_spec_value(specs, 'Конструкция', 'Высота')
        dimm.low_profile = self.str_to_bool(self.extract_spec_value(specs, 'Конструкция', 'Низкопрофильная (Low Profile)', 'нет'))

        # Дополнительная информация
        dimm.voltage = self.extract_spec_value(specs, 'Дополнительная информация', 'Напряжение питания')
        dimm.features = self.extract_spec_value(specs, 'Дополнительная информация', 'Особенности, дополнительно')
        dimm.package_contents = self.extract_spec_value(specs, 'Дополнительная информация', 'Комплектация')

        # Метаданные
        dimm.worker_id = item.get('_worker_id', None)
        dimm.url_index = item.get('_url_index', None)

        return dimm

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = DIMMDataLoader(Dimm, app, db)
        loader.run_interactive()
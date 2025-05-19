import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.so_dimm import SoDimm
from app.extensions import db

from basedataloader import BaseDataLoader  # Общий базовый загрузчик


class SoDimmDataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        sodimm = self.model_class()

        self.common_fields(sodimm, item)

        # Заводские данные
        sodimm.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца / производителя')
        sodimm.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')

        # Общие параметры
        sodimm.type_ = self.extract_spec_value(specs, 'Общие параметры', 'Тип')
        sodimm.model = self.extract_spec_value(specs, 'Общие параметры', 'Модель')
        sodimm.manufacturer_code = self.extract_spec_value(specs, 'Общие параметры', 'Код производителя')
        sodimm.color = self.extract_spec_value(specs, 'Общие параметры', 'Цвет')

        # Объем и состав комплекта
        sodimm.memory_type = self.extract_spec_value(specs, 'Объем и состав комплекта', 'Тип памяти')
        sodimm.total_memory = self.extract_spec_value(specs, 'Объем и состав комплекта', 'Суммарный объем памяти всего комплекта')
        sodimm.module_memory = self.extract_spec_value(specs, 'Объем и состав комплекта', 'Объем одного модуля памяти')
        sodimm.module_count = self.extract_spec_value(specs, 'Объем и состав комплекта', 'Количество модулей в комплекте')

        # Быстродействие
        sodimm.frequency = self.extract_spec_value(specs, 'Быстродействие', 'Частота')

        # Тайминги
        sodimm.cas_latency = self.extract_spec_value(specs, 'Тайминги', 'CAS Latency (CL)')
        sodimm.ras_to_cas_delay = self.extract_spec_value(specs, 'Тайминги', 'RAS to CAS Delay (tRCD)')
        sodimm.row_precharge_delay = self.extract_spec_value(specs, 'Тайминги', 'Row Precharge Delay (tRP)')
        sodimm.activate_to_precharge_delay = self.extract_spec_value(specs, 'Тайминги', 'Activate to Precharge Delay (tRAS)')

        # Конструктивные особенности
        sodimm.chip_count = self.extract_spec_value(specs, 'Конструктивные особенности', 'Количество чипов модуля')
        sodimm.double_sided = self.str_to_bool(self.extract_spec_value(specs, 'Конструктивные особенности', 'Двухсторонняя установка чипов', 'нет'))
        sodimm.heatsink = self.str_to_bool(self.extract_spec_value(specs, 'Конструктивные особенности', 'Радиатор', 'нет'))

        # Дополнительная информация
        sodimm.voltage = self.extract_spec_value(specs, 'Дополнительная информация', 'Напряжение питания')

        return sodimm


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = SoDimmDataLoader(SoDimm, app, db)
        loader.run_interactive()

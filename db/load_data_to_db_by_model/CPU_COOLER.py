import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.CPU_COOLER import CpuCooler
from app.extensions import db

from basedataloader import BaseDataLoader

class CpuCoolerDataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        cooler = self.model_class()
        self.common_fields(cooler, item)

        # Заводские данные
        cooler.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца / производителя')
        cooler.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')

        # Общие параметры
        cooler.type_ = self.extract_spec_value(specs, 'Общие параметры', 'Тип')
        cooler.model = self.extract_spec_value(specs, 'Общие параметры', 'Модель')
        cooler.manufacturer_code = self.extract_spec_value(specs, 'Общие параметры', 'Код производителя')
        cooler.socket = self.extract_spec_value(specs, 'Общие параметры', 'Сокет')
        cooler.tdp = self.extract_spec_value(specs, 'Общие параметры', 'Рассеиваемая мощность')
        cooler.design_type = self.extract_spec_value(specs, 'Общие параметры', 'Тип конструкции')

        # Радиатор
        cooler.base_material = self.extract_spec_value(specs, 'Радиатор', 'Материал основания')
        cooler.heatsink_material = self.extract_spec_value(specs, 'Радиатор', 'Материал радиатора')
        cooler.heatpipe_count = self.extract_spec_value(specs, 'Радиатор', 'Количество тепловых трубок')
        cooler.heatpipe_diameter = self.extract_spec_value(specs, 'Радиатор', 'Диаметр тепловых трубок')
        cooler.nickel_coating = self.extract_spec_value(specs, 'Радиатор', 'Никелированное покрытие')
        cooler.heatsink_color = self.extract_spec_value(specs, 'Радиатор', 'Цвет радиатора')

        # Вентилятор
        cooler.fan_count = self.extract_spec_value(specs, 'Вентилятор', 'Количество вентиляторов в комплекте')
        cooler.fan_max_count = self.extract_spec_value(specs, 'Вентилятор', 'Максимальное число устанавливаемых вентиляторов')
        cooler.fan_size = self.extract_spec_value(specs, 'Вентилятор', 'Размеры комплектных вентиляторов')
        cooler.fan_color = self.extract_spec_value(specs, 'Вентилятор', 'Цвет вентилятора')
        cooler.fan_connector = self.extract_spec_value(specs, 'Вентилятор', 'Разъем для подключения вентиляторов')
        cooler.max_rpm = self.extract_spec_value(specs, 'Вентилятор', 'Максимальная скорость вращения')
        cooler.min_rpm = self.extract_spec_value(specs, 'Вентилятор', 'Минимальная скорость вращения')
        cooler.pwm_control = self.extract_spec_value(specs, 'Вентилятор', 'Регулировка скорости вращения')
        cooler.max_airflow = self.extract_spec_value(specs, 'Вентилятор', 'Максимальный воздушный поток')
        cooler.max_static_pressure = self.extract_spec_value(specs, 'Вентилятор', 'Максимальное статическое давление')
        cooler.max_noise_level = self.extract_spec_value(specs, 'Вентилятор', 'Максимальный уровень шума')
        cooler.rated_current = self.extract_spec_value(specs, 'Вентилятор', 'Номинальный ток')
        cooler.rated_voltage = self.extract_spec_value(specs, 'Вентилятор', 'Номинальное напряжение')
        cooler.bearing_type = self.extract_spec_value(specs, 'Вентилятор', 'Тип подшипника')

        # Дополнительная информация
        cooler.thermal_paste_included = self.extract_spec_value(specs, 'Дополнительная информация', 'Термопаста в комплекте')
        cooler.lighting_type = self.extract_spec_value(specs, 'Дополнительная информация', 'Тип подсветки')
        cooler.lighting_connector = self.extract_spec_value(specs, 'Дополнительная информация', 'Тип разъема питания подсветки')
        cooler.lighting_source = self.extract_spec_value(specs, 'Дополнительная информация', 'Источник подсветки')
        cooler.extra_info = self.extract_spec_value(specs, 'Дополнительная информация', 'Дополнительная информация')
        cooler.package_contents = self.extract_spec_value(specs, 'Дополнительная информация', 'Комплектация')

        # Габариты и вес
        cooler.height = self.extract_spec_value(specs, 'Габариты и вес', 'Высота')
        cooler.width = self.extract_spec_value(specs, 'Габариты и вес', 'Ширина')
        cooler.depth = self.extract_spec_value(specs, 'Габариты и вес', 'Длина')
        cooler.weight = self.extract_spec_value(specs, 'Габариты и вес', 'Вес')

        # Метаданные
        cooler.worker_id = item.get('_worker_id', None)
        cooler.url_index = item.get('_url_index', None)

        return cooler

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = CpuCoolerDataLoader(CpuCooler, app, db)
        loader.run_interactive()

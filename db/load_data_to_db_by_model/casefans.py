import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.casefan import CaseFan
from app.extensions import db

from basedataloader import BaseDataLoader  

class CaseFanDataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        fan = self.model_class()

        self.populate_common_fields(fan, item)

        # Заводские данные
        fan.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца / производителя')
        fan.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')

        # Общие параметры
        fan.type = self.extract_spec_value(specs, 'Общие параметры', 'Тип')
        fan.model = self.extract_spec_value(specs, 'Общие параметры', 'Модель')
        fan.manufacturer_code = self.extract_spec_value(specs, 'Общие параметры', 'Код производителя')
        fan.fans_count = self.extract_spec_value(specs, 'Общие параметры', 'Количество вентиляторов в комплекте')

        # Внешний вид
        fan.frame_color = self.extract_spec_value(specs, 'Внешний вид', 'Цвет каркаса')
        fan.impeller_color = self.extract_spec_value(specs, 'Внешний вид', 'Цвет крыльчатки')
        fan.lighting_type = self.extract_spec_value(specs, 'Внешний вид', 'Тип подсветки')
        fan.lighting_source = self.extract_spec_value(specs, 'Внешний вид', 'Источник подсветки')

        # Конструкция
        fan.fan_size = self.extract_spec_value(specs, 'Конструкция', 'Размер вентилятора')
        fan.fan_thickness = self.extract_spec_value(specs, 'Конструкция', 'Толщина вентилятора')
        fan.bearing_type = self.extract_spec_value(specs, 'Конструкция', 'Тип подшипника')
        fan.anti_vibration_pad = self.str_to_bool(self.extract_spec_value(specs, 'Конструкция', 'Антивибрационная прокладка', 'нет'))

        # Технические характеристики
        fan.max_rotation_speed = self.extract_spec_value(specs, 'Технические характеристики', 'Максимальная скорость вращения')
        fan.min_rotation_speed = self.extract_spec_value(specs, 'Технические характеристики', 'Минимальная скорость вращения')
        fan.max_airflow = self.extract_spec_value(specs, 'Технические характеристики', 'Воздушный поток на максимальной скорости')
        fan.max_static_pressure = self.extract_spec_value(specs, 'Технические характеристики', 'Максимальное статическое давление')
        fan.max_noise_level = self.extract_spec_value(specs, 'Технические характеристики', 'Максимальный уровень шума')
        fan.min_noise_level = self.extract_spec_value(specs, 'Технические характеристики', 'Минимальный уровень шума')

        # Питание и подключение
        fan.power_connector_type = self.extract_spec_value(specs, 'Питание и подключение', 'Тип разъема питания вентилятора')
        fan.rpm_control = self.extract_spec_value(specs, 'Питание и подключение', 'Регулировка оборотов')
        fan.nominal_voltage = self.extract_spec_value(specs, 'Питание и подключение', 'Номинальное напряжение')
        fan.max_current = self.extract_spec_value(specs, 'Питание и подключение', 'Максимальный ток')
        fan.lighting_power_connector_type = self.extract_spec_value(specs, 'Питание и подключение', 'Тип разъема питания подсветки')
        fan.adapters_included = self.extract_spec_value(specs, 'Питание и подключение', 'Переходники в комплекте')
        fan.hub_controller_included = self.extract_spec_value(specs, 'Питание и подключение', 'Хаб-контроллер в комплекте')
        fan.remote_control_included = self.extract_spec_value(specs, 'Питание и подключение', 'ПДУ в комплекте')

        # Дополнительная информация
        fan.additional_info = self.extract_spec_value(specs, 'Дополнительная информация', 'Дополнительно')
        fan.package_contents = self.extract_spec_value(specs, 'Дополнительная информация', 'Комплектация')

        # Метаданные
        fan.worker_id = item.get('_worker_id', None)
        fan.url_index = item.get('_url_index', None)

        return fan

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = CaseFanDataLoader(CaseFan, app, db)
        loader.run_interactive()

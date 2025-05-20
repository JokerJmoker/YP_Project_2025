import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.water_cooling import WaterCooling
from app.extensions import db

from basedataloader import BaseDataLoader

class WaterCoolingKitDataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        kit = self.model_class()

        self.common_fields(kit, item)

        # Заводские данные
        kit.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца / производителя')
        kit.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')

        # Классификация
        kit.type = self.extract_spec_value(specs, 'Классификация', 'Тип')
        kit.model = self.extract_spec_value(specs, 'Классификация', 'Модель')
        kit.manufacturer_code = self.extract_spec_value(specs, 'Классификация', 'Код производителя')
        kit.serviceable = self.str_to_bool(self.extract_spec_value(specs, 'Классификация', 'Обслуживаемая СЖО', 'нет'))

        # Внешний вид
        kit.color = self.extract_spec_value(specs, 'Внешний вид', 'Основной цвет')
        kit.lighting_type = self.extract_spec_value(specs, 'Внешний вид', 'Тип подсветки')
        kit.lighting_source = self.extract_spec_value(specs, 'Внешний вид', 'Источник подсветки')
        kit.lighting_connector = self.extract_spec_value(specs, 'Внешний вид', 'Разъем подключения подсветки')
        kit.has_lcd = self.str_to_bool(self.extract_spec_value(specs, 'Внешний вид', 'LCD дисплей', 'нет'))

        # Водоблок
        kit.block_purpose = self.extract_spec_value(specs, 'Водоблок', 'Назначение')
        kit.compatible_sockets = self.extract_spec_value(specs, 'Водоблок', 'Сокет')
        kit.block_material = self.extract_spec_value(specs, 'Водоблок', 'Материал водоблока')
        kit.block_dimensions = self.extract_spec_value(specs, 'Водоблок', 'Размеры водоблока')

        # Радиатор
        kit.radiator_size = self.extract_spec_value(specs, 'Радиатор', 'Монтажный размер радиатора')
        kit.radiator_length = self.extract_spec_value(specs, 'Радиатор', 'Длина радиатора')
        kit.radiator_width = self.extract_spec_value(specs, 'Радиатор', 'Ширина радиатора')
        kit.radiator_thickness = self.extract_spec_value(specs, 'Радиатор', 'Толщина радиатора')
        kit.radiator_material = self.extract_spec_value(specs, 'Радиатор', 'Материал радиатора')

        # Вентиляторы
        kit.fans_count = self.extract_spec_value(specs, 'Вентиляторы', 'Количество вентиляторов в комплекте')
        kit.fan_size = self.extract_spec_value(specs, 'Вентиляторы', 'Размеры вентиляторов')
        kit.fan_bearing = self.extract_spec_value(specs, 'Вентиляторы', 'Тип подшипника вентилятора')
        kit.fan_min_speed = self.extract_spec_value(specs, 'Вентиляторы', 'Минимальная скорость вращения')
        kit.fan_max_speed = self.extract_spec_value(specs, 'Вентиляторы', 'Максимальная скорость вращения')
        kit.fan_speed_control = self.extract_spec_value(specs, 'Вентиляторы', 'Регулировка скорости вращения вентилятора')
        kit.fan_min_noise = self.extract_spec_value(specs, 'Вентиляторы', 'Минимальный уровень шума')
        kit.fan_max_noise = self.extract_spec_value(specs, 'Вентиляторы', 'Максимальный уровень шума')
        kit.fan_airflow = self.extract_spec_value(specs, 'Вентиляторы', 'Максимальный воздушный поток')
        kit.fan_pressure = self.extract_spec_value(specs, 'Вентиляторы', 'Максимальное статическое давление')
        kit.fan_connector = self.extract_spec_value(specs, 'Вентиляторы', 'Разъем подключения вентиляторов')

        # Помпа
        kit.pump_speed = self.extract_spec_value(specs, 'Помпа', 'Скорость вращения помпы')
        kit.pump_connector = self.extract_spec_value(specs, 'Помпа', 'Разъем подключения помпы')

        # Трубки
        kit.tube_length = self.extract_spec_value(specs, 'Трубки', 'Длина трубок')
        kit.tube_material = self.extract_spec_value(specs, 'Трубки', 'Материал трубок')
        kit.transparent_tubes = self.str_to_bool(self.extract_spec_value(specs, 'Трубки', 'Прозрачные трубки', 'нет'))

        # Дополнительная информация
        kit.features = self.extract_spec_value(specs, 'Дополнительная информация', 'Особенности, дополнительно')
        kit.thermal_paste = self.extract_spec_value(specs, 'Дополнительная информация', 'Термопаста в комплекте')

        # Метаданные
        kit.worker_id = item.get('_worker_id', None)
        kit.url_index = item.get('_url_index', None)

        return kit

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = WaterCoolingKitDataLoader(WaterCooling, app, db)
        loader.run_interactive()
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.pc_case import PcCase
from app.extensions import db

from basedataloader import BaseDataLoader

class PcCaseDataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        case = self.model_class()

        self.common_fields(case, item)

        # Заводские данные
        case.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца / производителя')
        case.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')

        # Общие параметры
        case.type = self.extract_spec_value(specs, 'Общие параметры', 'Тип')
        case.model = self.extract_spec_value(specs, 'Общие параметры', 'Модель')
        case.manufacturer_code = self.extract_spec_value(specs, 'Общие параметры', 'Код производителя')

        # Форм-фактор и габариты
        case.case_type = self.extract_spec_value(specs, 'Форм-фактор и габариты', 'Типоразмер корпуса')
        case.motherboard_orientation = self.extract_spec_value(specs, 'Форм-фактор и габариты', 'Ориентация материнской платы')
        case.length = self.extract_spec_value(specs, 'Форм-фактор и габариты', 'Длина')
        case.width = self.extract_spec_value(specs, 'Форм-фактор и габариты', 'Ширина')
        case.height = self.extract_spec_value(specs, 'Форм-фактор и габариты', 'Высота')
        case.weight = self.extract_spec_value(specs, 'Форм-фактор и габариты', 'Вес')

        # Внешний вид
        case.color = self.extract_spec_value(specs, 'Внешний вид', 'Основной цвет')
        case.materials = self.extract_spec_value(specs, 'Внешний вид', 'Материал корпуса')
        case.window_side = self.extract_spec_value(specs, 'Внешний вид', 'Наличие окна на боковой стенке')
        case.window_material = self.extract_spec_value(specs, 'Внешний вид', 'Материал окна')
        case.front_panel_material = self.extract_spec_value(specs, 'Внешний вид', 'Материал фронтальной панели')
        case.lighting_type = self.extract_spec_value(specs, 'Внешний вид', 'Тип подсветки')
        case.lighting_color = self.extract_spec_value(specs, 'Внешний вид', 'Цвет подсветки')
        case.lighting_source = self.extract_spec_value(specs, 'Внешний вид', 'Источник подсветки')
        case.lighting_connector = self.extract_spec_value(specs, 'Внешний вид', 'Разъем подключения подсветки')
        case.lighting_control = self.extract_spec_value(specs, 'Внешний вид', 'Способ управления подсветки')

        # Совместимость
        case.motherboard_form_factors = self.extract_spec_value(specs, 'Совместимость', 'Форм-фактор совместимых плат')
        case.psu_form_factor = self.extract_spec_value(specs, 'Совместимость', 'Форм-фактор совместимых блоков питания')
        case.psu_location = self.extract_spec_value(specs, 'Совместимость', 'Размещение блока питания')
        case.max_psu_length = self.extract_spec_value(specs, 'Совместимость', 'Максимальная длина блока питания')
        case.horizontal_expansion_slots = self.extract_spec_value(specs, 'Совместимость', 'Горизонтальные слоты расширения')
        case.vertical_expansion_slots = self.extract_spec_value(specs, 'Совместимость', 'Вертикальные слоты расширения')
        case.max_gpu_length = self.extract_spec_value(specs, 'Совместимость', 'Максимальная длина устанавливаемой видеокарты')
        case.max_cpu_cooler_height = self.extract_spec_value(specs, 'Совместимость', 'Максимальная высота процессорного кулера')
        case.drive_bays_2_5 = self.extract_spec_value(specs, 'Совместимость', 'Количество отсеков 2.5\" накопителей')
        case.drive_bays_3_5_internal = self.extract_spec_value(specs, 'Совместимость', 'Число внутренних отсеков 3.5\"')
        case.drive_bays_3_5_external = self.extract_spec_value(specs, 'Совместимость', 'Число внешних отсеков 3.5\"')
        case.drive_bays_5_25 = self.extract_spec_value(specs, 'Совместимость', 'Число отсеков 5.25\"')

        # Охлаждение
        case.included_fans = self.extract_spec_value(specs, 'Охлаждение', 'Вентиляторы в комплекте')
        case.front_fan_support = self.extract_spec_value(specs, 'Охлаждение', 'Поддержка фронтальных вентиляторов')
        case.rear_fan_support = self.extract_spec_value(specs, 'Охлаждение', 'Поддержка тыловых вентиляторов')
        case.top_fan_support = self.extract_spec_value(specs, 'Охлаждение', 'Поддержка верхних вентиляторов')
        case.bottom_fan_support = self.extract_spec_value(specs, 'Охлаждение', 'Поддержка нижних вентиляторов')
        case.side_fan_support = self.extract_spec_value(specs, 'Охлаждение', 'Поддержка боковых вентиляторов')
        case.liquid_cooling_support = self.str_to_bool(self.extract_spec_value(specs, 'Охлаждение', 'Возможность установки системы жидкостного охлаждения', 'нет'))
        case.front_radiator_support = self.extract_spec_value(specs, 'Охлаждение', 'Фронтальный монтажный размер радиатора СЖО')
        case.top_radiator_support = self.extract_spec_value(specs, 'Охлаждение', 'Верхний монтажный размер радиатора СЖО')
        case.rear_radiator_support = self.extract_spec_value(specs, 'Охлаждение', 'Тыловой монтажный размер радиатора СЖО')
        case.bottom_radiator_support = self.extract_spec_value(specs, 'Охлаждение', 'Нижний монтажный размер радиатора СЖО')
        case.side_radiator_support = self.extract_spec_value(specs, 'Охлаждение', 'Боковой монтажный размер радиатора СЖО')

        # Разъемы и интерфейсы
        case.io_panel_location = self.extract_spec_value(specs, 'Разъемы и интерфейсы лицевой панели', 'Расположение I / O панели')
        case.io_ports = self.extract_spec_value(specs, 'Разъемы и интерфейсы лицевой панели', 'Разъемы')
        case.card_reader = self.str_to_bool(self.extract_spec_value(specs, 'Разъемы и интерфейсы лицевой панели', 'Встроенный кард-ридер', 'нет'))

        # Обслуживание
        case.side_panel_mount = self.extract_spec_value(specs, 'Обслуживание', 'Фиксация боковых панелей')
        case.cpu_cooler_cutout = self.str_to_bool(self.extract_spec_value(specs, 'Обслуживание', 'Вырез в районе крепления кулера CPU', 'нет'))
        case.cable_routing = self.str_to_bool(self.extract_spec_value(specs, 'Обслуживание', 'Прокладка кабелей за задней стенкой', 'нет'))
        case.dust_filter = self.str_to_bool(self.extract_spec_value(specs, 'Обслуживание', 'Пылевой фильтр', 'нет'))

        # Дополнительная информация
        case.included_psu = self.extract_spec_value(specs, 'Дополнительная информация', 'Встроенный БП')
        case.silent_features = self.str_to_bool(self.extract_spec_value(specs, 'Дополнительная информация', 'Малошумные и антивибрационные корпуса', 'нет'))
        case.package_contents = self.extract_spec_value(specs, 'Дополнительная информация', 'Комплектация')
        case.features = self.extract_spec_value(specs, 'Дополнительная информация', 'Особенности')

        # Метаданные
        case.worker_id = item.get('_worker_id', None)
        case.url_index = item.get('_url_index', None)

        return case

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = PcCaseDataLoader(PcCase, app, db)
        loader.run_interactive()
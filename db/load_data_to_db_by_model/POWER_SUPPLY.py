import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.power_supply import PowerSupply
from app.extensions import db

from basedataloader import BaseDataLoader

class PowerSupplyDataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        psu = self.model_class()

        self.common_fields(psu, item)

        # Заводские данные
        psu.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца / производителя')
        psu.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')

        # Общие параметры
        psu.type = self.extract_spec_value(specs, 'Общие параметры', 'Тип')
        psu.model = self.extract_spec_value(specs, 'Общие параметры', 'Модель')
        psu.manufacturer_model = self.extract_spec_value(specs, 'Общие параметры', 'Модель производителя')
        psu.manufacturer_code = self.extract_spec_value(specs, 'Общие параметры', 'Код производителя')
        psu.wattage = self.extract_spec_value(specs, 'Общие параметры', 'Мощность (номинал)')

        # Внешний вид
        psu.form_factor = self.extract_spec_value(specs, 'Внешний вид', 'Форм-фактор')
        psu.color = self.extract_spec_value(specs, 'Внешний вид', 'Цвет')
        psu.cable_management = self.extract_spec_value(specs, 'Внешний вид', 'Отстегивающиеся кабели')
        psu.cable_sleeving = self.str_to_bool(self.extract_spec_value(specs, 'Внешний вид', 'Оплетка проводов', 'нет'))
        psu.cable_colors = self.extract_spec_value(specs, 'Внешний вид', 'Цвета проводов')
        psu.lighting_type = self.extract_spec_value(specs, 'Внешний вид', 'Тип подсветки')
        psu.lighting_color = self.extract_spec_value(specs, 'Внешний вид', 'Цвет подсветки')
        psu.lighting_source = self.extract_spec_value(specs, 'Внешний вид', 'Источник подсветки')
        psu.lighting_connector = self.extract_spec_value(specs, 'Внешний вид', 'Тип разъема питания подсветки')

        # Кабели и разъемы
        psu.main_connector = self.extract_spec_value(specs, 'Кабели и разъемы', 'Основной разъем питания')
        psu.cpu_connectors = self.extract_spec_value(specs, 'Кабели и разъемы', 'Разъемы для питания процессора (CPU)')
        psu.pcie_connectors = self.extract_spec_value(specs, 'Кабели и разъемы', 'Разъемы для питания видеокарты (PCI-E)')
        psu.sata_connectors = self.extract_spec_value(specs, 'Кабели и разъемы', 'Количество разъемов 15-pin SATA')
        psu.molex_connectors = self.extract_spec_value(specs, 'Кабели и разъемы', 'Количество разъемов 4-pin Molex')
        psu.floppy_connector = self.str_to_bool(self.extract_spec_value(specs, 'Кабели и разъемы', 'Разъем 4 pin Floppy', 'нет'))
        psu.cable_length_main = self.extract_spec_value(specs, 'Кабели и разъемы', 'Длина основного кабеля питания')
        psu.cable_length_cpu = self.extract_spec_value(specs, 'Кабели и разъемы', 'Длина кабеля питания процессора')
        psu.cable_length_pcie = self.extract_spec_value(specs, 'Кабели и разъемы', 'Длина кабеля питания PCI-E')
        psu.cable_length_sata = self.extract_spec_value(specs, 'Кабели и разъемы', 'Длина кабеля питания SATA')
        psu.cable_length_molex = self.extract_spec_value(specs, 'Кабели и разъемы', 'Длина кабеля питания Molex')

        # Электрические параметры
        psu.power_12v = self.extract_spec_value(specs, 'Электрические параметры', 'Мощность по линии 12 В')
        psu.current_12v = self.extract_spec_value(specs, 'Электрические параметры', 'Ток по линии +12 В')
        psu.current_3v = self.extract_spec_value(specs, 'Электрические параметры', 'Ток по линии +3.3 В')
        psu.current_5v = self.extract_spec_value(specs, 'Электрические параметры', 'Ток по линии +5 В')
        psu.current_5vsb = self.extract_spec_value(specs, 'Электрические параметры', 'Ток дежурного источника (+5 В Standby)')
        psu.current_12v_neg = self.extract_spec_value(specs, 'Электрические параметры', 'Ток по линии -12 В')
        psu.input_voltage = self.extract_spec_value(specs, 'Электрические параметры', 'Диапазон входного напряжения сети')

        # Система охлаждения
        psu.cooling_type = self.extract_spec_value(specs, 'Система охлаждения', 'Система охлаждения')
        psu.fan_size = self.extract_spec_value(specs, 'Система охлаждения', 'Размеры вентиляторов')
        psu.fan_control = self.extract_spec_value(specs, 'Система охлаждения', 'Регулировка оборотов')
        psu.hybrid_mode = self.str_to_bool(self.extract_spec_value(specs, 'Система охлаждения', 'Переключатель режима работы вентилятора (Hybrid mode)', 'нет'))
        psu.max_noise = self.extract_spec_value(specs, 'Система охлаждения', 'Максимальный уровень шума')

        # Сертификация
        psu.certification_80plus = self.extract_spec_value(specs, 'Сертификация', 'Сертификат 80 PLUS')
        psu.pfc_type = self.extract_spec_value(specs, 'Сертификация', 'Корректор коэффициента мощности (PFC)')
        psu.standards = self.extract_spec_value(specs, 'Сертификация', 'Соответствие стандартам')
        psu.protections = self.extract_spec_value(specs, 'Сертификация', 'Технологии защиты')

        # Дополнительная информация
        psu.power_cable_included = self.str_to_bool(self.extract_spec_value(specs, 'Дополнительная информация', 'Сетевой кабель в комплекте', 'нет'))
        psu.package_contents = self.extract_spec_value(specs, 'Дополнительная информация', 'Комплектация')
        psu.features = self.extract_spec_value(specs, 'Дополнительная информация', 'Особенности')

        # Габариты и вес
        psu.length = self.extract_spec_value(specs, 'Габариты и вес', 'Длина')
        psu.width = self.extract_spec_value(specs, 'Габариты и вес', 'Ширина')
        psu.height = self.extract_spec_value(specs, 'Габариты и вес', 'Высота')
        psu.weight = self.extract_spec_value(specs, 'Габариты и вес', 'Вес')

        # Метаданные
        psu.worker_id = item.get('_worker_id', None)
        psu.url_index = item.get('_url_index', None)

        return psu

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = PowerSupplyDataLoader(PowerSupply, app, db)
        loader.run_interactive()
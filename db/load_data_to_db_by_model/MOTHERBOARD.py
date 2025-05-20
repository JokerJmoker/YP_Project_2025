import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.motherboard import Motherboard
from app.extensions import db

from basedataloader import BaseDataLoader

class MotherboardDataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        mb = self.model_class()

        self.common_fields(mb, item)

        # Заводские данные
        mb.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца / производителя')
        mb.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')

        # Общие параметры
        mb.type = self.extract_spec_value(specs, 'Общие параметры', 'Тип')
        mb.model = self.extract_spec_value(specs, 'Общие параметры', 'Модель')
        mb.series = self.extract_spec_value(specs, 'Общие параметры', 'Серия')
        mb.color = self.extract_spec_value(specs, 'Общие параметры', 'Цвет')
        mb.release_year = self.extract_spec_value(specs, 'Общие параметры', 'Год релиза')

        # Форм-фактор и размеры
        mb.form_factor = self.extract_spec_value(specs, 'Форм-фактор и размеры', 'Форм-фактор')
        mb.height = self.extract_spec_value(specs, 'Форм-фактор и размеры', 'Высота')
        mb.width = self.extract_spec_value(specs, 'Форм-фактор и размеры', 'Ширина')

        # Процессор и чипсет
        mb.socket = self.extract_spec_value(specs, 'Процессор и чипсет', 'Сокет')
        mb.chipset = self.extract_spec_value(specs, 'Процессор и чипсет', 'Чипсет Intel')
        mb.compatible_cpus = self.extract_spec_value(specs, 'Процессор и чипсет', 'Совместимые ядра процессоров Intel')

        # Память
        mb.memory_type = self.extract_spec_value(specs, 'Память', 'Тип поддерживаемой памяти')
        mb.memory_form_factor = self.extract_spec_value(specs, 'Память', 'Форм-фактор поддерживаемой памяти')
        mb.memory_slots = self.extract_spec_value(specs, 'Память', 'Количество слотов памяти')
        mb.memory_channels = self.extract_spec_value(specs, 'Память', 'Количество каналов памяти')
        mb.max_memory = self.extract_spec_value(specs, 'Память', 'Максимальный объем памяти')
        mb.base_memory_freq = self.extract_spec_value(specs, 'Память', 'Максимальная частота памяти (JEDEC / без разгона)')
        mb.oc_memory_freq = self.extract_spec_value(specs, 'Память', 'Частота оперативной памяти в разгоне')

        # Слоты расширения
        mb.pcie_version = self.extract_spec_value(specs, 'Слоты расширения', 'Версия PCI Express')
        mb.pcie_x16_slots = self.extract_spec_value(specs, 'Слоты расширения', 'Слоты PCIe x16')
        mb.sli_crossfire = self.extract_spec_value(specs, 'Слоты расширения', 'Поддержка SLI / CrossFire')
        mb.sli_crossfire_count = self.extract_spec_value(specs, 'Слоты расширения', 'Количество карт в SLI / Crossfire')
        mb.pcie_x1_slots = self.extract_spec_value(specs, 'Слоты расширения', 'Количество слотов PCI-E x1')

        # Контроллеры накопителей
        mb.nvme_support = self.str_to_bool(self.extract_spec_value(specs, 'Контроллеры накопителей', 'Поддержка NVMe', 'нет'))
        mb.nvme_pcie_version = self.extract_spec_value(specs, 'Контроллеры накопителей', 'Версия PCI Express накопителей')
        mb.m2_slots = self.extract_spec_value(specs, 'Контроллеры накопителей', 'Количество разъемов M.2')
        mb.m2_cpu_slots = self.extract_spec_value(specs, 'Контроллеры накопителей', 'Разъемы M.2 (M), PCIe линии процессора')
        mb.m2_chipset_slots = self.extract_spec_value(specs, 'Контроллеры накопителей', 'Разъемы M.2 (M), PCIe линии чипсета')
        mb.sata_ports = self.extract_spec_value(specs, 'Контроллеры накопителей', 'Количество портов SATA')
        mb.sata_raid = self.extract_spec_value(specs, 'Контроллеры накопителей', 'Режим работы SATA RAID')
        mb.nvme_raid = self.extract_spec_value(specs, 'Контроллеры накопителей', 'Режим работы NVMe RAID')
        mb.other_storage = self.extract_spec_value(specs, 'Контроллеры накопителей', 'Другие разъемы накопителей')

        # Порты на задней панели
        mb.usb_a_ports = self.extract_spec_value(specs, 'Порты на задней панели', 'Порты USB Type-A')
        mb.usb_c_ports = self.extract_spec_value(specs, 'Порты на задней панели', 'Порты USB Type-C')
        mb.video_outputs = self.extract_spec_value(specs, 'Порты на задней панели', 'Видеовыходы')
        mb.lan_ports = self.extract_spec_value(specs, 'Порты на задней панели', 'Количество сетевых портов (RJ-45)')
        mb.audio_ports = self.extract_spec_value(specs, 'Порты на задней панели', 'Количество аналоговых аудиоразъемов')
        mb.spdif = self.extract_spec_value(specs, 'Порты на задней панели', 'Цифровые аудиопорты (S / PDIF)')
        mb.wifi_antennas = self.str_to_bool(self.extract_spec_value(specs, 'Порты на задней панели', 'Разъемы SMA (для антенны Wi-Fi)', 'нет'))
        mb.ps2_ports = self.extract_spec_value(specs, 'Порты на задней панели', 'Порты PS / 2')

        # Разъемы на плате
        mb.internal_usb_a = self.extract_spec_value(specs, 'Разъемы на плате', 'Внутренние USB Type-A разъемы')
        mb.internal_usb_c = self.extract_spec_value(specs, 'Разъемы на плате', 'Внутренные USB Type-C разъемы')
        mb.cpu_fan_headers = self.extract_spec_value(specs, 'Разъемы на плате', 'Разъемы питания процессорного охлаждения')
        mb.case_fan_4pin = self.extract_spec_value(specs, 'Разъемы на плате', 'Разъемы для корпусных вентиляторов (4 pin)')
        mb.aio_pump_headers = self.extract_spec_value(specs, 'Разъемы на плате', 'Совмещенные разъемы для вентиляторов и помпы СЖО (4 pin)')
        mb.case_fan_3pin = self.extract_spec_value(specs, 'Разъемы на плате', 'Разъемы для корпусных вентиляторов (3 pin)')
        mb.argb_headers = self.extract_spec_value(specs, 'Разъемы на плате', 'Разъемы 5V-D-G (3 pin) для ARGB подсветки')
        mb.rgb_headers = self.extract_spec_value(specs, 'Разъемы на плате', 'Разъемы 12V-G-R-B (4 pin) для RGB подсветки')
        mb.wifi_m2 = self.str_to_bool(self.extract_spec_value(specs, 'Разъемы на плате', 'Разъем M.2 (E) для модулей беспроводной связи', 'нет'))
        mb.com_ports = self.extract_spec_value(specs, 'Разъемы на плате', 'Разъем RS-232 (COM)')
        mb.lpt_ports = self.extract_spec_value(specs, 'Разъемы на плате', 'Интерфейс LPT')

        # Аудио
        mb.audio_scheme = self.extract_spec_value(specs, 'Аудио', 'Звуковая схема')
        mb.audio_chipset = self.extract_spec_value(specs, 'Аудио', 'Чипсет звукового адаптера')

        # Сеть
        mb.lan_speed = self.extract_spec_value(specs, 'Сеть', 'Скорость сетевого адаптера')
        mb.lan_chipsets = self.extract_spec_value(specs, 'Сеть', 'Сетевой адаптер')
        mb.wifi_standard = self.extract_spec_value(specs, 'Сеть', 'Стандарт Wi-Fi')
        mb.bluetooth = self.extract_spec_value(specs, 'Сеть', 'Версия Bluetooth')
        mb.wifi_chipset = self.extract_spec_value(specs, 'Сеть', 'Адаптер беспроводной связи')

        # Питание и охлаждение
        mb.main_power = self.extract_spec_value(specs, 'Питание и охлаждение', 'Основной разъем питания')
        mb.cpu_power = self.extract_spec_value(specs, 'Питание и охлаждение', 'Разъем питания процессора')
        mb.power_phases = self.extract_spec_value(specs, 'Питание и охлаждение', 'Количество фаз питания')
        mb.passive_cooling = self.extract_spec_value(specs, 'Питание и охлаждение', 'Пассивное охлаждение')
        mb.active_cooling = self.extract_spec_value(specs, 'Питание и охлаждение', 'Активное охлаждение')

        # Дополнительная информация
        mb.onboard_buttons = self.extract_spec_value(specs, 'Дополнительная информация', 'Кнопки на плате')
        mb.lighting = self.str_to_bool(self.extract_spec_value(specs, 'Дополнительная информация', 'Подсветка элементов платы', 'нет'))
        mb.lighting_software = self.extract_spec_value(specs, 'Дополнительная информация', 'ПО для синхронизации подсветки')
        mb.pcb_layers = self.extract_spec_value(specs, 'Дополнительная информация', 'Количество слоев печатной платы')
        mb.smartphone_app = self.extract_spec_value(specs, 'Дополнительная информация', 'Приложение для взаимодействия со смартфоном')
        mb.features = self.extract_spec_value(specs, 'Дополнительная информация', 'Особенности, дополнительно')
        mb.package_contents = self.extract_spec_value(specs, 'Дополнительная информация', 'Комплектация')

        # Габариты упаковки
        mb.box_length = self.extract_spec_value(specs, 'Габариты и вес в упаковке', 'Длина коробки')
        mb.box_width = self.extract_spec_value(specs, 'Габариты и вес в упаковке', 'Ширина коробки')
        mb.box_height = self.extract_spec_value(specs, 'Габариты и вес в упаковке', 'Высота коробки')
        mb.box_weight = self.extract_spec_value(specs, 'Габариты и вес в упаковке', 'Вес с коробкой')

        # Метаданные
        mb.worker_id = item.get('_worker_id', None)
        mb.url_index = item.get('_url_index', None)

        return mb

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = MotherboardDataLoader(Motherboard, app, db)
        loader.run_interactive()
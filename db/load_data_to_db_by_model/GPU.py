import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.gpu import Gpu
from app.extensions import db

from basedataloader import BaseDataLoader

class GPUDataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        gpu = self.model_class()

        self.common_fields(gpu, item)

        # Заводские данные
        gpu.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца / производителя')
        gpu.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')

        # Общие параметры
        gpu.type = self.extract_spec_value(specs, 'Общие параметры', 'Тип')
        gpu.model = self.extract_spec_value(specs, 'Общие параметры', 'Модель')
        gpu.manufacturer_code = self.extract_spec_value(specs, 'Общие параметры', 'Код производителя')
        gpu.color = self.extract_spec_value(specs, 'Общие параметры', 'Цвет')
        gpu.mining = self.str_to_bool(self.extract_spec_value(specs, 'Общие параметры', 'Предназначена для майнинга (добыча криптовалют)', 'нет'))
        gpu.lhr = self.str_to_bool(self.extract_spec_value(specs, 'Общие параметры', 'LHR', 'нет'))

        # Основные параметры
        gpu.gpu_model = self.extract_spec_value(specs, 'Основные параметры', 'Графический процессор')
        gpu.architecture = self.extract_spec_value(specs, 'Основные параметры', 'Микроархитектура')
        gpu.process_tech = self.extract_spec_value(specs, 'Основные параметры', 'Техпроцесс')

        # Спецификации видеопроцессора
        gpu.base_clock = self.extract_spec_value(specs, 'Спецификации видеопроцессора', 'Штатная частота работы видеочипа')
        gpu.boost_clock = self.extract_spec_value(specs, 'Спецификации видеопроцессора', 'Турбочастота')
        gpu.cuda_cores = self.extract_spec_value(specs, 'Спецификации видеопроцессора', 'Количество универсальных процессоров (ALU)')
        gpu.texture_units = self.extract_spec_value(specs, 'Спецификации видеопроцессора', 'Число текстурных блоков')
        gpu.raster_units = self.extract_spec_value(specs, 'Спецификации видеопроцессора', 'Число блоков растеризации')
        gpu.ray_tracing = self.str_to_bool(self.extract_spec_value(specs, 'Спецификации видеопроцессора', 'Поддержка трассировки лучей', 'нет'))
        gpu.rt_cores = self.extract_spec_value(specs, 'Спецификации видеопроцессора', 'Аппаратное ускорение трассировки лучей (RT-ядра)')
        gpu.tensor_cores = self.extract_spec_value(specs, 'Спецификации видеопроцессора', 'Тензорные ядра')

        # Спецификации видеопамяти
        gpu.vram_size = self.extract_spec_value(specs, 'Спецификации видеопамяти', 'Объем видеопамяти')
        gpu.vram_type = self.extract_spec_value(specs, 'Спецификации видеопамяти', 'Тип памяти')
        gpu.bus_width = self.extract_spec_value(specs, 'Спецификации видеопамяти', 'Разрядность шины памяти')
        gpu.memory_bandwidth = self.extract_spec_value(specs, 'Спецификации видеопамяти', 'Максимальная пропускная способность памяти')
        gpu.memory_clock = self.extract_spec_value(specs, 'Спецификации видеопамяти', 'Эффективная частота памяти')

        # Вывод изображения
        gpu.video_outputs = self.extract_spec_value(specs, 'Вывод изображения', 'Тип и количество видеоразъемов')
        gpu.hdmi_version = self.extract_spec_value(specs, 'Вывод изображения', 'Версия HDMI')
        gpu.dp_version = self.extract_spec_value(specs, 'Вывод изображения', 'Версия DisplayPort')
        gpu.max_displays = self.extract_spec_value(specs, 'Вывод изображения', 'Количество подключаемых одновременно мониторов')
        gpu.max_resolution = self.extract_spec_value(specs, 'Вывод изображения', 'Максимальное разрешение')

        # Подключение
        gpu.interface = self.extract_spec_value(specs, 'Подключение', 'Интерфейс подключения')
        gpu.slot_width = self.extract_spec_value(specs, 'Подключение', 'Форм-фактор разъема подключения')
        gpu.pcie_lanes = self.extract_spec_value(specs, 'Подключение', 'Количество линий PCI Express')
        gpu.power_connectors = self.extract_spec_value(specs, 'Подключение', 'Разъемы дополнительного питания')
        gpu.recommended_psu = self.extract_spec_value(specs, 'Подключение', 'Рекомендуемый блок питания')
        gpu.tdp = self.extract_spec_value(specs, 'Подключение', 'Потребляемая мощность')

        # Система охлаждения
        gpu.cooling_type = self.extract_spec_value(specs, 'Система охлаждения', 'Тип охлаждения')
        gpu.fans = self.extract_spec_value(specs, 'Система охлаждения', 'Тип и количество установленных вентиляторов')
        gpu.liquid_cooling = self.str_to_bool(self.extract_spec_value(specs, 'Система охлаждения', 'Радиатор жидкостного охлаждения', 'нет'))

        # Дополнительная информация
        gpu.lighting = self.str_to_bool(self.extract_spec_value(specs, 'Дополнительная информация', 'Подсветка элементов видеокарты', 'нет'))
        gpu.lighting_sync = self.extract_spec_value(specs, 'Дополнительная информация', 'Синхронизация RGB подсветки')
        gpu.lcd_display = self.str_to_bool(self.extract_spec_value(specs, 'Дополнительная информация', 'LCD дисплей', 'нет'))
        gpu.bios_switch = self.str_to_bool(self.extract_spec_value(specs, 'Дополнительная информация', 'Переключатель BIOS', 'нет'))
        gpu.features = self.extract_spec_value(specs, 'Дополнительная информация', 'Особенности, дополнительно')
        gpu.package_contents = self.extract_spec_value(specs, 'Дополнительная информация', 'Комплектация')

        # Габариты и вес
        gpu.low_profile = self.str_to_bool(self.extract_spec_value(specs, 'Габариты и вес', 'Низкопрофильная карта (Low Profile)', 'нет'))
        gpu.slots = self.extract_spec_value(specs, 'Габариты и вес', 'Количество занимаемых слотов расширения')
        gpu.length = self.extract_spec_value(specs, 'Габариты и вес', 'Длина видеокарты')
        gpu.width = self.extract_spec_value(specs, 'Габариты и вес', 'Ширина видеокарты')
        gpu.thickness = self.extract_spec_value(specs, 'Габариты и вес', 'Толщина видеокарты')
        gpu.weight = self.extract_spec_value(specs, 'Габариты и вес', 'Вес')

        # Метаданные
        gpu.worker_id = item.get('_worker_id', None)
        gpu.url_index = item.get('_url_index', None)

        return gpu

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = GPUDataLoader(Gpu, app, db)
        loader.run_interactive()
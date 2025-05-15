import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models.cpu import Cpu
from app.extensions import db

from basedataloader import BaseDataLoader  # файл с вашим классом BaseDataLoader

class CpuDataLoader(BaseDataLoader):
    def create_instance(self, item):
        specs = item.get('specs', {})

        cpu = self.model_class()

        self.populate_common_fields(cpu, item)

        cpu.warranty = self.extract_spec_value(specs, 'Заводские данные', 'Гарантия продавца')
        cpu.country = self.extract_spec_value(specs, 'Заводские данные', 'Страна-производитель')
        cpu.model = self.extract_spec_value(specs, 'Общие параметры', 'Модель')
        cpu.socket = self.extract_spec_value(specs, 'Общие параметры', 'Сокет')
        cpu.manufacturer_code = self.extract_spec_value(specs, 'Общие параметры', 'Код производителя')
        cpu.release_year = self.extract_spec_value(specs, 'Общие параметры', 'Год релиза')
        cpu.cooler_included = not self.str_to_bool(self.extract_spec_value(specs, 'Общие параметры', 'Система охлаждения в комплекте', 'нет'))
        cpu.thermal_interface_included = not self.str_to_bool(self.extract_spec_value(specs, 'Общие параметры', 'Термоинтерфейс в комплекте', 'нет'))

        cpu.total_cores = self.extract_spec_value(specs, 'Ядро и архитектура', 'Общее количество ядер')
        cpu.performance_cores = self.extract_spec_value(specs, 'Ядро и архитектура', 'Количество производительных ядер')
        cpu.efficiency_cores = self.extract_spec_value(specs, 'Ядро и архитектура', 'Количество энергоэффективных ядер')
        cpu.max_threads = self.extract_spec_value(specs, 'Ядро и архитектура', 'Максимальное число потоков')
        cpu.l2_cache = self.extract_spec_value(specs, 'Ядро и архитектура', 'Объем кэша L2')
        cpu.l3_cache = self.extract_spec_value(specs, 'Ядро и архитектура', 'Объем кэша L3')
        cpu.process_technology = self.extract_spec_value(specs, 'Ядро и архитектура', 'Техпроцесс')
        cpu.core_architecture = self.extract_spec_value(specs, 'Ядро и архитектура', 'Ядро')

        cpu.base_frequency = self.extract_spec_value(specs, 'Частота и возможность разгона', 'Базовая частота процессора')
        cpu.turbo_frequency = self.extract_spec_value(specs, 'Частота и возможность разгона', 'Максимальная частота в турбо режиме')
        cpu.base_efficiency_frequency = self.extract_spec_value(specs, 'Частота и возможность разгона', 'Базовая частота энергоэффективных ядер')
        cpu.turbo_efficiency_frequency = self.extract_spec_value(specs, 'Частота и возможность разгона', 'Частота в турбо режиме энергоэффективных ядер')
        cpu.unlocked_multiplier = self.str_to_bool(self.extract_spec_value(specs, 'Частота и возможность разгона', 'Свободный множитель', 'нет'))

        cpu.memory_type = self.extract_spec_value(specs, 'Параметры оперативной памяти', 'Тип памяти')
        cpu.max_memory = self.extract_spec_value(specs, 'Параметры оперативной памяти', 'Максимально поддерживаемый объем памяти')
        cpu.memory_channels = self.extract_spec_value(specs, 'Параметры оперативной памяти', 'Количество каналов')
        cpu.memory_frequency = self.extract_spec_value(specs, 'Параметры оперативной памяти', 'Частота оперативной памяти')
        cpu.ecc_support = self.str_to_bool(self.extract_spec_value(specs, 'Параметры оперативной памяти', 'Поддержка режима ECC', 'нет'))

        cpu.tdp = self.extract_spec_value(specs, 'Тепловые характеристики', 'Тепловыделение (TDP)')
        cpu.base_tdp = self.extract_spec_value(specs, 'Тепловые характеристики', 'Базовое тепловыделение')
        cpu.max_temperature = self.extract_spec_value(specs, 'Тепловые характеристики', 'Максимальная температура процессора')

        cpu.integrated_graphics = self.str_to_bool(self.extract_spec_value(specs, 'Графическое ядро', 'Интегрированное графическое ядро', 'нет'))
        cpu.gpu_model = self.extract_spec_value(specs, 'Графическое ядро', 'Модель графического процессора')
        cpu.gpu_frequency = self.extract_spec_value(specs, 'Графическое ядро', 'Максимальная частота графического ядра')
        cpu.execution_units = self.extract_spec_value(specs, 'Графическое ядро', 'Исполнительные блоки')
        cpu.shading_units = self.extract_spec_value(specs, 'Графическое ядро', 'Потоковые процессоры (Shading Units)')

        cpu.pci_express = self.extract_spec_value(specs, 'Шина и контроллеры', 'Встроенный контроллер PCI Express')
        cpu.pci_lanes = self.extract_spec_value(specs, 'Шина и контроллеры', 'Число линий PCI Express')

        cpu.virtualization = self.str_to_bool(self.extract_spec_value(specs, 'Дополнительная информация', 'Технология виртуализации', 'нет'))
        cpu.features = self.extract_spec_value(specs, 'Дополнительная информация', 'Особенности, дополнительно')

        return cpu


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        loader = CpuDataLoader(Cpu, app, db)
        loader.run_interactive()

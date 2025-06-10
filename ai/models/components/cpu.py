from pydantic import BaseModel
from typing import Optional
from utils.parsers import parse_float, parse_int, parse_bool


class CpuModel(BaseModel):
    id: int
    name: str
    price: int  # в рублях
    
    # Основные параметры совместимости
    socket: str                      # Сокет процессора (например, "LGA1700", "AM5")
    tdp: Optional[int] = None        # Теплопакет (Вт)
    base_tdp: Optional[int] = None   # Базовый теплопакет (Вт)
    cooler_included: Optional[bool] = None  # Входит ли кулер в комплект
    
    # Ядерная архитектура
    total_cores: Optional[int] = None        # Общее количество ядер
    performance_cores: Optional[int] = None  # Производительные ядра (для гибридных)
    efficiency_cores: Optional[int] = None   # Энергоэффективные ядра (для гибридных)
    max_threads: Optional[int] = None        # Макс. количество потоков
    
    # Частоты
    base_frequency: Optional[float] = None   # Базовая частота (ГГц)
    turbo_frequency: Optional[float] = None  # Турбо частота (ГГц)
    unlocked_multiplier: Optional[bool] = None  # Разблокированный множитель
    
    # Память
    memory_type: Optional[str] = None        # Тип памяти (DDR4, DDR5)
    max_memory: Optional[int] = None         # Макс. объем памяти (ГБ)
    memory_channels: Optional[int] = None    # Количество каналов
    memory_frequency: Optional[int] = None   # Частота памяти (МГц)
    
    # Графика
    integrated_graphics: Optional[bool] = None  # Наличие встроенной графики
    gpu_model: Optional[str] = None          # Модель встроенного GPU
    
    # PCI Express
    pci_express: Optional[str] = None        # Версия PCIe
    pci_lanes: Optional[int] = None          # Количество линий PCIe
    
    # Оценка бенчмарка
    benchmark_rate: Optional[float] = None 
    
    @classmethod
    def from_orm(cls, cpu_orm):
        return cls(
            id=cpu_orm.id,
            name=cpu_orm.name,
            price=int(cpu_orm.price.replace(' ', '').replace('₽', '')) if cpu_orm.price else 0,
            socket=cpu_orm.socket,
            tdp=parse_int(cpu_orm.tdp),
            base_tdp=parse_int(cpu_orm.base_tdp),
            cooler_included=parse_bool(cpu_orm.cooler_included),
            total_cores=parse_int(cpu_orm.total_cores),
            performance_cores=parse_int(cpu_orm.performance_cores),
            efficiency_cores=parse_int(cpu_orm.efficiency_cores),
            max_threads=parse_int(cpu_orm.max_threads),
            base_frequency=parse_float(cpu_orm.base_frequency),
            turbo_frequency=parse_float(cpu_orm.turbo_frequency),
            unlocked_multiplier=parse_bool(cpu_orm.unlocked_multiplier),
            memory_type=cpu_orm.memory_type,
            max_memory=parse_int(cpu_orm.max_memory),
            memory_channels=parse_int(cpu_orm.memory_channels),
            memory_frequency=parse_int(cpu_orm.memory_frequency),
            integrated_graphics=parse_bool(cpu_orm.integrated_graphics),
            gpu_model=cpu_orm.gpu_model,
            pci_express=cpu_orm.pci_express,
            pci_lanes=parse_int(cpu_orm.pci_lanes),
            benchmark_rate=parse_float(cpu_orm.benchmark_rate)
        )
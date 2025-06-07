from pydantic import BaseModel
from typing import Optional


class Hdd35Model(BaseModel):
    id: int
    name: str
    price: int  # цена в целочисленном формате (рубли)

    capacity: Optional[int] = None          # объем в ГБ
    cache_size: Optional[int] = None        # объем кэша в МБ
    rotation_speed: Optional[int] = None    # скорость вращения шпинделя, об/мин
    max_data_rate: Optional[str] = None     # макс. скорость передачи данных, например "6 Гбит/с"
    latency: Optional[float] = None         # время задержки, мс
    interface: Optional[str] = None         # интерфейс подключения (SATA, SAS и т.п.)
    interface_speed: Optional[str] = None   # пропускная способность интерфейса

    raid_optimized: Optional[bool] = None   # оптимизация под RAID

    recording_tech: Optional[str] = None    # технология записи
    shock_resistance: Optional[str] = None  # ударостойкость
    noise_operation: Optional[float] = None # уровень шума в работе, дБ
    noise_idle: Optional[float] = None      # уровень шума в простое, дБ
    helium_filled: Optional[bool] = None    # гелиевое наполнение

    load_cycles: Optional[int] = None       # циклы позиционирования

    max_power: Optional[float] = None       # макс. энергопотребление, Вт
    idle_power: Optional[float] = None      # энергопотребление в режиме ожидания, Вт

    min_temp: Optional[float] = None        # мин. рабочая температура, °C
    max_temp: Optional[float] = None        # макс. рабочая температура, °C

    features: Optional[str] = None           # дополнительные особенности

    width: Optional[int] = None              # ширина, мм
    length: Optional[int] = None             # длина, мм
    thickness: Optional[int] = None          # толщина, мм
    weight: Optional[float] = None           # вес, граммы

    @classmethod
    def from_orm(cls, orm_obj):
        def parse_int(value):
            try:
                return int(''.join(filter(str.isdigit, value))) if value else None
            except:
                return None

        def parse_float(value):
            try:
                cleaned = value.replace(',', '.').strip() if value else None
                if cleaned:
                    # Отбрасываем нечисловые символы в конце, если есть
                    num_str = ''.join(ch for ch in cleaned if ch.isdigit() or ch == '.')
                    return float(num_str) if num_str else None
                return None
            except:
                return None

        return cls(
            id=orm_obj.id,
            name=orm_obj.name,
            price=int(orm_obj.price.replace(' ', '').replace('₽', '')) if orm_obj.price else 0,

            capacity=parse_int(orm_obj.capacity),
            cache_size=parse_int(orm_obj.cache_size),
            rotation_speed=parse_int(orm_obj.rotation_speed),
            max_data_rate=orm_obj.max_data_rate,
            latency=parse_float(orm_obj.latency),
            interface=orm_obj.interface,
            interface_speed=orm_obj.interface_speed,

            raid_optimized=orm_obj.raid_optimized,

            recording_tech=orm_obj.recording_tech,
            shock_resistance=orm_obj.shock_resistance,
            noise_operation=parse_float(orm_obj.noise_operation),
            noise_idle=parse_float(orm_obj.noise_idle),
            helium_filled=orm_obj.helium_filled,

            load_cycles=parse_int(orm_obj.load_cycles),

            max_power=parse_float(orm_obj.max_power),
            idle_power=parse_float(orm_obj.idle_power),

            min_temp=parse_float(orm_obj.min_temp),
            max_temp=parse_float(orm_obj.max_temp),

            features=orm_obj.features,

            width=parse_int(orm_obj.width),
            length=parse_int(orm_obj.length),
            thickness=parse_int(orm_obj.thickness),
            weight=parse_float(orm_obj.weight),
        )

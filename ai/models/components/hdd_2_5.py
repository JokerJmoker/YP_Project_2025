from pydantic import BaseModel
from typing import Optional
from parsers import parse_float, parse_int


class Hdd25Model(BaseModel):
    id: int
    name: str
    price: int  # в рублях

    capacity: Optional[int] = None            # ГБ
    interface: Optional[str] = None
    rotation_speed: Optional[int] = None      # об/мин
    buffer_size: Optional[int] = None         # МБ
    data_transfer_rate: Optional[str] = None  # строка, например "6 Гбит/с"
    seek_time: Optional[float] = None         # мс

    width: Optional[int] = None                # мм
    length: Optional[int] = None               # мм
    thickness: Optional[int] = None            # мм
    weight: Optional[float] = None             # граммы

    max_power: Optional[float] = None          # Вт
    idle_power: Optional[float] = None         # Вт
    noise_operation: Optional[float] = None    # дБ
    noise_idle: Optional[float] = None         # дБ

    @classmethod
    def from_orm(cls, hdd_orm):
        def parse_dimension(value: Optional[str]) -> Optional[int]:
            if not value:
                return None
            digits = ''.join(filter(str.isdigit, value))
            return int(digits) if digits else None

        return cls(
            id=hdd_orm.id,
            name=hdd_orm.name,
            price=int(hdd_orm.price.replace(' ', '').replace('₽', '')) if hdd_orm.price else 0,
            capacity=parse_int(hdd_orm.capacity),
            interface=hdd_orm.interface,
            rotation_speed=parse_int(hdd_orm.rotation_speed),
            buffer_size=parse_int(hdd_orm.buffer_size),
            data_transfer_rate=hdd_orm.data_transfer_rate,
            seek_time=parse_float(hdd_orm.seek_time),
            width=parse_dimension(hdd_orm.width),
            length=parse_dimension(hdd_orm.length),
            thickness=parse_dimension(hdd_orm.thickness),
            weight=parse_float(hdd_orm.weight),
            max_power=parse_float(hdd_orm.max_power),
            idle_power=parse_float(hdd_orm.idle_power),
            noise_operation=parse_float(hdd_orm.noise_operation),
            noise_idle=parse_float(hdd_orm.noise_idle),
        )

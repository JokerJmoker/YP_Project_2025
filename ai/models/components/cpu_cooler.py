from pydantic import BaseModel
from typing import Optional
from .parsers import parse_float, parse_int

class CpuCoolerModel(BaseModel):
    id: int
    name: str
    price: int  # в рублях
    image_url: Optional[str] = None  # URL изображения

    
    # Основные параметры совместимости
    socket: str                    # Сокет процессора (например, "LGA1700", "AM5")
    tdp: Optional[int] = None      # Рассеиваемая мощность (Вт)
    type_: Optional[str] = None    # Тип кулера (башенный, низкопрофильный и т.д.)
    
    # Параметры вентилятора
    fan_size: Optional[int] = None              # мм
    fan_count: Optional[int] = None             # Количество вентиляторов
    max_rpm: Optional[int] = None               # Макс. скорость вращения (об/мин)
    min_rpm: Optional[int] = None               # Мин. скорость вращения (об/мин)
    max_noise_level: Optional[float] = None     # Макс. уровень шума (дБ)
    max_airflow: Optional[float] = None         # Макс. воздушный поток (CFM)
    
    # Габариты
    height: Optional[int] = None    # Высота кулера (мм)
    width: Optional[int] = None     # Ширина кулера (мм)
    depth: Optional[int] = None     # Глубина кулера (мм)
    
    @classmethod
    def from_orm(cls, cooler_orm):
        return cls(
            id=cooler_orm['id'],
            name=cooler_orm['name'],
            price=int(cooler_orm['price']),
            image_url=str(cooler_orm['image_url']),
            socket=cooler_orm['socket'],
            tdp=parse_int(cooler_orm['tdp']),
            type_=cooler_orm['type'],
            fan_size=parse_int(cooler_orm['fan_size']),
            fan_count=parse_int(cooler_orm['fan_count']),
            max_rpm=parse_int(cooler_orm['max_rpm']),
            min_rpm=parse_int(cooler_orm['min_rpm']),
            max_noise_level=parse_float(cooler_orm['max_noise_level']),
            max_airflow=parse_float(cooler_orm['max_airflow']),
            height=parse_int(cooler_orm['height']),
            width=parse_int(cooler_orm['width']),
            depth=parse_int(cooler_orm['depth'])
        )

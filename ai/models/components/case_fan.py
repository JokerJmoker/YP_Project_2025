from pydantic import BaseModel
from typing import Optional
from parsers import parse_float, parse_int


class CaseFanModel(BaseModel):
    id: int
    name: str
    price: int  # в рублях

    fan_size: Optional[int] = None              # мм
    fan_thickness: Optional[int] = None         # мм
    max_rotation_speed: Optional[int] = None    # об/мин
    min_rotation_speed: Optional[int] = None    # об/мин
    max_airflow: Optional[float] = None         # CFM
    max_static_pressure: Optional[float] = None # mmH2O
    max_noise_level: Optional[float] = None     # дБА
    min_noise_level: Optional[float] = None     # дБА
    power_connector_type: Optional[str] = None

    @classmethod
    def from_orm(cls, fan_orm):
        return cls(
            id=fan_orm.id,
            name=fan_orm.name,
            price=int(fan_orm.price.replace(' ', '').replace('₽', '')) if fan_orm.price else 0,
            fan_size=parse_int(fan_orm.fan_size),
            fan_thickness=parse_int(fan_orm.fan_thickness),
            max_rotation_speed=parse_int(fan_orm.max_rotation_speed),
            min_rotation_speed=parse_int(fan_orm.min_rotation_speed),
            max_airflow=parse_float(fan_orm.max_airflow),
            max_static_pressure=parse_float(fan_orm.max_static_pressure),
            max_noise_level=parse_float(fan_orm.max_noise_level),
            min_noise_level=parse_float(fan_orm.min_noise_level),
            power_connector_type=fan_orm.power_connector_type
        )

from pydantic import BaseModel
from typing import Optional
from .parsers import parse_bool, parse_int, parse_float


class WaterCoolingModel(BaseModel):
    id: int
    name: str
    price: int
    compatible_sockets: str
    fan_airflow: Optional[float] = None
    radiator_size: Optional[str] = None
    fans_count: Optional[int] = None
    fan_max_noise: Optional[float] = None
    pump_speed: Optional[int] = None
    fan_max_speed: Optional[int] = None
    tube_length: Optional[int] = None

    @classmethod
    def from_orm(cls, wc_orm):
        return cls(
            id=wc_orm['id'],
            name=wc_orm['name'],
            price=int(wc_orm['price']),
            compatible_sockets=wc_orm['compatible_sockets'],
            fan_airflow=parse_float(wc_orm.get('fan_airflow')),
            radiator_size=wc_orm.get('radiator_size'),
            fans_count=parse_int(wc_orm.get('fans_count')),
            fan_max_noise=parse_float(wc_orm.get('fan_max_noise')),
            pump_speed=parse_int(wc_orm.get('pump_speed')),
            fan_max_speed=parse_int(wc_orm.get('fan_max_speed')),
            tube_length=parse_int(wc_orm.get('tube_length'))
        )
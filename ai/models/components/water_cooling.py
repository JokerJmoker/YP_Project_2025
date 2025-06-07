from pydantic import BaseModel
from typing import Optional
from utils.parsers import parse_bool, parse_int, parse_float


class WaterCoolingModel(BaseModel):
    id: int
    name: str
    price: str

    # Внешний вид и освещение
    color: Optional[str]
    lighting_type: Optional[str]
    lighting_source: Optional[str]
    lighting_connector: Optional[str]
    has_lcd: Optional[bool]

    # Водоблок — совместимость и материалы
    block_purpose: Optional[str]
    compatible_sockets: Optional[str]
    block_material: Optional[str]
    block_dimensions: Optional[str]

    # Радиатор — размер и материал
    radiator_size: Optional[str]
    radiator_length: Optional[str]
    radiator_width: Optional[str]
    radiator_thickness: Optional[str]
    radiator_material: Optional[str]

    # Вентиляторы — количество и производительность
    fans_count: Optional[int]
    fan_size: Optional[str]
    fan_bearing: Optional[str]
    fan_min_speed: Optional[int]
    fan_max_speed: Optional[int]
    fan_speed_control: Optional[str]
    fan_min_noise: Optional[float]
    fan_max_noise: Optional[float]
    fan_airflow: Optional[str]
    fan_pressure: Optional[str]
    fan_connector: Optional[str]

    # Помпа — скорость и тип подключения
    pump_speed: Optional[int]
    pump_connector: Optional[str]

    # Трубки — длина, материал, прозрачность
    tube_length: Optional[str]
    tube_material: Optional[str]
    transparent_tubes: Optional[bool]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, wc_orm):
        return cls(
            id=wc_orm.id,
            name=wc_orm.name,
            price=wc_orm.price,

            color=wc_orm.color,
            lighting_type=wc_orm.lighting_type,
            lighting_source=wc_orm.lighting_source,
            lighting_connector=wc_orm.lighting_connector,
            has_lcd=parse_bool(wc_orm.has_lcd),

            block_purpose=wc_orm.block_purpose,
            compatible_sockets=wc_orm.compatible_sockets,
            block_material=wc_orm.block_material,
            block_dimensions=wc_orm.block_dimensions,

            radiator_size=wc_orm.radiator_size,
            radiator_length=wc_orm.radiator_length,
            radiator_width=wc_orm.radiator_width,
            radiator_thickness=wc_orm.radiator_thickness,
            radiator_material=wc_orm.radiator_material,

            fans_count=parse_int(wc_orm.fans_count),
            fan_size=wc_orm.fan_size,
            fan_bearing=wc_orm.fan_bearing,
            fan_min_speed=parse_int(wc_orm.fan_min_speed),
            fan_max_speed=parse_int(wc_orm.fan_max_speed),
            fan_speed_control=wc_orm.fan_speed_control,
            fan_min_noise=parse_float(wc_orm.fan_min_noise),
            fan_max_noise=parse_float(wc_orm.fan_max_noise),
            fan_airflow=wc_orm.fan_airflow,
            fan_pressure=wc_orm.fan_pressure,
            fan_connector=wc_orm.fan_connector,

            pump_speed=parse_int(wc_orm.pump_speed),
            pump_connector=wc_orm.pump_connector,

            tube_length=wc_orm.tube_length,
            tube_material=wc_orm.tube_material,
            transparent_tubes=parse_bool(wc_orm.transparent_tubes),
        )

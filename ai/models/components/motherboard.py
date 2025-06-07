from pydantic import BaseModel
from typing import Optional

class MotherboardModel(BaseModel):
    id: int
    name: str
    price: int  # в рублях

    socket: str
    form_factor: Optional[str] = None
    height: Optional[int] = None  # мм
    width: Optional[int] = None   # мм

    memory_type: Optional[str] = None
    memory_slots: Optional[int] = None
    max_memory: Optional[int] = None  # в ГБ
    memory_channels: Optional[int] = None

    pcie_version: Optional[str] = None
    pcie_x16_slots: Optional[int] = None

    m2_slots: Optional[int] = None
    sata_ports: Optional[int] = None
    nvme_support: Optional[bool] = False

    cpu_fan_headers: Optional[int] = None
    case_fan_4pin: Optional[int] = None
    case_fan_3pin: Optional[int] = None
    aio_pump_headers: Optional[int] = None

    lighting: Optional[bool] = False

    release_year: Optional[int] = None

    features: Optional[str] = None

    @classmethod
    def from_orm(cls, mb_orm):
        def parse_int_or_none(value):
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        
        def parse_bool(value):
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', 'yes', '1')
            return False

        return cls(
            id=mb_orm.id,
            name=mb_orm.name,
            price=int(mb_orm.price.replace(' ', '').replace('₽', '')) if mb_orm.price else 0,

            socket=mb_orm.socket,
            form_factor=mb_orm.form_factor,
            height=parse_int_or_none(mb_orm.height),
            width=parse_int_or_none(mb_orm.width),

            memory_type=mb_orm.memory_type,
            memory_slots=parse_int_or_none(mb_orm.memory_slots),
            max_memory=parse_int_or_none(mb_orm.max_memory),
            memory_channels=parse_int_or_none(mb_orm.memory_channels),

            pcie_version=mb_orm.pcie_version,
            pcie_x16_slots=parse_int_or_none(mb_orm.pcie_x16_slots),

            m2_slots=parse_int_or_none(mb_orm.m2_slots),
            sata_ports=parse_int_or_none(mb_orm.sata_ports),
            nvme_support=bool(mb_orm.nvme_support),

            cpu_fan_headers=parse_int_or_none(mb_orm.cpu_fan_headers),
            case_fan_4pin=parse_int_or_none(mb_orm.case_fan_4pin),
            case_fan_3pin=parse_int_or_none(mb_orm.case_fan_3pin),
            aio_pump_headers=parse_int_or_none(mb_orm.aio_pump_headers),

            lighting=parse_bool(mb_orm.lighting),
            release_year=parse_int_or_none(mb_orm.release_year),

            features=mb_orm.features,
        )

from pydantic import BaseModel
from typing import Optional
from .parsers import (
    parse_int,
    parse_bool,
    parse_memory_frequency,
    parse_str_list,
    extract_pcie_version,
    extract_number
)

class MotherboardModel(BaseModel):
    id: int
    name: str
    price: int
    image_url: Optional[str] = None  # URL изображения

    socket: str
    chipset: Optional[str] = None
    power_phases: Optional[int] = None

    form_factor: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None

    memory_type: Optional[str] = None
    memory_slots: Optional[int] = None
    memory_channels: Optional[int] = None
    max_memory: Optional[int] = None
    base_memory_freq: Optional[int] = None
    oc_memory_freq: Optional[list[int]] = None
    memory_form_factor: Optional[str] = None

    pcie_version: Optional[float] = None  # Обновлён тип
    pcie_x16_slots: Optional[int] = None
    sli_crossfire: Optional[bool] = None
    sli_crossfire_count: Optional[int] = None

    nvme_support: Optional[bool] = None
    nvme_pcie_version: Optional[float] = None  # Обновлён тип
    m2_slots: Optional[int] = None
    sata_ports: Optional[int] = None
    sata_raid: Optional[bool] = None
    nvme_raid: Optional[bool] = None

    cpu_fan_headers: Optional[int] = None
    aio_pump_headers: Optional[int] = None
    case_fan_4pin: Optional[int] = None
    case_fan_3pin: Optional[int] = None

    main_power: Optional[str] = None
    cpu_power: Optional[str] = None

    @classmethod
    def from_orm(cls, mb_orm):
        return cls(
            id=mb_orm['id'],
            name=mb_orm['name'],
            price=parse_int(mb_orm['price']),
            image_url=str(mb_orm['image_url']),
            socket=mb_orm['socket'],
            chipset=mb_orm['chipset'],
            power_phases=parse_int(mb_orm['power_phases']),
            form_factor=mb_orm['form_factor'],
            height=parse_int(mb_orm['height']),
            width=parse_int(mb_orm['width']),
            memory_type=mb_orm['memory_type'],
            memory_slots=parse_int(mb_orm['memory_slots']),
            memory_channels=parse_int(mb_orm['memory_channels']),
            max_memory=parse_int(mb_orm['max_memory']),
            base_memory_freq=parse_memory_frequency(mb_orm['base_memory_freq']),
            oc_memory_freq=parse_str_list(mb_orm['oc_memory_freq']),
            memory_form_factor=mb_orm['memory_form_factor'],
            pcie_version=extract_pcie_version(mb_orm['pcie_version']),
            pcie_x16_slots=extract_number(mb_orm['pcie_x16_slots']),
            sli_crossfire=parse_bool(mb_orm['sli_crossfire']),
            sli_crossfire_count=parse_int(mb_orm['sli_crossfire_count']),
            nvme_support=parse_bool(mb_orm['nvme_support']),
            nvme_pcie_version=extract_pcie_version(mb_orm['nvme_pcie_version']),
            m2_slots=parse_int(mb_orm['m2_slots']),
            sata_ports=parse_int(mb_orm['sata_ports']),
            sata_raid=parse_bool(mb_orm['sata_raid']),
            nvme_raid=parse_bool(mb_orm['nvme_raid']),
            cpu_fan_headers=parse_int(mb_orm['cpu_fan_headers']),
            aio_pump_headers=parse_int(mb_orm['aio_pump_headers']),
            case_fan_4pin=parse_int(mb_orm['case_fan_4pin']),
            case_fan_3pin=parse_int(mb_orm['case_fan_3pin']),
            main_power=mb_orm['main_power'],
            cpu_power=mb_orm['cpu_power'],
        )

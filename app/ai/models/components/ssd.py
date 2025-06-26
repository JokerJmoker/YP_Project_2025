from pydantic import BaseModel
from typing import Optional
from .parsers import parse_bool  # для булевых, если нужно

class SsdModel(BaseModel):
    id: int
    name: str
    price: str

    # Важные для совместимости и выбора характеристики
    capacity: Optional[str]
    nvme: Optional[bool]
    interface: Optional[str]
    type: Optional[str]  # например, '2.5" SATA накопитель'
    model: Optional[str]
    manufacturer_code: Optional[str]

    # Конфигурация накопителя — влияет на производительность и надежность
    controller: Optional[str]
    cell_type: Optional[str]
    memory_structure: Optional[str]
    has_dram: Optional[bool]

    # Показатели производительности
    max_read_speed: Optional[str]
    max_write_speed: Optional[str]
    random_read_iops: Optional[str]
    random_write_iops: Optional[str]

    # Надежность — может влиять на выбор
    tbw: Optional[str]
    dwpd: Optional[str]

    # Габариты — для оценки совместимости по месту установки
    width: Optional[str]
    length: Optional[str]
    thickness: Optional[str]
    weight: Optional[str]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, ssd_orm):
        return cls(
            id=ssd_orm.id,
            name=ssd_orm.name,
            price=ssd_orm.price,

            capacity=ssd_orm.capacity,
            nvme=parse_bool(ssd_orm.nvme),
            interface=ssd_orm.interface,
            type=ssd_orm.type,
            model=ssd_orm.model,
            manufacturer_code=ssd_orm.manufacturer_code,

            controller=ssd_orm.controller,
            cell_type=ssd_orm.cell_type,
            memory_structure=ssd_orm.memory_structure,
            has_dram=parse_bool(ssd_orm.has_dram),

            max_read_speed=ssd_orm.max_read_speed,
            max_write_speed=ssd_orm.max_write_speed,
            random_read_iops=ssd_orm.random_read_iops,
            random_write_iops=ssd_orm.random_write_iops,

            tbw=ssd_orm.tbw,
            dwpd=ssd_orm.dwpd,

            width=ssd_orm.width,
            length=ssd_orm.length,
            thickness=ssd_orm.thickness,
            weight=ssd_orm.weight,
        )

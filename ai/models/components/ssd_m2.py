from pydantic import BaseModel
from typing import Optional
from parsers import parse_bool


class SsdM2Model(BaseModel):
    id: int
    name: str
    price: str

    # Важные для совместимости и выбора характеристики
    capacity: Optional[str]
    form_factor: Optional[str]
    interface: Optional[str]
    m2_key: Optional[str]
    nvme: Optional[bool]

    # Конфигурация накопителя
    controller: Optional[str]          # Контроллер
    cell_type: Optional[str]           # Тип ячеек (например, TLC)
    memory_structure: Optional[str]    # Структура памяти (например, 3D NAND)
    has_dram: Optional[bool]           # Наличие DRAM буфера
    dram_size: Optional[str]           # Размер DRAM буфера

    # Основные показатели производительности
    max_read_speed: Optional[str]
    max_write_speed: Optional[str]
    random_read_iops: Optional[str]
    random_write_iops: Optional[str]

    # Габариты
    length: Optional[str]
    width: Optional[str]
    thickness: Optional[str]
    weight: Optional[str]

    # Дополнительно
    heatsink_included: Optional[bool]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, ssd_orm):
        return cls(
            id=ssd_orm.id,
            name=ssd_orm.name,
            price=ssd_orm.price,

            capacity=ssd_orm.capacity,
            form_factor=ssd_orm.form_factor,
            interface=ssd_orm.interface,
            m2_key=ssd_orm.m2_key,
            nvme=parse_bool(ssd_orm.nvme),

            controller=ssd_orm.controller,
            cell_type=ssd_orm.cell_type,
            memory_structure=ssd_orm.memory_structure,
            has_dram=parse_bool(ssd_orm.has_dram),
            dram_size=ssd_orm.dram_size,

            max_read_speed=ssd_orm.max_read_speed,
            max_write_speed=ssd_orm.max_write_speed,
            random_read_iops=ssd_orm.random_read_iops,
            random_write_iops=ssd_orm.random_write_iops,

            length=ssd_orm.length,
            width=ssd_orm.width,
            thickness=ssd_orm.thickness,
            weight=ssd_orm.weight,

            heatsink_included=parse_bool(ssd_orm.heatsink_included),
        )

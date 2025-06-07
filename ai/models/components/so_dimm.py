from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from utils.parsers import parse_bool


class SoDimmModel(BaseModel):
    id: int
    name: str
    price: str

    # Ключевые параметры для совместимости
    memory_type: Optional[str]       # Тип памяти (DDR4, DDR5 и т.д.)
    total_memory: Optional[str]      # Общий объем комплекта
    module_memory: Optional[str]     # Объем одного модуля
    module_count: Optional[str]      # Кол-во модулей
    frequency: Optional[str]          # Частота работы
    voltage: Optional[str]            # Напряжение питания
    
    # Конструктивные особенности, влияющие на совместимость
    double_sided: Optional[bool]     # Двусторонний модуль
    heatsink: Optional[bool]          # Наличие радиатора (может влиять на установку)

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, sodimm_orm):
        return cls(
            id=sodimm_orm.id,
            name=sodimm_orm.name,
            price=sodimm_orm.price,

            memory_type=sodimm_orm.memory_type,
            total_memory=sodimm_orm.total_memory,
            module_memory=sodimm_orm.module_memory,
            module_count=sodimm_orm.module_count,
            frequency=sodimm_orm.frequency,
            voltage=sodimm_orm.voltage,

            double_sided=parse_bool(sodimm_orm.double_sided),
            heatsink=parse_bool(sodimm_orm.heatsink),
        )

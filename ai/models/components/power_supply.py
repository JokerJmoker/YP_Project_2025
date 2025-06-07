from pydantic import BaseModel
from typing import Optional

class PowerSupplyModel(BaseModel):
    id: int
    name: str
    price: int  # В рублях

    wattage: Optional[int] = None  # Номинальная мощность, Вт
    form_factor: Optional[str] = None  # Форма (ATX, SFX и т.п.)

    cable_management: Optional[str] = None  # Модульность кабелей (например, "модульный", "не модульный")
    cable_sleeving: Optional[bool] = False  # Оплетка кабелей

    main_connector: Optional[str] = None  # Основной разъем (обычно 24-pin)
    cpu_connectors: Optional[str] = None  # Разъемы питания процессора (например, "1x4+4-pin")
    pcie_connectors: Optional[str] = None  # Разъемы питания видеокарт (например, "2x6+2-pin")
    sata_connectors: Optional[int] = None  # Кол-во SATA разъемов
    molex_connectors: Optional[int] = None  # Кол-во Molex разъемов
    floppy_connector: Optional[bool] = False  # Наличие разъема floppy

    cooling_type: Optional[str] = None  # Тип охлаждения (активное, пассивное)
    fan_size: Optional[int] = None  # Размер вентилятора, мм
    hybrid_mode: Optional[bool] = False  # Наличие гибридного режима работы вентилятора

    certification_80plus: Optional[str] = None  # Сертификация эффективности (например, "80 Plus Gold")
    pfc_type: Optional[str] = None  # Тип PFC (Active, Passive)

    length: Optional[int] = None  # Длина блока питания, мм
    width: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[float] = None  # Вес, кг

    @classmethod
    def from_orm(cls, ps_orm):
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

        def parse_float_or_none(value):
            try:
                return float(value.replace(',', '.'))
            except (ValueError, AttributeError, TypeError):
                return None

        return cls(
            id=ps_orm.id,
            name=ps_orm.name,
            price=int(ps_orm.price.replace(' ', '').replace('₽', '')) if ps_orm.price else 0,

            wattage=parse_int_or_none(ps_orm.wattage),
            form_factor=ps_orm.form_factor,

            cable_management=ps_orm.cable_management,
            cable_sleeving=parse_bool(ps_orm.cable_sleeving),

            main_connector=ps_orm.main_connector,
            cpu_connectors=ps_orm.cpu_connectors,
            pcie_connectors=ps_orm.pcie_connectors,
            sata_connectors=parse_int_or_none(ps_orm.sata_connectors),
            molex_connectors=parse_int_or_none(ps_orm.molex_connectors),
            floppy_connector=parse_bool(ps_orm.floppy_connector),

            cooling_type=ps_orm.cooling_type,
            fan_size=parse_int_or_none(ps_orm.fan_size),
            hybrid_mode=parse_bool(ps_orm.hybrid_mode),

            certification_80plus=ps_orm.certification_80plus,
            pfc_type=ps_orm.pfc_type,

            length=parse_int_or_none(ps_orm.length),
            width=parse_int_or_none(ps_orm.width),
            height=parse_int_or_none(ps_orm.height),
            weight=parse_float_or_none(ps_orm.weight),
        )

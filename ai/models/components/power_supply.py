from pydantic import BaseModel
from typing import Optional
from .parsers import (
    parse_int,
    parse_bool,
    parse_float,
    extract_number
)

class PowerSupplyModel(BaseModel):
    id: int
    name: str
    price: int

    wattage: Optional[int] = None
    form_factor: Optional[str] = None

    cable_management: Optional[str] = None
    cable_sleeving: Optional[bool] = None

    main_connector: Optional[str] = None
    cpu_connectors: Optional[str] = None
    pcie_connectors: Optional[str] = None
    sata_connectors: Optional[int] = None
    molex_connectors: Optional[int] = None
    floppy_connector: Optional[bool] = None

    cooling_type: Optional[str] = None
    fan_size: Optional[int] = None
    hybrid_mode: Optional[bool] = None

    certification_80plus: Optional[str] = None
    pfc_type: Optional[str] = None

    length: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[float] = None

    @classmethod
    def from_orm(cls, ps_orm):
        return cls(
            id=ps_orm['id'],
            name=ps_orm['name'],
            price=parse_int(ps_orm['price']),
            
            wattage=parse_int(ps_orm.get('wattage')),
            form_factor=ps_orm.get('form_factor'),
            
            cable_management=ps_orm.get('cable_management'),
            cable_sleeving=parse_bool(ps_orm.get('cable_sleeving')),
            
            main_connector=ps_orm.get('main_connector'),
            cpu_connectors=ps_orm.get('cpu_connectors'),
            pcie_connectors=ps_orm.get('pcie_connectors'),
            sata_connectors=parse_int(ps_orm.get('sata_connectors')),
            molex_connectors=parse_int(ps_orm.get('molex_connectors')),
            floppy_connector=parse_bool(ps_orm.get('floppy_connector')),
            
            cooling_type=ps_orm.get('cooling_type'),
            fan_size=parse_int(ps_orm.get('fan_size')),
            hybrid_mode=parse_bool(ps_orm.get('hybrid_mode')),
            
            certification_80plus=ps_orm.get('certification_80plus'),
            pfc_type=ps_orm.get('pfc_type'),
            
            length=parse_int(ps_orm.get('length')),
            width=parse_int(ps_orm.get('width')),
            height=parse_int(ps_orm.get('height')),
            weight=parse_float(ps_orm.get('weight')),
        )
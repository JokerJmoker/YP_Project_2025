from pydantic import BaseModel
from typing import Optional
from .parsers import parse_float, parse_int, parse_bool


class DimmModel(BaseModel):
    id: int
    name: str
    price: int  # in rubles

    # Critical compatibility parameters
    memory_type: str                   # DDR4, DDR5, etc.
    module_type: str                   # DIMM, SODIMM
    total_memory: Optional[int] = None
    modules_count: Optional[int] = None
    frequency: Optional[int] = None
    ecc_memory: bool                   # ECC support
    registered_memory: bool            # Registered/buffered memory

    # Performance parameters
    cas_latency: Optional[int] = None  # CL timing
    ras_to_cas_delay: Optional[int] = None  # tRCD
    row_precharge_delay: Optional[int] = None  # tRP
    activate_to_precharge_delay: Optional[int] = None  # tRAS
    voltage: Optional[float] = None    # Operating voltage

    # Overclocking profiles
    intel_xmp: Optional[str] = None    # XMP profile support
    amd_expo: Optional[str] = None     # EXPO profile support

    # Physical dimensions
    height: Optional[int] = None       # Module height in mm
    low_profile: Optional[bool] = None # Low-profile module

    @classmethod
    def from_orm(cls, dimm_orm):
        return cls(
            id=dimm_orm['id'],
            name=dimm_orm['name'],
            price=int(dimm_orm['price']),
            memory_type=dimm_orm['memory_type'],
            module_type=dimm_orm['module_type'],
            total_memory=parse_int(dimm_orm.get('total_memory', '').replace('ГБ', '').strip()) or None,
            modules_count=parse_int(dimm_orm.get('modules_count', '').replace('шт', '').strip()) or None,
            frequency=parse_int(dimm_orm.get('frequency', '').replace('МГц', '').strip()) or None,
            ecc_memory=parse_bool(dimm_orm.get('ecc_memory')),
            registered_memory=parse_bool(dimm_orm.get('registered_memory')),
            cas_latency=parse_int(dimm_orm.get('cas_latency')),
            ras_to_cas_delay=parse_int(dimm_orm.get('ras_to_cas_delay')),
            row_precharge_delay=parse_int(dimm_orm.get('row_precharge_delay')),
            activate_to_precharge_delay=parse_int(dimm_orm.get('activate_to_precharge_delay')),
            voltage=parse_float(dimm_orm.get('voltage', '').replace('В', '').strip()) if dimm_orm.get('voltage') else None,
            intel_xmp=dimm_orm.get('intel_xmp'),
            amd_expo=dimm_orm.get('amd_expo'),
            height=parse_int(dimm_orm.get('height', '').replace('мм', '').strip()) or None,
            low_profile=parse_bool(dimm_orm.get('low_profile'))
        )

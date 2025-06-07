from pydantic import BaseModel
from typing import Optional
from utils.parsers import parse_float, parse_int, parse_bool


class DimmModel(BaseModel):
    id: int
    name: str
    price: int  # in rubles

    # Critical compatibility parameters
    memory_type: str                   # DDR4, DDR5, etc.
    module_type: str                   # DIMM, SODIMM
    total_memory: int                  # Total capacity in GB
    modules_count: int                 # Number of modules in kit
    frequency: int                     # Speed in MHz
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
            id=dimm_orm.id,
            name=dimm_orm.name,
            price=int(dimm_orm.price.replace(' ', '').replace('₽', '')) if dimm_orm.price else 0,
            memory_type=dimm_orm.memory_type,
            module_type=dimm_orm.module_type,
            total_memory=parse_int(dimm_orm.total_memory.replace('GB', '').strip()) if dimm_orm.total_memory else 0,
            modules_count=parse_int(dimm_orm.modules_count),
            frequency=parse_int(dimm_orm.frequency.replace('MHz', '').strip()) if dimm_orm.frequency else 0,
            ecc_memory=parse_bool(dimm_orm.ecc_memory),
            registered_memory=parse_bool(dimm_orm.registered_memory),
            cas_latency=parse_int(dimm_orm.cas_latency),
            ras_to_cas_delay=parse_int(dimm_orm.ras_to_cas_delay),
            row_precharge_delay=parse_int(dimm_orm.row_precharge_delay),
            activate_to_precharge_delay=parse_int(dimm_orm.activate_to_precharge_delay),
            voltage=parse_float(dimm_orm.voltage.replace('V', '').strip()) if dimm_orm.voltage else None,
            intel_xmp=dimm_orm.intel_xmp,
            amd_expo=dimm_orm.amd_expo,
            height=parse_int(dimm_orm.height.replace('mm', '').strip()) if dimm_orm.height else None,
            low_profile=parse_bool(dimm_orm.low_profile)
        )
from pydantic import BaseModel
from typing import Optional
from utils.parsers import parse_float, parse_int, parse_bool


class GpuModel(BaseModel):
    id: int
    name: str
    price: int  # in rubles

    # Critical compatibility parameters
    interface: str                     # PCIe version (e.g. "PCIe 4.0 x16")
    slot_width: str                    # Slot size (e.g. "Dual-slot")
    length: Optional[int] = None       # Length in mm
    tdp: Optional[int] = None          # Power consumption in watts
    power_connectors: Optional[str] = None  # Required power connectors

    # GPU specifications
    gpu_model: str                     # GPU model name (e.g. "RTX 4080")
    architecture: Optional[str] = None # Architecture (e.g. "Ada Lovelace")
    vram_size: Optional[int] = None    # VRAM in GB
    vram_type: Optional[str] = None    # GDDR6X, GDDR6, etc.
    bus_width: Optional[int] = None    # Memory bus width in bits

    # Performance parameters
    base_clock: Optional[int] = None   # Base clock in MHz
    boost_clock: Optional[int] = None  # Boost clock in MHz
    cuda_cores: Optional[int] = None   # CUDA cores/Stream processors
    ray_tracing: Optional[bool] = None # RT support
    tensor_cores: Optional[int] = None # Tensor cores

    # Output capabilities
    video_outputs: Optional[str] = None # Available ports
    max_resolution: Optional[str] = None # Max supported resolution
    
    # Оценка бенчмарка
    benchmark_rate: Optional[float] = None 

    @classmethod
    def from_orm(cls, gpu_orm):
        def parse_gpu_size(size_str):
            if size_str and 'mm' in size_str:
                return parse_int(size_str.replace('mm', '').strip())
            return None

        return cls(
            id=gpu_orm.id,
            name=gpu_orm.name,
            price=int(gpu_orm.price.replace(' ', '').replace('₽', '')) if gpu_orm.price else 0,
            interface=gpu_orm.interface,
            slot_width=gpu_orm.slot_width,
            length=parse_gpu_size(gpu_orm.length),
            tdp=parse_int(gpu_orm.tdp.replace('W', '').strip()) if gpu_orm.tdp else None,
            power_connectors=gpu_orm.power_connectors,
            gpu_model=gpu_orm.gpu_model,
            architecture=gpu_orm.architecture,
            vram_size=parse_int(gpu_orm.vram_size.replace('GB', '').strip()) if gpu_orm.vram_size else None,
            vram_type=gpu_orm.vram_type,
            bus_width=parse_int(gpu_orm.bus_width.replace('bit', '').strip()) if gpu_orm.bus_width else None,
            base_clock=parse_int(gpu_orm.base_clock.replace('MHz', '').strip()) if gpu_orm.base_clock else None,
            boost_clock=parse_int(gpu_orm.boost_clock.replace('MHz', '').strip()) if gpu_orm.boost_clock else None,
            cuda_cores=parse_int(gpu_orm.cuda_cores),
            ray_tracing=parse_bool(gpu_orm.ray_tracing),
            tensor_cores=parse_int(gpu_orm.tensor_cores),
            video_outputs=gpu_orm.video_outputs,
            max_resolution=gpu_orm.max_resolution,
            benchmark_rate=parse_float(gpu_orm.benchmark_rate)
        )
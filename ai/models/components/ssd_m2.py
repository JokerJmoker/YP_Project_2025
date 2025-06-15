from pydantic import BaseModel
from typing import Optional
from .parsers import parse_bool, parse_int, parse_iops, parse_speed

class SsdM2Model(BaseModel):
    id: int
    name: str
    price: int  # Было str, теперь int
    image_url: Optional[str] = None  # URL изображения

    capacity: Optional[str]
    form_factor: Optional[str]
    interface: Optional[str]
    m2_key: Optional[str]
    nvme: Optional[bool]

    controller: Optional[str]
    cell_type: Optional[str]
    memory_structure: Optional[str]
    has_dram: Optional[bool]
    dram_size: Optional[str]

    max_read_speed: Optional[int] = None   # в Мбайт/сек
    max_write_speed: Optional[int] = None  # в Мбайт/сек
    random_read_iops: Optional[int] = None
    random_write_iops: Optional[int] = None

    length: Optional[int]
    width: Optional[int]
    thickness: Optional[int]
    weight: Optional[int]

    heatsink_included: Optional[bool]

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, ssd_orm):
        return cls(
            id=parse_int(ssd_orm['id']),
            name=ssd_orm['name'],
            price=parse_int(ssd_orm['price']),
            image_url=str(ssd_orm['image_url']),
            capacity=None if not ssd_orm.get('capacity') else ssd_orm['capacity'].replace('ГБ', '').strip(),
            form_factor=ssd_orm.get('form_factor'),
            interface=ssd_orm.get('interface'),
            m2_key=ssd_orm.get('m2_key'),
            nvme=parse_bool(ssd_orm.get('nvme')),
            controller=ssd_orm.get('controller'),
            cell_type=ssd_orm.get('cell_type'),
            memory_structure=ssd_orm.get('memory_structure'),
            has_dram=parse_bool(ssd_orm.get('has_dram')),
            dram_size=ssd_orm.get('dram_size'),
            max_read_speed=parse_speed(ssd_orm.get('max_read_speed')),
            max_write_speed=parse_speed(ssd_orm.get('max_write_speed')),
            random_read_iops=parse_iops(ssd_orm.get('random_read_iops')),
            random_write_iops=parse_iops(ssd_orm.get('random_write_iops')),
            length=parse_int(str(ssd_orm.get('length', '')).replace('mm', '').strip()),
            width=parse_int(str(ssd_orm.get('width', '')).replace('mm', '').strip()),
            thickness=parse_int(str(ssd_orm.get('thickness', '')).replace('mm', '').strip()),
            weight=parse_int(str(ssd_orm.get('weight', '')).replace('g', '').strip()),
            heatsink_included=parse_bool(ssd_orm.get('heatsink_included'))
        )

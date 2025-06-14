from pydantic import BaseModel
from typing import Optional
from .parsers import parse_int, parse_bool


from pydantic import BaseModel, validator
from typing import Optional, List
import re

class PcCaseModel(BaseModel):
    id: int
    name: str
    price: Optional[int] = None

    # Форм-фактор и габариты (мм)
    case_type: Optional[str] = None
    length: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    weight: Optional[int] = None

    motherboard_form_factors: Optional[str] = None
    psu_form_factor: Optional[str] = None
    max_psu_length: Optional[int] = None
    max_gpu_length: Optional[int] = None
    max_cpu_cooler_height: Optional[int] = None

    # Отсеки для накопителей
    drive_bays_2_5: Optional[int] = None
    drive_bays_3_5_internal: Optional[int] = None
    drive_bays_3_5_external: Optional[int] = None
    drive_bays_5_25: Optional[int] = None

    # Охлаждение
    included_fans: Optional[int] = None
    front_fan_support: Optional[List[int]] = None
    rear_fan_support: Optional[List[int]] = None
    top_fan_support: Optional[List[int]] = None
    bottom_fan_support: Optional[List[int]] = None
    side_fan_support: Optional[List[int]] = None

    liquid_cooling_support: Optional[bool] = None
    front_radiator_support: Optional[List[int]] = None
    top_radiator_support: Optional[List[int]] = None
    rear_radiator_support: Optional[List[int]] = None
    bottom_radiator_support: Optional[List[int]] = None
    side_radiator_support: Optional[List[int]] = None

    # Дополнительные функции
    cpu_cooler_cutout: Optional[bool] = None
    cable_routing: Optional[bool] = None
    dust_filter: Optional[bool] = None
    side_panel_mount: Optional[str] = None

    @classmethod
    def from_orm(cls, case_orm):
        def parse_sizes(size_str: Optional[str]) -> Optional[List[int]]:
            if not size_str:
                return None
            sizes = []
            for part in size_str.split(','):
                match = re.search(r'(\d+)', part.strip())
                if match:
                    sizes.append(int(match.group(1)))
            return sizes if sizes else None

        return cls(
            id=case_orm['id'],
            name=case_orm['name'],
            price=parse_int(case_orm.get('price')),
            
            case_type=case_orm.get('case_type'),
            length=parse_int(case_orm.get('length')),
            width=parse_int(case_orm.get('width')),
            height=parse_int(case_orm.get('height')),
            weight=parse_int(case_orm.get('weight')),
            
            motherboard_form_factors=case_orm.get('motherboard_form_factors'),
            psu_form_factor=case_orm.get('psu_form_factor'),
            max_psu_length=parse_int(case_orm.get('max_psu_length')),
            max_gpu_length=parse_int(case_orm.get('max_gpu_length')),
            max_cpu_cooler_height=parse_int(case_orm.get('max_cpu_cooler_height')),
            
            drive_bays_2_5=parse_int(case_orm.get('drive_bays_2_5')),
            drive_bays_3_5_internal=parse_int(case_orm.get('drive_bays_3_5_internal')),
            drive_bays_3_5_external=parse_int(case_orm.get('drive_bays_3_5_external')),
            drive_bays_5_25=parse_int(case_orm.get('drive_bays_5_25')),
            
            included_fans=parse_int(case_orm.get('included_fans')),
            front_fan_support=parse_sizes(case_orm.get('front_fan_support')),
            rear_fan_support=parse_sizes(case_orm.get('rear_fan_support')),
            top_fan_support=parse_sizes(case_orm.get('top_fan_support')),
            bottom_fan_support=parse_sizes(case_orm.get('bottom_fan_support')),
            side_fan_support=parse_sizes(case_orm.get('side_fan_support')),
            
            liquid_cooling_support=parse_bool(case_orm.get('liquid_cooling_support')),
            front_radiator_support=parse_sizes(case_orm.get('front_radiator_support')),
            top_radiator_support=parse_sizes(case_orm.get('top_radiator_support')),
            rear_radiator_support=parse_sizes(case_orm.get('rear_radiator_support')),
            bottom_radiator_support=parse_sizes(case_orm.get('bottom_radiator_support')),
            side_radiator_support=parse_sizes(case_orm.get('side_radiator_support')),
            
            cpu_cooler_cutout=parse_bool(case_orm.get('cpu_cooler_cutout')),
            cable_routing=parse_bool(case_orm.get('cable_routing')),
            dust_filter=parse_bool(case_orm.get('dust_filter')),
            side_panel_mount=case_orm.get('side_panel_mount')
        )

    def supports_fan_size(self, size: int, tolerance: int = 10) -> bool:
        """Проверяет, поддерживает ли корпус вентиляторы указанного размера с допуском"""
        fan_positions = [
            self.front_fan_support,
            self.rear_fan_support,
            self.top_fan_support,
            self.bottom_fan_support,
            self.side_fan_support
        ]
        
        for position in fan_positions:
            if not position:
                continue
            
            for supported_size in position:
                if abs(supported_size - size) <= tolerance:
                    return True
        return False

    def supports_radiator_size(self, size: int) -> bool:
        """Проверяет, поддерживает ли корпус радиатор указанного размера"""
        radiator_positions = [
            self.front_radiator_support,
            self.top_radiator_support,
            self.rear_radiator_support,
            self.bottom_radiator_support,
            self.side_radiator_support
        ]
        
        for position in radiator_positions:
            if position and size in position:
                return True
        return False
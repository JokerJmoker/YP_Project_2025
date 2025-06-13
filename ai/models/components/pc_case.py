from pydantic import BaseModel
from typing import Optional
from parsers import parse_int, parse_bool


class PcCaseModel(BaseModel):
    id: int
    name: str
    price: Optional[int]  # цена в рублях

    # Форм-фактор и габариты (мм)
    case_type: Optional[str]
    length: Optional[int]
    width: Optional[int]
    height: Optional[int]
    weight: Optional[int]

    motherboard_form_factors: Optional[str]  # список форм-факторов в строке
    psu_form_factor: Optional[str]
    max_psu_length: Optional[int]
    max_gpu_length: Optional[int]
    max_cpu_cooler_height: Optional[int]

    horizontal_expansion_slots: Optional[int]
    vertical_expansion_slots: Optional[int]

    # Отсеки для накопителей (кол-во)
    drive_bays_2_5: Optional[int]  # преобразуем к int
    drive_bays_3_5_internal: Optional[int]
    drive_bays_3_5_external: Optional[int]
    drive_bays_5_25: Optional[int]

    # Охлаждение
    included_fans: Optional[int]
    front_fan_support: Optional[str]
    rear_fan_support: Optional[str]
    top_fan_support: Optional[str]
    bottom_fan_support: Optional[str]
    side_fan_support: Optional[str]

    liquid_cooling_support: Optional[bool]
    front_radiator_support: Optional[str]
    top_radiator_support: Optional[str]
    rear_radiator_support: Optional[str]
    bottom_radiator_support: Optional[str]
    side_radiator_support: Optional[str]

    cpu_cooler_cutout: Optional[bool]

    # Обслуживание и удобство
    cable_routing: Optional[bool]
    dust_filter: Optional[bool]
    side_panel_mount: Optional[str]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, case_orm):
        return cls(
            id=case_orm.id,
            name=case_orm.name,
            price=parse_int(case_orm.price),
            case_type=case_orm.case_type,
            length=parse_int(case_orm.length),
            width=parse_int(case_orm.width),
            height=parse_int(case_orm.height),
            weight=parse_int(case_orm.weight),
            motherboard_form_factors=case_orm.motherboard_form_factors,
            psu_form_factor=case_orm.psu_form_factor,
            max_psu_length=parse_int(case_orm.max_psu_length),
            max_gpu_length=parse_int(case_orm.max_gpu_length),
            max_cpu_cooler_height=parse_int(case_orm.max_cpu_cooler_height),
            horizontal_expansion_slots=parse_int(case_orm.horizontal_expansion_slots),
            vertical_expansion_slots=parse_int(case_orm.vertical_expansion_slots),
            drive_bays_2_5=parse_int(case_orm.drive_bays_2_5),
            drive_bays_3_5_internal=parse_int(case_orm.drive_bays_3_5_internal),
            drive_bays_3_5_external=parse_int(case_orm.drive_bays_3_5_external),
            drive_bays_5_25=parse_int(case_orm.drive_bays_5_25),
            included_fans=parse_int(case_orm.included_fans),
            front_fan_support=case_orm.front_fan_support,
            rear_fan_support=case_orm.rear_fan_support,
            top_fan_support=case_orm.top_fan_support,
            bottom_fan_support=case_orm.bottom_fan_support,
            side_fan_support=case_orm.side_fan_support,
            liquid_cooling_support=parse_bool(case_orm.liquid_cooling_support),
            front_radiator_support=case_orm.front_radiator_support,
            top_radiator_support=case_orm.top_radiator_support,
            rear_radiator_support=case_orm.rear_radiator_support,
            bottom_radiator_support=case_orm.bottom_radiator_support,
            side_radiator_support=case_orm.side_radiator_support,
            cpu_cooler_cutout=parse_bool(case_orm.cpu_cooler_cutout),
            cable_routing=parse_bool(case_orm.cable_routing),
            dust_filter=parse_bool(case_orm.dust_filter),
            side_panel_mount=case_orm.side_panel_mount
        )

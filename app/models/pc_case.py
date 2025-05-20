from datetime import datetime
from app.extensions import db

class PcCase(db.Model):
    __table_args__ = {'schema': 'pc_components'}
    __tablename__ = 'pc_case'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(350), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)

    # Заводские данные
    warranty = db.Column(db.String(100))
    country = db.Column(db.String(300))

    # Общие параметры
    type = db.Column(db.String(100))  # "корпус"
    model = db.Column(db.String(300))
    manufacturer_code = db.Column(db.String(300))

    # Форм-фактор и габариты
    case_type = db.Column(db.String(100))  # Full-Tower, Mid-Tower и т.д.
    motherboard_orientation = db.Column(db.String(200))
    length = db.Column(db.String(50))
    width = db.Column(db.String(50))
    height = db.Column(db.String(50))
    weight = db.Column(db.String(50))

    # Внешний вид
    color = db.Column(db.String(200))
    materials = db.Column(db.String(300))
    window_side = db.Column(db.String(100))
    window_material = db.Column(db.String(200))
    front_panel_material = db.Column(db.String(300))
    lighting_type = db.Column(db.String(100))
    lighting_color = db.Column(db.String(100))
    lighting_source = db.Column(db.String(200))
    lighting_connector = db.Column(db.String(200))
    lighting_control = db.Column(db.String(500))

    # Совместимость
    motherboard_form_factors = db.Column(db.String(300))
    psu_form_factor = db.Column(db.String(100))
    psu_location = db.Column(db.String(100))
    max_psu_length = db.Column(db.String(50))
    horizontal_expansion_slots = db.Column(db.String(50))
    vertical_expansion_slots = db.Column(db.String(50))
    max_gpu_length = db.Column(db.String(50))
    max_cpu_cooler_height = db.Column(db.String(50))
    drive_bays_2_5 = db.Column(db.String(100))
    drive_bays_3_5_internal = db.Column(db.String(100))
    drive_bays_3_5_external = db.Column(db.String(100))
    drive_bays_5_25 = db.Column(db.String(100))

    # Охлаждение
    included_fans = db.Column(db.String(300))
    front_fan_support = db.Column(db.String(300))
    rear_fan_support = db.Column(db.String(300))
    top_fan_support = db.Column(db.String(200))
    bottom_fan_support = db.Column(db.String(200))
    side_fan_support = db.Column(db.String(200))
    liquid_cooling_support = db.Column(db.Boolean)
    front_radiator_support = db.Column(db.String(300))
    top_radiator_support = db.Column(db.String(200))
    rear_radiator_support = db.Column(db.String(300))
    bottom_radiator_support = db.Column(db.String(200))
    side_radiator_support = db.Column(db.String(300))

    # Разъемы и интерфейсы
    io_panel_location = db.Column(db.String(100))
    io_ports = db.Column(db.String(500))
    card_reader = db.Column(db.Boolean)

    # Обслуживание
    side_panel_mount = db.Column(db.String(200))
    cpu_cooler_cutout = db.Column(db.Boolean)
    cable_routing = db.Column(db.Boolean)
    dust_filter = db.Column(db.Boolean)

    # Дополнительная информация
    included_psu = db.Column(db.String(100))
    silent_features = db.Column(db.Boolean)
    package_contents = db.Column(db.String(1000))
    features = db.Column(db.String(1000))

    # Метаданные
    worker_id = db.Column(db.Integer)
    url_index = db.Column(db.Integer)

    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
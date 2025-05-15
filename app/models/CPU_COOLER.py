from datetime import datetime
from app.extensions import db

class CpuCooler(db.Model):
    __tablename__ = 'CPU_COOLER'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)

    # Заводские данные
    warranty = db.Column(db.String(50))
    country = db.Column(db.String(100))

    # Общие параметры
    type_ = db.Column('type', db.String(100))  # Кулер для процессора
    model = db.Column(db.String(150))
    manufacturer_code = db.Column(db.String(100))
    socket = db.Column(db.String(250))
    tdp = db.Column(db.String(50))  # Рассеиваемая мощность
    design_type = db.Column(db.String(100))  # Тип конструкции

    # Радиатор
    base_material = db.Column(db.String(100))
    heatsink_material = db.Column(db.String(100))
    heatpipe_count = db.Column(db.String(20))
    heatpipe_diameter = db.Column(db.String(20))
    nickel_coating = db.Column(db.String(100))
    heatsink_color = db.Column(db.String(50))

    # Вентилятор
    fan_count = db.Column(db.String(20))
    fan_max_count = db.Column(db.String(20))
    fan_size = db.Column(db.String(50))
    fan_color = db.Column(db.String(50))
    fan_connector = db.Column(db.String(50))
    max_rpm = db.Column(db.String(50))
    min_rpm = db.Column(db.String(50))
    pwm_control = db.Column(db.String(100))
    max_airflow = db.Column(db.String(50))
    max_static_pressure = db.Column(db.String(50))
    max_noise_level = db.Column(db.String(50))
    rated_current = db.Column(db.String(50))
    rated_voltage = db.Column(db.String(50))
    bearing_type = db.Column(db.String(100))

    # Дополнительная информация
    thermal_paste_included = db.Column(db.String(100))
    lighting_type = db.Column(db.String(100))
    lighting_connector = db.Column(db.String(100))
    lighting_source = db.Column(db.String(100))
    extra_info = db.Column(db.String(250))
    package_contents = db.Column(db.String(250))

    # Габариты и вес
    height = db.Column(db.String(50))
    width = db.Column(db.String(50))
    depth = db.Column(db.String(50))
    weight = db.Column(db.String(50))

    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

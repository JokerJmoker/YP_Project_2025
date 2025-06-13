from datetime import datetime
from app.extensions import db

class WaterCooling(db.Model):
    __table_args__ = {'schema': 'pc_components'}
    __tablename__ = 'water_cooling'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(400), nullable=False)  # Увеличен размер для длинных названий
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

    # Заводские данные
    warranty = db.Column(db.String(100))
    country = db.Column(db.String(300))

    # Классификация
    type = db.Column(db.String(200))  # "комплект для сборки СЖО"
    model = db.Column(db.String(300))
    manufacturer_code = db.Column(db.String(300))
    serviceable = db.Column(db.Boolean)  # Обслуживаемая СЖО

    # Внешний вид
    color = db.Column(db.String(100))
    lighting_type = db.Column(db.String(100))
    lighting_source = db.Column(db.String(300))
    lighting_connector = db.Column(db.String(100))
    has_lcd = db.Column(db.Boolean)  # Наличие LCD дисплея

    # Водоблок
    block_purpose = db.Column(db.String(100))  # Назначение
    compatible_sockets = db.Column(db.String(500))
    block_material = db.Column(db.String(100))
    block_dimensions = db.Column(db.String(200))

    # Радиатор
    radiator_size = db.Column(db.String(100))
    radiator_length = db.Column(db.String(50))
    radiator_width = db.Column(db.String(50))
    radiator_thickness = db.Column(db.String(50))
    radiator_material = db.Column(db.String(100))

    # Вентиляторы
    fans_count = db.Column(db.String(50))
    fan_size = db.Column(db.String(100))
    fan_bearing = db.Column(db.String(200))
    fan_min_speed = db.Column(db.String(100))
    fan_max_speed = db.Column(db.String(100))
    fan_speed_control = db.Column(db.String(200))
    fan_min_noise = db.Column(db.String(100))
    fan_max_noise = db.Column(db.String(100))
    fan_airflow = db.Column(db.String(100))
    fan_pressure = db.Column(db.String(100))
    fan_connector = db.Column(db.String(100))

    # Помпа
    pump_speed = db.Column(db.String(100))
    pump_connector = db.Column(db.String(100))

    # Трубки
    tube_length = db.Column(db.String(100))
    tube_material = db.Column(db.String(100))
    transparent_tubes = db.Column(db.Boolean)

    # Дополнительная информация
    features = db.Column(db.String(1000))
    thermal_paste = db.Column(db.String(200))  # Наличие термопасты

    # Метаданные
    worker_id = db.Column(db.Integer)
    url_index = db.Column(db.Integer)

    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
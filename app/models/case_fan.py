from datetime import datetime
from app.extensions import db

class CaseFan(db.Model):
    __table_args__ = {'schema': 'pc_components'}
    __tablename__ = 'case_fan' 
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    
    # Заводские данные
    warranty = db.Column(db.String(50))
    country = db.Column(db.String(255))
    
    # Общие параметры
    type = db.Column(db.String(255))  # "вентилятор"
    model = db.Column(db.String(255))
    manufacturer_code = db.Column(db.String(255))
    fans_count = db.Column(db.String(10))  # Количество вентиляторов в комплекте
    
    # Внешний вид
    frame_color = db.Column(db.String(50))
    impeller_color = db.Column(db.String(50))
    lighting_type = db.Column(db.String(50))  # Тип подсветки
    lighting_source = db.Column(db.String(255))
    
    # Конструкция
    fan_size = db.Column(db.String(50))  # Размер вентилятора
    fan_thickness = db.Column(db.String(50))  # Толщина вентилятора
    bearing_type = db.Column(db.String(255))
    anti_vibration_pad = db.Column(db.Boolean)
    
    # Технические характеристики
    max_rotation_speed = db.Column(db.String(50))
    min_rotation_speed = db.Column(db.String(50))
    max_airflow = db.Column(db.String(50))  # Воздушный поток на максимальной скорости
    max_static_pressure = db.Column(db.String(50))
    max_noise_level = db.Column(db.String(50))
    min_noise_level = db.Column(db.String(50))
    
    # Питание и подключение
    power_connector_type = db.Column(db.String(255))
    rpm_control = db.Column(db.String(50))  # Регулировка оборотов
    nominal_voltage = db.Column(db.String(50))
    max_current = db.Column(db.String(50))
    lighting_power_connector_type = db.Column(db.String(50))
    adapters_included = db.Column(db.String(50))  # Переходники в комплекте
    hub_controller_included = db.Column(db.String(50))  # Хаб-контроллер в комплекте
    remote_control_included = db.Column(db.String(50))  # ПДУ в комплекте
    
    # Дополнительная информация
    additional_info = db.Column(db.String(500))
    package_contents = db.Column(db.String(500))
    
    # Метаданные
    worker_id = db.Column(db.Integer)
    url_index = db.Column(db.Integer)
    
    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
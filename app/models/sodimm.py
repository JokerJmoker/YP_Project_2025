from datetime import datetime
from app.extensions import db

class SoDimm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    
    # Заводские данные
    warranty = db.Column(db.String(50))
    country = db.Column(db.String(100))
    
    # Общие параметры
    type = db.Column(db.String(100))
    model = db.Column(db.String(100))
    manufacturer_code = db.Column(db.String(100))
    color = db.Column(db.String(50))
    
    # Объем и состав комплекта
    memory_type = db.Column(db.String(50))
    total_memory = db.Column(db.String(50))
    module_memory = db.Column(db.String(50))
    module_count = db.Column(db.String(50))
    
    # Быстродействие
    frequency = db.Column(db.String(50))
    
    # Тайминги
    cas_latency = db.Column(db.String(10))
    ras_to_cas_delay = db.Column(db.String(10))
    row_precharge_delay = db.Column(db.String(10))
    activate_to_precharge_delay = db.Column(db.String(10))
    
    # Конструктивные особенности
    double_sided = db.Column(db.Boolean)
    heatsink = db.Column(db.Boolean)
    
    # Дополнительная информация
    voltage = db.Column(db.String(50))
    
    # Дата добавления в базу
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

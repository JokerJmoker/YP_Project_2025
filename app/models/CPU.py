from datetime import datetime
from app.extensions import db

class Cpu(db.Model):
    __tablename__ = 'CPU' 

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    
    # Заводские данные
    warranty = db.Column(db.String(50))
    country = db.Column(db.String(100))
    
    # Общие параметры
    model = db.Column(db.String(100))
    socket = db.Column(db.String(50))
    manufacturer_code = db.Column(db.String(100))
    release_year = db.Column(db.String(10))
    cooler_included = db.Column(db.Boolean)
    thermal_interface_included = db.Column(db.Boolean)
    
    # Ядро и архитектура
    total_cores = db.Column(db.String(10))
    performance_cores = db.Column(db.String(10))
    efficiency_cores = db.Column(db.String(10))
    max_threads = db.Column(db.String(10))
    l2_cache = db.Column(db.String(50))
    l3_cache = db.Column(db.String(50))
    process_technology = db.Column(db.String(50))
    core_architecture = db.Column(db.String(100))
    
    # Частота и разгон
    base_frequency = db.Column(db.String(50))
    turbo_frequency = db.Column(db.String(50))
    base_efficiency_frequency = db.Column(db.String(50))
    turbo_efficiency_frequency = db.Column(db.String(50))
    unlocked_multiplier = db.Column(db.Boolean)
    
    # Параметры оперативной памяти
    memory_type = db.Column(db.String(100))
    max_memory = db.Column(db.String(50))
    memory_channels = db.Column(db.String(10))
    memory_frequency = db.Column(db.String(100))
    ecc_support = db.Column(db.Boolean)
    
    # Тепловые характеристики
    tdp = db.Column(db.String(50))
    base_tdp = db.Column(db.String(50))
    max_temperature = db.Column(db.String(50))
    
    # Графическое ядро
    integrated_graphics = db.Column(db.Boolean)
    gpu_model = db.Column(db.String(100))
    gpu_frequency = db.Column(db.String(50))
    execution_units = db.Column(db.String(10))
    shading_units = db.Column(db.String(10))
    
    # Шина и контроллеры
    pci_express = db.Column(db.String(50))
    pci_lanes = db.Column(db.String(50))
    
    # Дополнительно
    virtualization = db.Column(db.Boolean)
    features = db.Column(db.String(500))
    
    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

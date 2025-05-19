from datetime import datetime
from app.extensions import db

class Dimm(db.Model):
    __table_args__ = {'schema': 'pc_components'}
    __tablename__ = 'dimm'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)  # Увеличено с 250 до 300
    price = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)

    # Заводские данные
    warranty = db.Column(db.String(100))  # Увеличено с 50 до 100
    country = db.Column(db.String(300))  # Увеличено с 255 до 300

    # Общие параметры
    type = db.Column(db.String(100))  # Увеличено с 255 до 100
    model = db.Column(db.String(300))  # Увеличено с 255 до 300
    manufacturer_code = db.Column(db.String(300))  # Увеличено с 255 до 300

    # Объем и состав комплекта
    memory_type = db.Column(db.String(50))
    module_type = db.Column(db.String(100))  # Увеличено с 50 до 100
    total_memory = db.Column(db.String(100))  # Увеличено с 50 до 100
    single_module_memory = db.Column(db.String(100))  # Увеличено с 50 до 100
    modules_count = db.Column(db.String(20))  # Увеличено с 10 до 20
    registered_memory = db.Column(db.Boolean)
    ecc_memory = db.Column(db.Boolean)

    # Быстродействие
    frequency = db.Column(db.String(100))  # Увеличено с 50 до 100
    amd_expo = db.Column(db.String(500))  # Увеличено с 50 до 500 (для длинных описаний)
    intel_xmp = db.Column(db.String(500))  # Увеличено с 50 до 500

    # Тайминги
    cas_latency = db.Column(db.String(20))  # Увеличено с 10 до 20
    ras_to_cas_delay = db.Column(db.String(20))  # Увеличено с 10 до 20
    row_precharge_delay = db.Column(db.String(20))  # Увеличено с 10 до 20
    activate_to_precharge_delay = db.Column(db.String(20))  # Увеличено с 10 до 20

    # Конструкция
    has_heatsink = db.Column(db.Boolean)
    heatsink_color = db.Column(db.String(300))  # Увеличено с 50 до 300
    has_lighting = db.Column(db.Boolean)
    height = db.Column(db.String(50))  # Увеличено с 10 до 50
    low_profile = db.Column(db.Boolean)

    # Дополнительная информация
    voltage = db.Column(db.String(50))  # Увеличено с 20 до 50
    features = db.Column(db.String(1000))  # Увеличено с 500 до 1000
    package_contents = db.Column(db.String(1000))  # Увеличено с 500 до 1000

    # Метаданные
    worker_id = db.Column(db.Integer)
    url_index = db.Column(db.Integer)

    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
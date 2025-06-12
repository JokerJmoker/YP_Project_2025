from datetime import datetime
from app.extensions import db

class PowerSupply(db.Model):
    __table_args__ = {'schema': 'pc_components'}
    __tablename__ = 'power_supply'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(400), nullable=False)  # Увеличен размер для длинных названий
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

    # Заводские данные
    warranty = db.Column(db.String(100))
    country = db.Column(db.String(300))

    # Общие параметры
    type = db.Column(db.String(100))  # "блок питания"
    model = db.Column(db.String(300))
    manufacturer_model = db.Column(db.String(300))
    manufacturer_code = db.Column(db.String(300))
    wattage = db.Column(db.String(50))  # Номинальная мощность

    # Внешний вид
    form_factor = db.Column(db.String(100))
    color = db.Column(db.String(100))
    cable_management = db.Column(db.String(200))  # Модульность кабелей
    cable_sleeving = db.Column(db.Boolean)  # Оплетка проводов
    cable_colors = db.Column(db.String(100))
    lighting_type = db.Column(db.String(100))
    lighting_color = db.Column(db.String(100))
    lighting_source = db.Column(db.String(200))
    lighting_connector = db.Column(db.String(100))

    # Кабели и разъемы
    main_connector = db.Column(db.String(100))  # 24 pin
    cpu_connectors = db.Column(db.String(200))  # CPU 4+4 pin
    pcie_connectors = db.Column(db.String(500))  # PCI-E 6+2 pin
    sata_connectors = db.Column(db.String(50))
    molex_connectors = db.Column(db.String(50))
    floppy_connector = db.Column(db.Boolean)
    cable_length_main = db.Column(db.String(50))
    cable_length_cpu = db.Column(db.String(50))
    cable_length_pcie = db.Column(db.String(200))
    cable_length_sata = db.Column(db.String(50))
    cable_length_molex = db.Column(db.String(50))

    # Электрические параметры
    power_12v = db.Column(db.String(100))
    current_12v = db.Column(db.String(100))
    current_3v = db.Column(db.String(50))
    current_5v = db.Column(db.String(50))
    current_5vsb = db.Column(db.String(50))
    current_12v_neg = db.Column(db.String(50))
    input_voltage = db.Column(db.String(200))

    # Система охлаждения
    cooling_type = db.Column(db.String(100))
    fan_size = db.Column(db.String(100))
    fan_control = db.Column(db.String(200))
    hybrid_mode = db.Column(db.Boolean)
    max_noise = db.Column(db.String(50))

    # Сертификация
    certification_80plus = db.Column(db.String(100))
    pfc_type = db.Column(db.String(100))
    standards = db.Column(db.String(200))
    protections = db.Column(db.String(500))  # Технологии защиты

    # Дополнительная информация
    power_cable_included = db.Column(db.Boolean)
    package_contents = db.Column(db.String(500))
    features = db.Column(db.String(500))

    # Габариты и вес
    length = db.Column(db.String(50))
    width = db.Column(db.String(50))
    height = db.Column(db.String(50))
    weight = db.Column(db.String(50))

    # Метаданные
    worker_id = db.Column(db.Integer)
    url_index = db.Column(db.Integer)

    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
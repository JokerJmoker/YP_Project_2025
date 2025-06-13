from datetime import datetime
from app.extensions import db

class Ssd(db.Model):
    __table_args__ = {'schema': 'pc_components'}
    __tablename__ = 'ssd'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(350), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

    # Заводские данные
    warranty = db.Column(db.String(100))
    country = db.Column(db.String(300))

    # Общие параметры
    type = db.Column(db.String(100))  # "2.5\" SATA накопитель"
    model = db.Column(db.String(300))
    manufacturer_code = db.Column(db.String(300))

    # Основные характеристики
    capacity = db.Column(db.String(100))  # Объем накопителя
    nvme = db.Column(db.Boolean)  # Поддержка NVMe
    interface = db.Column(db.String(100))  # SATA

    # Конфигурация накопителя
    controller = db.Column(db.String(200))  # Контроллер
    cell_type = db.Column(db.String(100))  # 3 бит TLC
    memory_structure = db.Column(db.String(100))  # 3D NAND
    has_dram = db.Column(db.Boolean)  # Наличие DRAM буфера

    # Показатели производительности
    max_read_speed = db.Column(db.String(100))  # Макс. скорость чтения
    max_write_speed = db.Column(db.String(100))  # Макс. скорость записи
    random_read_iops = db.Column(db.String(100))  # Случайное чтение
    random_write_iops = db.Column(db.String(100))  # Случайная запись

    # Надежность
    tbw = db.Column(db.String(100))  # Ресурс записи (TBW)
    dwpd = db.Column(db.String(50))  # DWPD
    shock_resistance = db.Column(db.String(100))  # Ударостойкость

    # Дополнительная информация
    features = db.Column(db.String(500))  # Особенности
    package_contents = db.Column(db.String(500))  # Комплектация

    # Габариты
    width = db.Column(db.String(50))
    length = db.Column(db.String(50))
    thickness = db.Column(db.String(50))
    weight = db.Column(db.String(50))

    # Метаданные
    worker_id = db.Column(db.Integer)
    url_index = db.Column(db.Integer)

    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
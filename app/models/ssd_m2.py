from datetime import datetime
from app.extensions import db

class SsdM2(db.Model):
    __table_args__ = {'schema': 'pc_components'}
    __tablename__ = 'ssd_m2'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(350), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)

    # Заводские данные
    warranty = db.Column(db.String(100))
    country = db.Column(db.String(300))

    # Общие параметры
    type = db.Column(db.String(100))  # "SSD M.2 накопитель"
    model = db.Column(db.String(300))
    manufacturer_code = db.Column(db.String(300))

    # Основные характеристики
    capacity = db.Column(db.String(100))  # Объем накопителя
    form_factor = db.Column(db.String(50))  # 2280
    interface = db.Column(db.String(100))  # PCIe 4.0 x4
    m2_key = db.Column(db.String(50))  # Ключ M.2
    nvme = db.Column(db.Boolean)  # Поддержка NVMe

    # Конфигурация накопителя
    controller = db.Column(db.String(200))  # Контроллер
    cell_type = db.Column(db.String(100))  # 3 бит TLC
    memory_structure = db.Column(db.String(100))  # 3D NAND
    has_dram = db.Column(db.Boolean)  # Наличие DRAM буфера
    dram_size = db.Column(db.String(100))  # Объем DRAM буфера

    # Показатели скорости
    max_read_speed = db.Column(db.String(100))  # Макс. скорость чтения
    max_write_speed = db.Column(db.String(100))  # Макс. скорость записи
    random_read_iops = db.Column(db.String(100))  # Случайное чтение
    random_write_iops = db.Column(db.String(100))  # Случайная запись

    # Надежность
    tbw = db.Column(db.String(100))  # Ресурс записи (TBW)
    dwpd = db.Column(db.String(50))  # DWPD

    # Дополнительная информация
    heatsink_included = db.Column(db.Boolean)  # Радиатор в комплекте
    power_consumption = db.Column(db.String(100))  # Энергопотребление
    features = db.Column(db.String(500))  # Особенности

    # Габариты
    length = db.Column(db.String(50))
    width = db.Column(db.String(50))
    thickness = db.Column(db.String(50))
    weight = db.Column(db.String(50))

    # Метаданные
    worker_id = db.Column(db.Integer)
    url_index = db.Column(db.Integer)

    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
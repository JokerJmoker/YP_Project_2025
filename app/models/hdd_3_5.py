from datetime import datetime
from app.extensions import db

class Hdd_3_5(db.Model):
    __table_args__ = {'schema': 'pc_components'}
    __tablename__ = 'hdd_3_5'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(350), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)

    # Заводские данные
    warranty = db.Column(db.String(100))
    country = db.Column(db.String(300))

    # Общие параметры
    type = db.Column(db.String(100))  # "жесткий диск"
    model = db.Column(db.String(300))
    manufacturer_code = db.Column(db.String(300))
    purpose = db.Column(db.String(500))  # Назначение

    # Характеристики накопителя
    capacity = db.Column(db.String(100))  # Объем HDD
    cache_size = db.Column(db.String(100))  # Объем кэш-памяти
    rotation_speed = db.Column(db.String(100))  # Скорость вращения
    max_data_rate = db.Column(db.String(100))  # Макс. скорость передачи
    latency = db.Column(db.String(50))  # Время задержки
    interface = db.Column(db.String(100))  # Интерфейс
    interface_speed = db.Column(db.String(100))  # Пропускная способность
    raid_optimized = db.Column(db.Boolean)  # Оптимизация под RAID

    # Механика и надежность
    recording_tech = db.Column(db.String(100))  # Технология записи
    shock_resistance = db.Column(db.String(100))  # Ударостойкость
    noise_operation = db.Column(db.String(50))  # Шум при работе
    noise_idle = db.Column(db.String(50))  # Шум в простое
    helium_filled = db.Column(db.Boolean)  # Гелиевое наполнение
    load_cycles = db.Column(db.String(100))  # Циклы позиционирования

    # Энергопотребление
    max_power = db.Column(db.String(50))  # Макс. энергопотребление
    idle_power = db.Column(db.String(50))  # В режиме ожидания

    # Температурный режим
    min_temp = db.Column(db.String(50))  # Мин. рабочая температура
    max_temp = db.Column(db.String(50))  # Макс. рабочая температура

    # Особенности
    features = db.Column(db.String(500))  # Дополнительные особенности

    # Габариты и вес
    width = db.Column(db.String(50))
    length = db.Column(db.String(50))
    thickness = db.Column(db.String(50))
    weight = db.Column(db.String(50))

    # Метаданные
    worker_id = db.Column(db.Integer)
    url_index = db.Column(db.Integer)

    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
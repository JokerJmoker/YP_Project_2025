from datetime import datetime
from app.extensions import db

class Hdd_2_5(db.Model):
    __table_args__ = {'schema': 'pc_components'}
    __tablename__ = 'hdd_2_5'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(300), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

    # Заводские данные
    warranty = db.Column(db.String(100))
    country = db.Column(db.String(300))

    # Общие параметры
    type = db.Column(db.String(100))  # "жесткий диск"
    model = db.Column(db.String(300))
    manufacturer_code = db.Column(db.String(300))

    # Характеристики накопителя
    capacity = db.Column(db.String(100))  # Объем HDD
    buffer_size = db.Column(db.String(100))  # Объем буфера
    rotation_speed = db.Column(db.String(50))  # Скорость вращения
    data_transfer_rate = db.Column(db.String(100))  # Скорость обмена данными
    seek_time = db.Column(db.String(50))  # Время доступа
    interface = db.Column(db.String(100))  # Интерфейс
    interface_speed = db.Column(db.String(100))  # Пропускная способность

    # Механика и надежность
    recording_tech = db.Column(db.String(100))  # Технология записи
    shock_resistance = db.Column(db.String(100))  # Ударостойкость
    noise_operation = db.Column(db.String(50))  # Шум при работе
    noise_idle = db.Column(db.String(50))  # Шум в простое
    load_cycles = db.Column(db.String(100))  # Циклы позиционирования

    # Энергопотребление
    max_power = db.Column(db.String(50))  # Макс. энергопотребление
    idle_power = db.Column(db.String(50))  # В режиме ожидания

    # Температурный режим
    min_temp = db.Column(db.String(50))  # Мин. рабочая температура
    max_temp = db.Column(db.String(50))  # Макс. рабочая температура

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
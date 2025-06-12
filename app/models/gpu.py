from datetime import datetime
from app.extensions import db

class Gpu(db.Model):
    __table_args__ = {'schema': 'pc_components'}
    __tablename__ = 'gpu'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(350), nullable=False)  # Учитываем длинные названия
    price = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

    # Заводские данные
    warranty = db.Column(db.String(100))
    country = db.Column(db.String(300))

    # Общие параметры
    type = db.Column(db.String(100))
    model = db.Column(db.String(300))
    manufacturer_code = db.Column(db.String(300))
    color = db.Column(db.String(100))
    mining = db.Column(db.Boolean)  # Для майнинга
    lhr = db.Column(db.Boolean)  # LHR (ограничение майнинга)

    # Основные параметры
    gpu_model = db.Column(db.String(200))  # Графический процессор
    architecture = db.Column(db.String(100))  # Микроархитектура
    process_tech = db.Column(db.String(50))  # Техпроцесс

    # Спецификации видеопроцессора
    base_clock = db.Column(db.String(50))  # Штатная частота
    boost_clock = db.Column(db.String(50))  # Турбочастота
    cuda_cores = db.Column(db.String(50))  # Количество ALU
    texture_units = db.Column(db.String(50))  # Текстурные блоки
    raster_units = db.Column(db.String(50))  # Блоки растеризации
    ray_tracing = db.Column(db.Boolean)  # Поддержка трассировки
    rt_cores = db.Column(db.String(50))  # RT-ядра
    tensor_cores = db.Column(db.String(50))  # Тензорные ядра

    # Спецификации видеопамяти
    vram_size = db.Column(db.String(50))  # Объем видеопамяти
    vram_type = db.Column(db.String(50))  # Тип памяти
    bus_width = db.Column(db.String(50))  # Разрядность шины
    memory_bandwidth = db.Column(db.String(100))  # Пропускная способность
    memory_clock = db.Column(db.String(50))  # Эффективная частота

    # Вывод изображения
    video_outputs = db.Column(db.String(300))  # Видеоразъемы
    hdmi_version = db.Column(db.String(50))
    dp_version = db.Column(db.String(50))
    max_displays = db.Column(db.String(50))
    max_resolution = db.Column(db.String(100))

    # Подключение
    interface = db.Column(db.String(100))  # PCIe версия
    slot_width = db.Column(db.String(50))  # Форм-фактор
    pcie_lanes = db.Column(db.String(50))
    power_connectors = db.Column(db.String(200))
    recommended_psu = db.Column(db.String(100))
    tdp = db.Column(db.String(50))  # Потребляемая мощность

    # Система охлаждения
    cooling_type = db.Column(db.String(100))
    fans = db.Column(db.String(200))  # Тип и количество вентиляторов
    liquid_cooling = db.Column(db.Boolean)

    # Дополнительная информация
    lighting = db.Column(db.Boolean)
    lighting_sync = db.Column(db.String(200))
    lcd_display = db.Column(db.Boolean)
    bios_switch = db.Column(db.Boolean)
    features = db.Column(db.String(1000))
    package_contents = db.Column(db.String(1000))

    # Габариты и вес
    low_profile = db.Column(db.Boolean)
    slots = db.Column(db.String(50))  # Количество слотов
    length = db.Column(db.String(50))  # Длина
    width = db.Column(db.String(50))  # Ширина
    thickness = db.Column(db.String(50))  # Толщина
    weight = db.Column(db.String(50))  # Вес

    # Метаданные
    worker_id = db.Column(db.Integer)
    url_index = db.Column(db.Integer)

    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Оценка бенчмарка    
    benchmark_rate = db.Column(db.Float, nullable=True)
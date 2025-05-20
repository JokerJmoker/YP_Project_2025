from datetime import datetime
from app.extensions import db

class Motherboard(db.Model):
    __table_args__ = {'schema': 'pc_components'}
    __tablename__ = 'motherboard'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(350), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    image_path = db.Column(db.String(500), nullable=False)

    # Заводские данные
    warranty = db.Column(db.String(100))
    country = db.Column(db.String(300))

    # Общие параметры
    type = db.Column(db.String(100))  # "материнская плата"
    model = db.Column(db.String(300))
    series = db.Column(db.String(200))
    color = db.Column(db.String(100))
    release_year = db.Column(db.String(50))

    # Форм-фактор и размеры
    form_factor = db.Column(db.String(100))
    height = db.Column(db.String(50))
    width = db.Column(db.String(50))

    # Процессор и чипсет
    socket = db.Column(db.String(100))
    chipset = db.Column(db.String(100))
    compatible_cpus = db.Column(db.String(300))

    # Память
    memory_type = db.Column(db.String(100))
    memory_form_factor = db.Column(db.String(100))
    memory_slots = db.Column(db.String(50))
    memory_channels = db.Column(db.String(50))
    max_memory = db.Column(db.String(100))
    base_memory_freq = db.Column(db.String(100))
    oc_memory_freq = db.Column(db.String(500))  # Частоты в разгоне

    # Слоты расширения
    pcie_version = db.Column(db.String(100))
    pcie_x16_slots = db.Column(db.String(500))
    sli_crossfire = db.Column(db.String(200))
    sli_crossfire_count = db.Column(db.String(100))
    pcie_x1_slots = db.Column(db.String(50))

    # Контроллеры накопителей
    nvme_support = db.Column(db.Boolean)
    nvme_pcie_version = db.Column(db.String(100))
    m2_slots = db.Column(db.String(50))
    m2_cpu_slots = db.Column(db.String(200))
    m2_chipset_slots = db.Column(db.String(500))
    sata_ports = db.Column(db.String(50))
    sata_raid = db.Column(db.String(200))
    nvme_raid = db.Column(db.String(100))
    other_storage = db.Column(db.String(200))

    # Порты на задней панели
    usb_a_ports = db.Column(db.String(500))
    usb_c_ports = db.Column(db.String(300))
    video_outputs = db.Column(db.String(300))
    lan_ports = db.Column(db.String(50))
    audio_ports = db.Column(db.String(100))
    spdif = db.Column(db.String(100))
    wifi_antennas = db.Column(db.Boolean)
    ps2_ports = db.Column(db.String(100))

    # Разъемы на плате
    internal_usb_a = db.Column(db.String(300))
    internal_usb_c = db.Column(db.String(200))
    cpu_fan_headers = db.Column(db.String(200))
    case_fan_4pin = db.Column(db.String(50))
    aio_pump_headers = db.Column(db.String(200))
    case_fan_3pin = db.Column(db.String(50))
    argb_headers = db.Column(db.String(100))
    rgb_headers = db.Column(db.String(100))
    wifi_m2 = db.Column(db.Boolean)
    com_ports = db.Column(db.String(100))
    lpt_ports = db.Column(db.String(100))

    # Аудио
    audio_scheme = db.Column(db.String(100))
    audio_chipset = db.Column(db.String(200))

    # Сеть
    lan_speed = db.Column(db.String(200))
    lan_chipsets = db.Column(db.String(300))
    wifi_standard = db.Column(db.String(100))
    bluetooth = db.Column(db.String(100))
    wifi_chipset = db.Column(db.String(200))

    # Питание и охлаждение
    main_power = db.Column(db.String(100))
    cpu_power = db.Column(db.String(200))
    power_phases = db.Column(db.String(100))
    passive_cooling = db.Column(db.String(300))
    active_cooling = db.Column(db.String(500))

    # Дополнительная информация
    onboard_buttons = db.Column(db.String(500))
    lighting = db.Column(db.Boolean)
    lighting_software = db.Column(db.String(200))
    pcb_layers = db.Column(db.String(50))
    smartphone_app = db.Column(db.String(100))
    features = db.Column(db.String(1000))
    package_contents = db.Column(db.String(1000))

    # Габариты упаковки
    box_length = db.Column(db.String(50))
    box_width = db.Column(db.String(50))
    box_height = db.Column(db.String(50))
    box_weight = db.Column(db.String(50))

    # Метаданные
    worker_id = db.Column(db.Integer)
    url_index = db.Column(db.Integer)

    # Дата добавления
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
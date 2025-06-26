import psycopg2
from psycopg2 import sql

# Данные для подключения к БД (замените на свои)
DB_NAME = "mydb"
DB_USER = "jokerjmoker"
DB_PASSWORD = "270961Ts"
DB_HOST = "127.0.0.1"
DB_PORT = "5532"

# Данные для таблицы (один вариант CPU/GPU для каждой категории)
PC_CONFIGS = [
    {
        "quality": "low",
        "cpu": "Процессор AMD Ryzen 5 5600 OEM",
        "gpu": "Видеокарта ASRock AMD Radeon RX 6500 XT Challenger ITX [RX6500XT CLI 4G]",
        "dimm": "Оперативная память ExeGate HiPower [EX288049RUS] 8 ГБ",
        "ssd_m2": "500 ГБ M.2 NVMe накопитель Kingston NV2 [SNV2S/500G]",
    },
    {
        "quality": "medium",
        "cpu": "Процессор AMD Ryzen 5 5600G OEM",
        "gpu": "Видеокарта MSI AMD Radeon RX 6700 XT MECH 2X OC [RX 6700 XT MECH 2X 12G OC]",
        "dimm": "Оперативная память ADATA XPG SPECTRIX D50 RGB [AX4U36008G18I-ST50] 8 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель WD Blue SN580 [WDS100T3B0E]",
    },
    {
        "quality": "high",
        "cpu": "Процессор AMD Ryzen 5 7600X BOX",
        "gpu": "Видеокарта GIGABYTE GeForce RTX 3060 GAMING OC (LHR) [GV-N3060GAMING OC-12GD Rev2.0]",
        "dimm": "Оперативная память ADATA XPG SPECTRIX D45G RGB [AX4U36008G18I-DCBKD45G] 16 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель Samsung 980 PRO [MZ-V8P1T0BW]",
    },
    {
        "quality": "ultra",
        "cpu": "Процессор AMD Ryzen 7 7800X3D BOX",
        "gpu": "Видеокарта ASUS GeForce RTX 4070 Ti SUPER PRIME OC Edition [PRIME-RTX4070TIS-O16G]",
        "dimm": "Оперативная память Kingston FURY Beast Black RGB [KF436C18BB2AK2/32] 32 ГБ",
        "ssd_m2": "2000 ГБ M.2 NVMe накопитель WD Black SN770 [WDS200T3X0E]",
    }
]

def create_game_table():
    try:
        # Подключаемся к БД
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # Создаем схему games, если она не существует
        cursor.execute("CREATE SCHEMA IF NOT EXISTS games")
        
        # Создаем таблицу games.valorant
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games.valorant (
                quality VARCHAR(50) PRIMARY KEY,
                cpu VARCHAR(100) NOT NULL,
                gpu VARCHAR(100) NOT NULL,
                ssd_m2 VARCHAR(100) NOT NULL,
                dimm VARCHAR(100) NOT NULL
            )
        """)

        # Вставляем данные
        for config in PC_CONFIGS:
            cursor.execute(
                sql.SQL("""
                    INSERT INTO games.valorant (quality, cpu, gpu, ssd_m2, dimm)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (quality) DO NOTHING
                """),
                (config["quality"], config["cpu"], config["gpu"], config["ssd_m2"], config["dimm"])
            )

        # Сохраняем изменения
        conn.commit()
        print("Таблица 'games.valorant' успешно создана и заполнена!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_game_table()
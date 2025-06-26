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
        "cpu": "Процессор AMD Ryzen 5 3500 OEM",
        "gpu": "Видеокарта ASRock AMD Radeon RX 550 Low Profile [RX550 LP 4G]",
        "dimm": "Оперативная память Neo Forza [NMUD416F82-3200EA10] 16 ГБ",
        "ssd_m2": "500 ГБ M.2 NVMe накопитель Kingston NV2 [SNV2S/500G]",
    },
    {
        "quality": "medium",
        "cpu": "Процессор Intel Core i7-10700KF OEM",
        "gpu": "Видеокарта MSI AMD Radeon RX 6700 XT MECH 2X OC [RX 6700 XT MECH 2X 12G OC]",
        "dimm": "Оперативная память Kingston FURY Beast Black [KF432C16BBK2/16-SP] 16 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель WD Blue SN580 [WDS100T3B0E]",
    },
    {
        "quality": "high",
        "cpu": "Процессор AMD Ryzen 7 7800X3D BOX",
        "gpu": "Видеокарта ASUS GeForce RTX 4070 Dual EVO OC Edition [DUAL-RTX4070-O12G]",
        "dimm": "Оперативная память Patriot Viper Elite II [PVE2432G320C8K] 32 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель Samsung 980 PRO [MZ-V8P1T0BW]",
    },
    {
        "quality": "ultra",
        "cpu": "Процессор Intel Core i9-14900KS BOX",
        "gpu": "Видеокарта MSI GeForce RTX 5080 VENTUS 3X OC [RTX 5080 16G VENTUS 3X OC]",
        "dimm": "Оперативная память Patriot Viper Venom RGB [PVVR564G520C40K] 64 ГБ",
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
        
        # Создаем таблицу games.call_of_duty_modern_warfare_3
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games.call_of_duty_modern_warfare_3 (
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
                    INSERT INTO games.call_of_duty_modern_warfare_3 (quality, cpu, gpu, ssd_m2, dimm)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (quality) DO NOTHING
                """),
                (config["quality"], config["cpu"], config["gpu"], config["ssd_m2"], config["dimm"])
            )

        # Сохраняем изменения
        conn.commit()
        print("Таблица 'games.call_of_duty_modern_warfare_3' успешно создана и заполнена!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_game_table()
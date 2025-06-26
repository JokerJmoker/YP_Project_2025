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
        "cpu": "Процессор Intel Core i3-9100F OEM",
        "gpu": "Видеокарта GIGABYTE GeForce GT 1030 Low Profile D4 2G [GV-N1030D4-2GL]",
        "dimm": "Оперативная память Patriot Signature Line [PSD48G320081] 8 ГБ",
        "ssd_m2": "500 ГБ M.2 NVMe накопитель Kingston NV2 [SNV2S/500G]",
    },
    {
        "quality": "medium",
        "cpu": "Процессор AMD Ryzen 5 5600XT OEM",
        "gpu": "Видеокарта ASRock AMD Radeon RX 6600 Challenger White [RX6600 CLW 8G]",
        "dimm": "Оперативная память Kingston FURY Beast Black [KF432C16BBK2/16-SP] 16 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель WD Blue SN580 [WDS100T3B0E]",
    },
    {
        "quality": "high",
        "cpu": "Процессор Intel Core i7-12700F BOX",
        "gpu": "Видеокарта GIGABYTE GeForce RTX 3060 WINDFORCE [GV-N3060WF2-12GD]",
        "dimm": "Оперативная память Crucial [CT32G52C42U5] 32 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель Samsung 980 PRO [MZ-V8P1T0BW]",
    },
    {
        "quality": "ultra",
        "cpu": "Процессор Intel Core i9-13900K BOX",
        "gpu": "Видеокарта GIGABYTE GeForce RTX 4080 SUPER GAMING OC [GV-N408SGAMING OC-16GD]",
        "dimm": "Оперативная память Kingston FURY Beast Black RGB [KF436C18BB2AK4/128] 128 ГБ",
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
        
        # Создаем таблицу games.apex_legends
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games.apex_legends (
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
                    INSERT INTO games.apex_legends (quality, cpu, gpu, ssd_m2, dimm)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (quality) DO NOTHING
                """),
                (config["quality"], config["cpu"], config["gpu"], config["ssd_m2"], config["dimm"])
            )

        # Сохраняем изменения
        conn.commit()
        print("Таблица 'games.apex_legends' успешно создана и заполнена!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_game_table()
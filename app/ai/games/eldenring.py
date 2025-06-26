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
        "cpu": "Процессор Intel Core i5-8400 OEM",
        "gpu": "Видеокарта GIGABYTE GeForce GT 1030 Low Profile D4 2G [GV-N1030D4-2GL]",
        "dimm": "Оперативная память Neo Forza [NMUD416F82-3200EA10] 16 ГБ",
        "ssd_m2": "500 ГБ M.2 NVMe накопитель Kingston NV2 [SNV2S/500G]",
    },
    {
        "quality": "medium",
        "cpu": "Процессор AMD Ryzen 5 3600X OEM",
        "gpu": "Видеокарта MSI GeForce GTX 1650 D6 VENTUS XS OCV3 [GeForce GTX 1650 D6 VENTUS XS OCV3]",
        "dimm": "Оперативная память Netac Shadow [NTSDD4P26SP-16B] 16 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель WD Blue SN580 [WDS100T3B0E]",
    },
    {
        "quality": "high",
        "cpu": "Процессор AMD Ryzen 7 5800X OEM",
        "gpu": "Видеокарта INNO3D GeForce RTX 3060 TWIN X2 (LHR) [N30602-12D6-119032AH]",
        "dimm": "Оперативная память Kingston ValueRAM [KVR32N22D8/32] 32 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель Samsung 980 PRO [MZ-V8P1T0BW]",
    },
    {
        "quality": "ultra",
        "cpu": "Процессор Intel Core i9-14900KF BOX",
        "gpu": "Видеокарта Sapphire AMD Radeon RX 7900 XT PULSE OC [11323-02-20G]",
        "dimm": "Оперативная память Kingston ValueRAM [KVR32N22D8/32] 32 ГБ",
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
        
        # Создаем таблицу games.eldenring
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games.eldenring (
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
                    INSERT INTO games.eldenring (quality, cpu, gpu, ssd_m2, dimm)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (quality) DO NOTHING
                """),
                (config["quality"], config["cpu"], config["gpu"], config["ssd_m2"], config["dimm"])
            )

        # Сохраняем изменения
        conn.commit()
        print("Таблица 'games.eldenring' успешно создана и заполнена!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_game_table()
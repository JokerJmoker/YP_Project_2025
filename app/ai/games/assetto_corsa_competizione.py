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
        "gpu": "Видеокарта MSI GeForce GTX 1650 D6 VENTUS XS OCV3 [GeForce GTX 1650 D6 VENTUS XS OCV3]",
        "dimm": "Оперативная память ExeGate HiPower [EX288049RUS] 8 ГБ",
        "ssd_m2": "500 ГБ M.2 NVMe накопитель Kingston NV2 [SNV2S/500G]",
    },
    {
        "quality": "medium",
        "cpu": "Процессор Intel Core i7-10700KF OEM",
        "gpu": "Видеокарта INNO3D GeForce RTX 3060 TWIN X2 (LHR) [N30602-12D6-119032AH]",
        "dimm": "Оперативная память Kingston FURY Renegade RGB [KF436C16RB12A/16] 16 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель WD Blue SN580 [WDS100T3B0E]",
    },
    {
        "quality": "high",
        "cpu": "Процессор Intel Core i9-12900KF BOX",
        "gpu": "Видеокарта GIGABYTE GeForce RTX 4070 WINDFORCE 2X OC V2 [GV-N4070WF2OCV2-12GD]",
        "dimm": "Оперативная память Kingston FURY Beast Black [KF556C36BBEK2-32] 32 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель Samsung 980 PRO [MZ-V8P1T0BW]",
    },
    {
        "quality": "ultra",
        "cpu": "Процессор AMD Ryzen 9 7950X3D BOX",
        "gpu": "Видеокарта MSI GeForce RTX 5080 VENTUS 3X OC [RTX 5080 16G VENTUS 3X OC]",
        "dimm": "Оперативная память Corsair Vengeance RGB PRO [CMW32GX4M4C3600C18] 32 ГБ",
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
        
        # Создаем таблицу games.assetto_corsa_competizione
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games.assetto_corsa_competizione (
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
                    INSERT INTO games.assetto_corsa_competizione (quality, cpu, gpu, ssd_m2, dimm)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (quality) DO NOTHING
                """),
                (config["quality"], config["cpu"], config["gpu"], config["ssd_m2"], config["dimm"])
            )

        # Сохраняем изменения
        conn.commit()
        print("Таблица 'games.assetto_corsa_competizione' успешно создана и заполнена!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_game_table()
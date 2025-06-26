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
        "cpu": "Процессор AMD Ryzen 3 4100 OEM",
        "gpu": "Видеокарта Palit GeForce GT 1030 [NEC103000646-1082F]",
        "dimm": "Оперативная память DEXP [DEXP8GD3UD16] 8 ГБ",
        "ssd_m2": "500 ГБ M.2 NVMe накопитель Kingston NV2 [SNV2S/500G]",
    },
    {
        "quality": "medium",
        "cpu": "Процессор Intel Core i5-10400F BOX",
        "gpu": "Видеокарта MSI GeForce GT 1030 [GeForce GT 1030 4GD4 LP OC]",
        "dimm": "Оперативная память Patriot Signature Line Premium [PSP416G2666KH1] 16 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель WD Blue SN580 [WDS100T3B0E]",
    },
    {
        "quality": "high",
        "cpu": "Процессор Intel Core i7-12700K BOX",
        "gpu": "Видеокарта INNO3D GeForce RTX 3060 TWIN X2 (LHR) [N30602-12D6-119032AH]",
        "dimm": "Оперативная память G.Skill Aegis [F4-3200C16S-16GIS] 16 ГБ",
        "ssd_m2": "1000 ГБ M.2 NVMe накопитель Samsung 980 PRO [MZ-V8P1T0BW]",
    },
    {
        "quality": "ultra",
        "cpu": "Процессор AMD Ryzen 9 7950X3D BOX",
        "gpu": "Видеокарта MSI GeForce RTX 4070 Ti SUPER GAMING SLIM WHITE [GeForce RTX 4070 Ti SUPER 16G GAMING SLIM WHITE]",
        "dimm": "Оперативная память Kingston FURY Beast White [KF560C40BW-32] 32 ГБ",
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
        
        # Создаем таблицу games.cs_2
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games.cs_2 (
                quality VARCHAR(50) PRIMARY KEY,
                cpu VARCHAR(150) NOT NULL,
                gpu VARCHAR(150) NOT NULL,
                ssd_m2 VARCHAR(150) NOT NULL,
                dimm VARCHAR(150) NOT NULL
            )
        """)

        # Вставляем данные
        for config in PC_CONFIGS:
            cursor.execute(
                sql.SQL("""
                    INSERT INTO games.cs_2 (quality, cpu, gpu, ssd_m2, dimm)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (quality) DO NOTHING
                """),
                (config["quality"], config["cpu"], config["gpu"], config["ssd_m2"], config["dimm"])
            )

        # Сохраняем изменения
        conn.commit()
        print("Таблица 'games.cs_2' успешно создана и заполнена!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_game_table()
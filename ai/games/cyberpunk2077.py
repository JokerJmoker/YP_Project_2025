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
        "preset": "low",
        "cpu": "Процессор AMD Ryzen 5 5600 BOX",
        "gpu": "ASUS GeForce GT 1030 LP [GT1030-2G-BRK]",
        "dimm": "Оперативная память Kingston FURY Beast Black [KF432C16BBK2/16-SP] 16 ГБ",
        "ssd": "500 ГБ M.2 NVMe накопитель Kingston NV2 [SNV2S/500G]",
    },
    {
        "preset": "medium",
        "cpu": "Процессор Intel Core i5-12400F OEM",
        "gpu": "Видеокарта Palit GeForce RTX 3060 Dual (LHR) [NE63060019K9-190AD]",
        "dimm": "Оперативная память Kingston FURY Beast Black RGB [KF436C17BB2AK2/16] 16 ГБ",
        "ssd": "1000 ГБ M.2 NVMe накопитель WD Blue SN580 [WDS100T3B0E]",
    },
    {
        "preset": "high",
        "cpu": "Процессор AMD Ryzen 7 5800X3D OEM",
        "gpu": "Видеокарта MSI GeForce RTX 4070 SUPER VENTUS 2X OC [GeForce RTX 4070 SUPER 12G VENTUS 2X OC]",
        "dimm": "Оперативная память Kingston FURY Renegade RGB [KF436C16RB12AK2/32] 32 ГБ",
        "ssd": "1000 ГБ M.2 NVMe накопитель Samsung 980 PRO [MZ-V8P1T0BW]",
    },
    {
        "preset": "ultra",
        "cpu": "Процессор Intel Core i7-14700K OEM",
        "gpu": "Видеокарта GIGABYTE GeForce RTX 4080 SUPER GAMING OC [GV-N408SGAMING OC-16GD]",
        "dimm": "Оперативная память G.Skill Trident Z5 RGB [F5-7800J3646H16GX2-TZ5RK] 32 ГБ",
        "ssd": "2000 ГБ M.2 NVMe накопитель WD Black SN770 [WDS200T3X0E]",
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
        
        # Создаем таблицу games.cyberpunk_2077
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS games.cyberpunk_2077 (
                preset VARCHAR(50) PRIMARY KEY,
                cpu VARCHAR(100) NOT NULL,
                gpu VARCHAR(100) NOT NULL,
                ssd VARCHAR(100) NOT NULL,
                dimm VARCHAR(100) NOT NULL
            )
        """)

        # Вставляем данные
        for config in PC_CONFIGS:
            cursor.execute(
                sql.SQL("""
                    INSERT INTO games.cyberpunk_2077 (preset, cpu, gpu, ssd, dimm)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (preset) DO NOTHING
                """),
                (config["preset"], config["cpu"], config["gpu"], config["ssd"], config["dimm"])
            )

        # Сохраняем изменения
        conn.commit()
        print("Таблица 'games.cyberpunk_2077' успешно создана и заполнена!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_game_table()
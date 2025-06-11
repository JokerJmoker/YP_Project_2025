import json
import psycopg2
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def select_json_file():
    Tk().withdraw()
    file_path = askopenfilename(
        filetypes=[("JSON Files", "*.json")],
        title="Выберите JSON-файл запроса"
    )
    return file_path

def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_user_request(data):
    selections = data["user_selections"]

    game_title = selections["game"]["title"]
    graphics_quality = selections["game"]["graphics_settings"]["quality"].lower()

    budget_amount = int(selections["budget"]["amount"])
    currency = selections["budget"]["currency"]

    mandatory = selections["components"]["mandatory"]
    mandatory_priorities = selections["components"]["mandatory_priorities"]

    optional = selections["components"]["optional"]
    optional_priorities = selections["components"]["optional_priorities"]

    return {
        "game": game_title,
        "quality": graphics_quality,
        "budget": budget_amount,
        "currency": currency,
        "mandatory": {
            k: v.lower() if isinstance(v, str) else v
            for k, v in mandatory.items()
        },
        "mandatory_priorities": {
            k.replace("_priority", ""): v.lower()
            for k, v in mandatory_priorities.items()
        },
        "optional": {
            k: v.lower() if isinstance(v, str) else v
            for k, v in optional.items()
        },
        "optional_priorities": {
            k.replace("_priority", ""): v.lower()
            for k, v in optional_priorities.items()
        }
    }

def get_recommended_config(game_title, quality, conn):
    with conn.cursor() as cur:
        query = f"""
        SELECT cpu, gpu, ssd, dimm
        FROM games."{game_title}"
        WHERE preset = %s
        """
        cur.execute(query, (quality,))
        result = cur.fetchone()
        if not result:
            raise ValueError("Нет конфигурации для указанных параметров.")
        return {
            "cpu": result[0],
            "gpu": result[1],
            "ssd": result[2],
            "dimm": result[3]
        }

def get_component_price(component_type, name, conn):
    with conn.cursor() as cur:
        query = f"""
        SELECT price FROM pc_components.{component_type}
        WHERE name = %s
        """
        cur.execute(query, (name,))
        result = cur.fetchone()
        if result:
            # Обрабатываем цену в формате "12345 ₽"
            price_str = str(result[0])
            # Удаляем всё, кроме цифр
            price_clean = ''.join(c for c in price_str if c.isdigit())
            return int(price_clean) if price_clean else 0
        return 0

def calculate_total_price(config, conn):
    total = 0
    for component_type, name in config.items():
        price = get_component_price(component_type, name, conn)
        total += price
    return total

def is_within_budget(config, budget, conn):
    total_price = calculate_total_price(config, conn)
    return total_price <= budget

def handle_build_request(request_data, conn):
    parsed = parse_user_request(request_data)
    try:
        recommended = get_recommended_config(parsed["game"], parsed["quality"], conn)
        total_price = calculate_total_price(recommended, conn)

        if total_price <= parsed["budget"]:
            return {
                "status": "success",
                "build": recommended,
                "total_price": total_price,
                "currency": "₽",
                "within_budget": True
            }
        else:
            return {
                "status": "partial",
                "message": "Сборка не укладывается в бюджет. Требуется подбор альтернатив.",
                "recommended_build": recommended,
                "recommended_price": total_price,
                "currency": "₽",
                "within_budget": False
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

def main():
    file_path = select_json_file()
    if not file_path:
        print("Файл не выбран.")
        return

    data = load_json_data(file_path)

    conn = psycopg2.connect(
        dbname="mydb",
        user="jokerjmoker",
        password="270961Ts",
        host="127.0.0.1",
        port="5532"
    )

    try:
        result = handle_build_request(data, conn)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        conn.close()

if __name__ == "__main__":
    main()
from ai_db.queries_1st_stage import get_recommended_config, get_component_price

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

def calculate_total_price(conn, config):
    total = 0
    for component_type, name in config.items():
        price = get_component_price(conn, component_type, name)
        total += price
    return total

def handle_build_request(conn, request_data):
    parsed = parse_user_request(request_data)
    try:
        recommended = get_recommended_config(conn, parsed["game"], parsed["quality"])
        total_price = calculate_total_price(conn, recommended)

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
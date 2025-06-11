from ai_db.queries_1st_stage import get_recommended_config, get_component_price

def parse_allocation_method(allocation_data, method):
        """Helper function to parse allocation data based on selected method"""
        method_data = allocation_data.get(f"{method}_based", {})
        
        if method == "priority_based":
            return {
                k.replace("_priority", ""): v.lower()
                for k, v in method_data.items()
            }
        elif method == "percentage_based":
            return {
                k.replace("_percentage", ""): int(v)
                for k, v in method_data.items()
            }
        elif method == "fixed_price_based":
            return {
                k.replace("_max_price", ""): int(v)
                for k, v in method_data.items()
            }
        return {}


def calculate_total_price(conn, config):
    total = 0
    for component_type, name in config.items():
        price = get_component_price(conn, component_type, name)
        total += price
    return total


def parse_user_request(data):
    try:
        selections = data["user_selections"]
        
        # Game info
        game_info = {
            "title": selections["game"]["title"],
            "graphics": {
                "quality": selections["game"]["graphics_settings"].get("quality", "medium").lower(),
                "target_fps": selections["game"]["graphics_settings"].get("target_fps"),
                "resolution": selections["game"]["graphics_settings"].get("resolution"),
                "ray_tracing": selections["game"]["graphics_settings"].get("ray_tracing", False),
                "dlss": selections["game"]["graphics_settings"].get("dlss", "disabled").lower(),
                "fsr": selections["game"]["graphics_settings"].get("fsr", "disabled").lower()
            }
        }

        # Budget info
        budget_info = {
            "amount": int(selections["budget"]["amount"]),
            "currency": selections["budget"].get("currency", "RUB"),
            "allocation_method": selections["budget"].get("budget_allocation_method", "priority_based")
        }

        # Components
        components = {
            "mandatory": {
                "components": {
                    k: v.lower() if isinstance(v, str) else v
                    for k, v in selections["components"]["mandatory"].items()
                },
                "allocation": parse_allocation_method(
                    selections["components"].get("mandatory_allocation", {}),
                    budget_info["allocation_method"]
                )
            },
            "optional": {
                "components": {
                    k: v.lower() if isinstance(v, str) else v
                    for k, v in selections["components"].get("optional", {}).items()
                },
                "allocation": parse_allocation_method(
                    selections["components"].get("optional_allocation", {}),
                    budget_info["allocation_method"]
                )
            }
        }

        return {
            "game": game_info,
            "budget": budget_info,
            "components": components
        }
    except KeyError as e:
        raise ValueError(f"Missing required field: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing request: {str(e)}")


def handle_build_request(conn, request_data):
    try:
        parsed = parse_user_request(request_data)
        recommended = get_recommended_config(conn, parsed["game"], parsed["game"]["graphics"]["quality"])
        total_price = calculate_total_price(conn, recommended)

        response = {
            "status": "success",
            "build": recommended,
            "total_price": total_price,
            "currency": "₽",
            "within_budget": total_price <= parsed["budget"]["amount"]
        }

        if not response["within_budget"]:
            response["status"] = "partial"
            response["message"] = "Сборка не укладывается в бюджет. Требуется подбор альтернатив."

        return response
    except ValueError as e:
        return {
            "status": "error",
            "message": f"Invalid request data: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Internal error: {str(e)}"
        }
def parse_game_settings(game_data):
    """Парсим настройки игры с валидацией данных"""
    if not isinstance(game_data, dict):
        raise ValueError("game_data должен быть словарем")
    
    # Вход — уже сам game
    game_info = game_data
    graphics_settings = game_info.get("graphics_settings", {})
    
    # Обработка названия игры
    title = game_info.get("title", "").strip().lower()
    if not title:
        raise ValueError("Название игры (title) обязательно и не может быть пустым")
    
    # Валидация качества графики
    quality = graphics_settings.get("quality", "medium").lower()
    if quality not in ["low", "medium", "high", "ultra"]:
        quality = "medium"
    
    result = {
        "title": title,
        "graphics": {
            "quality": quality,
            "target_fps": int(graphics_settings.get("target_fps", 60)),
            "resolution": str(graphics_settings.get("resolution", "1920x1080")),
            "ray_tracing": bool(graphics_settings.get("ray_tracing", False)),
            "dlss": graphics_settings.get("dlss", "disabled").lower(),
            "fsr": graphics_settings.get("fsr", "disabled").lower()
        }
    }
    
    return result


def parse_budget_settings(budget_data):
    """Парсим бюджет и метод распределения"""
    result = {
        "amount": int(budget_data.get("amount", 0)),
        "allocation_method": budget_data.get("budget_allocation_method", "priority_based").lower()
    }
    return result


def parse_components(components_data):
    """Парсим списки компонентов"""
    result = {
        "mandatory": {
            k: v.lower() if isinstance(v, str) else v
            for k, v in components_data.get("mandatory", {}).items()
        },
        "optional": {
            k: v.lower() if isinstance(v, str) else v
            for k, v in components_data.get("optional", {}).items()
        }
    }
    return result


def parse_allocation_block(allocation_section: dict, method: str) -> dict:
    if not isinstance(allocation_section, dict):
        return {}

    method = method.lower()
    key_map = {
        "priority_based": "_priority",
        "percentage_based": "_percentage",
        "fixed_price_based": "_max_price"
    }

    suffix = key_map.get(method)
    method_data = allocation_section.get(method, {})

    if not method_data or not suffix:
        return {}

    if method == "priority_based":
        parsed = {
            k.replace(suffix, "") + suffix: str(v).capitalize()
            for k, v in method_data.items()
            if isinstance(v, str)
        }
    elif method == "percentage_based" or method == "fixed_price_based":
        parsed = {
            k.replace(suffix, "") + suffix: int(v)
            for k, v in method_data.items()
            if isinstance(v, (int, float, str)) and str(v).isdigit()
        }
    else:
        parsed = {}

    return {
        "method": method,
        method: parsed
    }


def parse_user_request(data):
    try:
        selections = data.get("user_selections", {})

        # Парсим настройки игры
        game = parse_game_settings(selections.get("game", {}))
        # Парсим бюджет
        budget = parse_budget_settings(selections.get("budget", {}))
        # Парсим компоненты
        components = parse_components(selections.get("components", {}))

        comp_section = selections.get("components", {})
        mand_alloc = comp_section.get("mandatory_allocation", {})
        opt_alloc = comp_section.get("optional_allocation", {})

        mand_method = mand_alloc.get("method", budget["allocation_method"]).lower()
        opt_method = opt_alloc.get("method", budget["allocation_method"]).lower()

        allocations = {
            "mandatory": parse_allocation_block(mand_alloc, mand_method),
            "optional": parse_allocation_block(opt_alloc, opt_method)
        }

        return {
            "game": game,
            "budget": budget,
            "components": components,
            "allocations": allocations
        }
    except Exception as e:
        raise ValueError(f"Parsing error: {str(e)}")



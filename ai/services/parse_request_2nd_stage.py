def parse_budget_settings(budget_data):
    """Парсим бюджет и метод распределения"""
    result = {
        "amount": int(budget_data.get("amount", 0)),
        "currency": budget_data.get("currency", "RUB").upper(),
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

def parse_allocation_settings(allocation_data, method):
    if not isinstance(allocation_data, dict):
        return {}

    allocation_data = {k.lower(): v for k, v in allocation_data.items()}

    # Нормализуем метод — убираем суффикс "_based", если есть
    if method.endswith("_based"):
        method = method[:-6]  # удаляем последние 6 символов

    method_key = f"{method}_based"  # теперь точно корректно

    method_data = allocation_data.get(method_key, {})

    if not method_data:
        return {}

    if method == "priority":
        return {
            k.replace("_priority", ""): v.lower()
            for k, v in method_data.items()
            if isinstance(v, str)
        }
    elif method == "percentage":
        return {
            k.replace("_percentage", ""): int(v)
            for k, v in method_data.items()
            if isinstance(v, int)
        }
    elif method == "fixed_price":
        return {
            k.replace("_max_price", ""): int(v)
            for k, v in method_data.items()
            if isinstance(v, int)
        }
    return {}



def parse_user_request(data):
    try:
        selections = data.get("user_selections", {})

        budget = parse_budget_settings(selections.get("budget", {}))
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
            "budget": budget,
            "components": components,
            "allocations": allocations
        }
    except Exception as e:
        raise ValueError(f"Parsing error: {str(e)}")

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

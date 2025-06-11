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
    """Парсим правила распределения бюджета"""
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

def parse_user_request(data):
    try:
        selections = data["user_selections"]
        
        return {
            "budget": parse_budget_settings(selections.get("budget", {})),
            "components": parse_components(selections.get("components", {})),
            "allocations": {
                "mandatory": parse_allocation_settings(
                    selections.get("components", {}).get("mandatory_allocation", {}),
                    selections.get("budget", {}).get("budget_allocation_method", "priority_based")
                ),
                "optional": parse_allocation_settings(
                    selections.get("components", {}).get("optional_allocation", {}),
                    selections.get("budget", {}).get("budget_allocation_method", "priority_based")
                )
            }
        }
    except Exception as e:
        raise ValueError(f"Parsing error: {str(e)}")
    
    
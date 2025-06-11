def parse_game_settings(game_data):
    """Парсим настройки игры с валидацией данных"""
    if not isinstance(game_data, dict):
        raise ValueError("game_data должен быть словарем")
    
    # Получаем user_selections или пустой словарь
    user_selections = game_data.get("user_selections", {})
    if not isinstance(user_selections, dict):
        raise ValueError("user_selections должен быть словарем")
    
    # Получаем настройки игры
    game_info = user_selections.get("game", {})
    graphics_settings = game_info.get("graphics_settings", {})
    
    # Обработка названия игры
    title = game_info.get("title", "").strip().lower()
    if not title:
        raise ValueError("Название игры (title) обязательно и не может быть пустым")
    
    # Валидация качества графики
    quality = graphics_settings.get("quality", "medium").lower()
    if quality not in ["low", "medium", "high", "ultra"]:
        quality = "medium"  # Значение по умолчанию, если указано некорректное
    
    # Создаем результат
    result = {
        "title": title,
        "graphics": {
            "quality": quality,
            "target_fps": int(graphics_settings.get("target_fps", 60)),
            "resolution": str(graphics_settings.get("resolution", "1920x1080")),
            "ray_tracing": bool(graphics_settings.get("ray_tracing", False)),
            "dlss": graphics_settings.get("dlss", "disabled").lower(),
            "fsr": graphics_settings.get("fsr", "disabled").lower()
        },
        "budget": user_selections.get("budget", {}),
        "components": user_selections.get("components", {})
    }
    
    return result

    
    
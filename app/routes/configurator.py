# app/routes/configurator.py
from flask import render_template, Blueprint, request, jsonify
import json

configurator = Blueprint('configurator', __name__)

@configurator.route('/configurator')
def index():
    return render_template('configurator/index.html', title='Конфигуратор')

@configurator.route('/configurator/log-click', methods=['POST'])
def log_click():
    data = request.get_json()
    game_name = data.get('gameName', '')
    graphics_quality = data.get('graphicsQuality', 'High')
    target_fps = data.get('targetFps', 60)
    resolution = data.get('resolution', 1080)
    ray_tracing = data.get('rayTracingEnabled', False)
    dlss_value = data.get('dlss', 'off')
    fsr_value = data.get('fsr', 'off')
    budget_amount = data.get('budgetAmount', 150000)
    budget_allocation_method = data.get('budgetAllocationMethod', 'fixed_price_based')

    if game_name:
        game_name = game_name.replace(' ', '_')
    else:
        game_name = "Unknown"

    # Валидация качества графики
    valid_qualities = {"Low", "Medium", "High", "Ultra"}
    if graphics_quality not in valid_qualities:
        graphics_quality = "High"

    # Валидация FPS
    try:
        target_fps = int(target_fps)
        valid_fps = {30, 60, 120, 144, 240}
        if target_fps not in valid_fps:
            target_fps = 60
    except (ValueError, TypeError):
        target_fps = 60

    # Валидация разрешения
    try:
        resolution = int(resolution)
        valid_resolutions = {720, 1080, 1440, 2160}
        if resolution not in valid_resolutions:
            resolution = 1080
    except (ValueError, TypeError):
        resolution = 1080

    # Валидация бюджета
    try:
        budget_amount = int(budget_amount)
        if budget_amount < 50000 or budget_amount > 450000:
            budget_amount = 150000
    except (ValueError, TypeError):
        budget_amount = 150000

    # Валидация метода бюджета
    if budget_allocation_method not in ["fixed_price_based", "percentage_based"]:
        budget_allocation_method = "fixed_price_based"

    # Маппинг значений масштабирования
    dlss_mapping = {
        "off": "Disabled",
        "dlss-quality": "Quality",
        "dlss-balanced": "Balanced",
        "dlss-performance": "Performance",
        "dlss-ultra-performance": "Ultra Performance"
    }
    dlss_setting = dlss_mapping.get(dlss_value, "Disabled")

    fsr_mapping = {
        "off": "Disabled",
        "fsr-quality": "Quality",
        "fsr-balanced": "Balanced",
        "fsr-performance": "Performance",
        "fsr-ultra-performance": "Ultra Performance"
    }
    fsr_setting = fsr_mapping.get(fsr_value, "Disabled")

    log_data = {
        "user_selections": {
            "game": {
                "title": game_name,
                "graphics_settings": {
                    "quality": graphics_quality,
                    "target_fps": target_fps,
                    "resolution": resolution,
                    "ray_tracing": bool(ray_tracing),
                    "dlss": dlss_setting,
                    "fsr": fsr_setting
                }
            },
            "budget": {
                "amount": budget_amount,
                "budget_allocation_method": budget_allocation_method
            }
        }
    }
    print(json.dumps(log_data, ensure_ascii=False, indent=2))

    return jsonify({"status": "ok"}), 200
# app/routes/configurator.py
from flask import render_template, Blueprint, request, jsonify
import json
from app.ai.main import main as ai_main

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
    components = data.get('components', {})

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

    # Валидация данных о комплектующих
    def validate_component(value, default="any"):
        if not value or value == "any":
            return default
        return str(value)[:100]  # Ограничиваем длину строки

    def validate_percentage(value, default=0, min_val=0, max_val=100):
        try:
            value = int(value)
            return max(min_val, min(value, max_val))
        except (ValueError, TypeError):
            return default

    def validate_price(value, default=0, min_val=0, max_val=300000):
        try:
            value = int(value)
            return max(min_val, min(value, max_val))
        except (ValueError, TypeError):
            return default

    def validate_cooler_type(value):
        valid_types = {"included_with_cpu", "water_cooling", "air_cooler", "any"}
        return value if value in valid_types else "any"

    # Обрабатываем данные о комплектующих
    mandatory = components.get('mandatory', {})
    mandatory_allocation = components.get('mandatory_allocation', {})
    optional = components.get('optional', {})
    optional_allocation = components.get('optional_allocation', {})

    validated_components = {
        "mandatory": {
            "cpu": validate_component(mandatory.get('cpu')),
            "gpu": validate_component(mandatory.get('gpu')),
            "dimm": validate_component(mandatory.get('dimm')),
            "ssd_m2": validate_component(mandatory.get('ssd_m2')),
            "motherboard": validate_component(mandatory.get('motherboard')),
            "power_supply": validate_component(mandatory.get('power_supply'))
        },
        "mandatory_allocation": {
            "method": budget_allocation_method
        },
        "optional": {
            "case_fan": validate_component(optional.get('case_fan')),
            "pc_case": validate_component(optional.get('pc_case')),
            "cpu_cooler": validate_cooler_type(optional.get('cpu_cooler', 'any'))
        },
        "optional_allocation": {
            "method": budget_allocation_method
        }
    }

    if budget_allocation_method == "percentage_based":
        # Валидация обязательных компонентов
        mandatory_percentage = mandatory_allocation.get('percentage_based', {})
        validated_components["mandatory_allocation"]["percentage_based"] = {
            "cpu_percentage": validate_percentage(mandatory_percentage.get('cpu_percentage', 25)),  # 25% по умолчанию
            "gpu_percentage": validate_percentage(mandatory_percentage.get('gpu_percentage', 35)),  # 35%
            "dimm_percentage": validate_percentage(mandatory_percentage.get('dimm_percentage', 8)),  # 8%
            "ssd_m2_percentage": validate_percentage(mandatory_percentage.get('ssd_m2_percentage', 7)),  # 7%
            "motherboard_percentage": validate_percentage(mandatory_percentage.get('motherboard_percentage', 8)),  # 8%
            "power_supply_percentage": validate_percentage(mandatory_percentage.get('power_supply_percentage', 7))  # 7%
        }
        
        # Валидация дополнительных компонентов
        optional_percentage = optional_allocation.get('percentage_based', {})
        validated_components["optional_allocation"]["percentage_based"] = {
            "case_fan_percentage": validate_percentage(optional_percentage.get('case_fan_percentage', 3)),  # 3%
            "pc_case_percentage": validate_percentage(optional_percentage.get('pc_case_percentage', 5)),  # 5%
            "cpu_cooler_percentage": validate_percentage(optional_percentage.get('cpu_cooler_percentage', 2))  # 2%
        }
    else:
        # Валидация обязательных компонентов
        mandatory_fixed = mandatory_allocation.get('fixed_price_based', {})
        validated_components["mandatory_allocation"]["fixed_price_based"] = {
            "cpu_max_price": validate_price(mandatory_fixed.get('cpu_max_price', 30000)),  # 30k ₽
            "gpu_max_price": validate_price(mandatory_fixed.get('gpu_max_price', 60000)),  # 60k ₽
            "dimm_max_price": validate_price(mandatory_fixed.get('dimm_max_price', 10000)),  # 10k ₽
            "ssd_m2_max_price": validate_price(mandatory_fixed.get('ssd_m2_max_price', 8000)),  # 8k ₽
            "motherboard_max_price": validate_price(mandatory_fixed.get('motherboard_max_price', 12000)),  # 12k ₽
            "power_supply_max_price": validate_price(mandatory_fixed.get('power_supply_max_price', 8000))  # 8k ₽
        }
        
        # Валидация дополнительных компонентов
        optional_fixed = optional_allocation.get('fixed_price_based', {})
        validated_components["optional_allocation"]["fixed_price_based"] = {
            "case_fan_max_price": validate_price(optional_fixed.get('case_fan_max_price', 3000)),  # 3k ₽
            "pc_case_max_price": validate_price(optional_fixed.get('pc_case_max_price', 7000)),  # 7k ₽
            "cpu_cooler_max_price": validate_price(optional_fixed.get('cpu_cooler_max_price', 5000))  # 5k ₽
        }

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
            },
            "components": validated_components
        }
    }
    print(json.dumps(log_data, ensure_ascii=False, indent=2))
    
    result = ai_main(log_data)
    return jsonify({
        "status": "ok",
        "result": result  # если тебе нужно вернуть результат клиенту
    }), 200
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
    resolution = data.get('resolution', 1080)  # Новый параметр

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

    log_data = {
        "user_selections": {
            "game": {
                "title": game_name,
                "graphics_settings": {
                    "quality": graphics_quality,
                    "target_fps": target_fps,
                    "resolution": resolution
                }
            }
        }
    }
    print(json.dumps(log_data, ensure_ascii=False, indent=2))

    return jsonify({"status": "ok"}), 200
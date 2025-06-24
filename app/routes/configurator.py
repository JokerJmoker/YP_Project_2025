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

    # Валидация и замена пробелов на _
    if game_name:
        game_name = game_name.replace(' ', '_')
    else:
        game_name = "Unknown"

    log_data = {
        "user_selections": {
            "game": {
                "title": game_name
            }
        }
    }
    print(json.dumps(log_data, ensure_ascii=False, indent=2))

    return jsonify({"status": "ok"}), 200
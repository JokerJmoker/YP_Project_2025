# app/routes/configurator.py
from flask import render_template, Blueprint, request, jsonify

configurator = Blueprint('configurator', __name__)

@configurator.route('/configurator')
def index():
    return render_template('configurator/index.html', title='Конфигуратор')

@configurator.route('/configurator/log-click', methods=['POST'])
def log_click():
    data = request.get_json()
    game_id = data.get('gameId')
    game_name = data.get('gameName')
    timestamp = data.get('timestamp')

    print(f"[LOG] Click on: {game_name} (ID: {game_id}) at {timestamp}")

    return jsonify({"status": "ok"}), 200

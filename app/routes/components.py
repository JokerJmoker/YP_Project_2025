# app/routes/components.py
from flask import render_template, Blueprint, jsonify, request
from app.ai.main import main as ai_main

components = Blueprint('components', __name__)

@components.route('/components')
def index():
    initial_data = {}  # Или наполни нужными начальными данными, если есть
    return render_template(
        'components/index.html',
        title='Компоненты',
        initial_data=initial_data
    )

@components.route('/api/components/result', methods=['GET'])
def get_components_result():
    """
    GET endpoint для получения результатов подбора компонентов.
    Можно использовать:
    1. Передачу ID конфигурации через параметры URL
    2. Хранение данных в сессии
    3. Получение последнего результата из БД/кеша
    """
    try:
        # Вариант 1: Получение через query параметры
        config_id = request.args.get('config_id')
        
        # Вариант 2: Из сессии (если вы сохранили результат после POST /configurator/log-click)
        # server_data = session.get('pc_configuration')
        
        if not config_id:
            return jsonify({
                "status": "error",
                "message": "Configuration ID not provided"
            }), 400

        # Здесь должна быть логика получения данных по ID
        # Например, из базы данных или кеша
        # В демонстрационных целях просто возвращаем тестовые данные
        example_data = {
            "status": "ok",
            "config_id": config_id,
            "components": {
                "cpu": "Intel Core i7-13700K",
                "gpu": "NVIDIA RTX 4070 Ti",
                # ... другие компоненты
            }
        }
        
        return jsonify(example_data), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500
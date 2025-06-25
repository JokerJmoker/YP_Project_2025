# app/routes/components.py
from flask import render_template, Blueprint, jsonify, request
from app.ai.main import main as ai_main

from datetime import datetime
from flask import session
import json 

components = Blueprint('components', __name__)

@components.route('/components')
def index():
    return render_template('components/index.html',title='Компоненты')

@components.route('/api/components/result', methods=['GET'])
def get_components_result():
    try:
        print("\n=== НАЧАЛО ОБРАБОТКИ GET ЗАПРОСА НА КОМПОНЕНТЫ ===")
        
        # Логируем полученные параметры
        config_id = request.args.get('config_id')
        print(f"[DEBUG] Полученный config_id: {config_id}")
        print(f"[DEBUG] Все параметры запроса: {request.args}")

        if not config_id:
            print("[ERROR] Отсутствует config_id в запросе")
            return jsonify({
                "status": "error",
                "message": "Configuration ID not provided"
            }), 400

        # Получаем сохраненные конфигурации из сессии
        pc_configurations = session.get('pc_configurations', {})
        print(f"[DEBUG] Всего конфигураций в сессии: {len(pc_configurations)}")
        
        # Логируем доступные ID конфигураций для отладки
        if pc_configurations:
            print("[DEBUG] Доступные config_ids в сессии:")
            for cid in pc_configurations.keys():
                print(f" - {cid}")
        
        # Получаем запрошенную конфигурацию
        config_data = pc_configurations.get(config_id)
        
        if not config_data:
            print(f"[ERROR] Конфигурация с ID {config_id} не найдена")
            return jsonify({
                "status": "error",
                "message": "Configuration not found"
            }), 404
        
        print(f"[DEBUG] Найдена конфигурация с timestamp: {config_data['timestamp']}")
        print("[DEBUG] Пример данных компонентов:")
        print(json.dumps(config_data['result'], indent=2, ensure_ascii=False))
                
        # Формируем успешный ответ
        response_data = {
            "status": "ok",
            "config_id": config_id,
            "user_selections": config_data['user_selections'],
            "components": config_data['result'],
            "timestamp": config_data['timestamp']
        }
        
        print("\n[DEBUG] Отправляемый ответ:")
        print(json.dumps(response_data, indent=2))
        print("=== УСПЕШНОЕ ЗАВЕРШЕНИЕ ОБРАБОТКИ ===")
        
        return jsonify(response_data), 200

    except Exception as e:
        print(f"\n[ERROR] Критическая ошибка: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": "Internal server error",
            "details": str(e)
        }), 500
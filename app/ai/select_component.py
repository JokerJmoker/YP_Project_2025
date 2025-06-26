from flask import Blueprint, request, jsonify
from datetime import datetime
import json
import logging
from ai_db.database import Database
from services.file_handler_request import select_json_file, load_json_data
from services.request_processor_1st_stage import get_game_recommendation
from services.request_processor_2nd_stage import get_propriate_components
from select_componet_1st_stage.get_component_by_name import process_component_lookup
from select_componet_2nd_stage.cpu import run_cpu_selection_test
from select_componet_2nd_stage.gpu import run_gpu_selection_test
from select_componet_2nd_stage.ssd_m2 import run_ssd_m2_selection_test
from select_componet_2nd_stage.dimm import run_dimm_selection_test 
from select_componet_2nd_stage.motherboard import run_motherboard_selection_test
from select_componet_2nd_stage.power_supply import run_power_supply_selection_test
from select_componet_2nd_stage.cpu_cooler import run_cpu_cooler_selection_test
from select_componet_2nd_stage.case_fan import run_case_fan_selection_test
from select_componet_2nd_stage.pc_case import run_pc_case_selection_test

api = Blueprint('api', __name__)

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_configuration(data):
    """Основная функция обработки конфигурации"""
    try:
        with Database() as conn:
            # Первый этап - получение рекомендаций по игре
            result_1st_stage = get_game_recommendation(conn, data)
            
            # Второй этап - получение совместимых компонентов
            result_2nd_stage = get_propriate_components(conn, data)
            
            # Подбор конкретных компонентов
            chosen_gpu = run_gpu_selection_test(result_1st_stage, result_2nd_stage)
            chosen_cpu = run_cpu_selection_test(result_1st_stage, result_2nd_stage, chosen_gpu)
            chosen_cpu_cooler = run_cpu_cooler_selection_test(result_2nd_stage, chosen_cpu)
            chosen_ssd_m2 = run_ssd_m2_selection_test(result_1st_stage, result_2nd_stage)
            chosen_dimm = run_dimm_selection_test(result_1st_stage, result_2nd_stage, chosen_cpu)
            chosen_motherboard = run_motherboard_selection_test(
                result_2nd_stage, chosen_cpu, chosen_gpu, chosen_dimm, chosen_ssd_m2
            )
            chosen_power_supply = run_power_supply_selection_test(
                result_2nd_stage, chosen_cpu, chosen_gpu, chosen_motherboard
            )
            chosen_case_fan = run_case_fan_selection_test(result_2nd_stage, chosen_power_supply)
            chosen_pc_case = run_pc_case_selection_test(
                result_2nd_stage, chosen_gpu, chosen_cpu_cooler, 
                chosen_motherboard, chosen_power_supply, chosen_case_fan
            )
            
            # Формируем итоговую конфигурацию
            config = {
                "cpu": chosen_cpu,
                "gpu": chosen_gpu,
                "cpu_cooler": chosen_cpu_cooler,
                "ssd_m2": chosen_ssd_m2,
                "dimm": chosen_dimm,
                "motherboard": chosen_motherboard,
                "power_supply": chosen_power_supply,
                "case_fan": chosen_case_fan,
                "pc_case": chosen_pc_case,
                "timestamp": datetime.now().isoformat()
            }
            
            return config
            
    except Exception as e:
        logger.error(f"Error processing configuration: {str(e)}")
        raise

@api.route('/api/build-config', methods=['POST'])
def handle_build_config():
    try:
        # Получаем и валидируем данные
        data = request.get_json()
        
        if not data or 'user_selections' not in data:
            return jsonify({"error": "Invalid request format"}), 400
        
        user_selections = data['user_selections']
        
        # Логируем полученные данные
        logger.info(f"Received build config at {datetime.now()}: {json.dumps(data, indent=2)}")
        
        # Обрабатываем конфигурацию
        config = process_configuration(user_selections)
        
        # Рассчитываем распределение бюджета
        budget_info = calculate_budget_distribution(user_selections)
        
        # Формируем ответ
        response = {
            "status": "success",
            "config_id": f"config_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "configuration": config,
            "budget_distribution": budget_info,
            "message": "Конфигурация успешно собрана"
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing build config: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e),
            "message": "Произошла ошибка при обработке вашей конфигурации"
        }), 500

def calculate_budget_distribution(config):
    """Рассчитывает распределение бюджета по компонентам"""
    try:
        budget = config['budget']['amount']
        method = config['budget']['budget_allocation_method']
        
        if method == 'percentage_based':
            mandatory = config['components']['mandatory_allocation']['percentage_based']
            optional = config['components']['optional_allocation']['percentage_based']
            
            distribution = {
                "cpu": budget * mandatory['cpu_percentage'] / 100,
                "gpu": budget * mandatory['gpu_percentage'] / 100,
                "dimm": budget * mandatory['dimm_percentage'] / 100,
                "ssd_m2": budget * mandatory['ssd_m2_percentage'] / 100,
                "motherboard": budget * mandatory['motherboard_percentage'] / 100,
                "power_supply": budget * mandatory['power_supply_percentage'] / 100,
                "case_fan": budget * optional['case_fan_percentage'] / 100,
                "pc_case": budget * optional['pc_case_percentage'] / 100,
                "cpu_cooler": budget * optional['cpu_cooler_percentage'] / 100
            }
            
            return {
                "method": "percentage_based",
                "distribution": distribution,
                "total": sum(distribution.values())
            }
            
        else:  # fixed_price_based
            mandatory = config['components']['mandatory_allocation']['fixed_price_based']
            optional = config['components']['optional_allocation']['fixed_price_based']
            
            distribution = {
                "cpu": mandatory['cpu_max_price'],
                "gpu": mandatory['gpu_max_price'],
                "dimm": mandatory['dimm_max_price'],
                "ssd_m2": mandatory['ssd_m2_max_price'],
                "motherboard": mandatory['motherboard_max_price'],
                "power_supply": mandatory['power_supply_max_price'],
                "case_fan": optional['case_fan_max_price'],
                "pc_case": optional['pc_case_max_price'],
                "cpu_cooler": optional['cpu_cooler_max_price']
            }
            
            return {
                "method": "fixed_price_based",
                "distribution": distribution,
                "total": sum(distribution.values())
            }
            
    except Exception as e:
        logger.error(f"Error calculating budget distribution: {str(e)}")
        return {"error": str(e)}
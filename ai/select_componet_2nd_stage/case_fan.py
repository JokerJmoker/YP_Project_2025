from typing import Dict, Any
from psycopg2.extras import DictCursor
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.case_fan import CaseFanModel

def select_cooling_system(
    input_data_2nd_stage: Dict[str, Any],
    chosen_power_supply: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Подбирает систему охлаждения на основе:
    - сертификата блока питания (определяет минимальный CFM)
    - бюджета
    - предпочтений по размеру корпуса
    """
    print("\n[DEBUG] ===== НАЧАЛО ПОДБОРА СИСТЕМЫ ОХЛАЖДЕНИЯ =====")
    
    # 1. Определяем минимальные требования к воздушному потоку
    certification = chosen_power_supply.get("certification_80plus", "Standard")
    required_cfm = {
        "Standard": 25.5,
        "Bronze": 38.25,
        "Silver": 51.0,
        "Gold": 63.75,
        "Platinum": 76.5,
        "Titanium": 89.25
    }.get(certification, 25.5)
    
    print(f"[DEBUG] Требуемый воздушный поток: {required_cfm} CFM (сертификат: {certification})")

    # 2. Рассчитываем максимальный бюджет
    user_request = input_data_2nd_stage["user_request"]
    if user_request["allocations"]["optional"]["method"] == "percentage_based":
        cooling_percentage = user_request["allocations"]["optional"]["percentage_based"]["cooling_percentage"]
        max_price = round((cooling_percentage / 100) * user_request["budget"]["amount"])
    else:
        max_price = user_request["allocations"]["optional"]["fixed_price_based"]["cooling_max_price"]
    
    print(f"[DEBUG] Максимальный бюджет: {max_price} руб.")

    # 3. Проверяем предпочтения по размеру корпуса
    pc_case_pref = user_request["components"]["optional"].get("pc_case", "any")
    size_condition = "AND (fan_size ~ '^[0-9]+$' OR fan_size ~ '120')" if pc_case_pref == "small_size" else ""
    print(f"[DEBUG] Предпочтения по корпусу: {pc_case_pref}")

    # 4. Формируем и выполняем основной запрос
    query = f"""
        SELECT 
            id, name, price,
            fan_size, fan_thickness,
            max_rotation_speed, min_rotation_speed,
            max_airflow, max_static_pressure,
            max_noise_level, min_noise_level,
            power_connector_type
        FROM pc_components.case_fan
        WHERE price <= %s
        {size_condition}
        ORDER BY 
            price DESC,
            CASE 
                WHEN max_airflow ~ '[0-9]' THEN 
                    CAST(SUBSTRING(max_airflow FROM '[0-9]+\.?[0-9]*') AS FLOAT)
                ELSE 0
            END DESC
        LIMIT 1
    """
    
    print(f"[DEBUG] Выполняем основной запрос с бюджетом {max_price} руб.")
    
    with Database() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(query, (max_price,))
            result = cursor.fetchone()
            
            if not result:
                # 5. Fallback: если не найдено по основному запросу
                print("[DEBUG] Не найдено по основному запросу, пробуем fallback")
                fallback_query = f"""
                    SELECT 
                        id, name, price,
                        fan_size, max_airflow
                    FROM pc_components.case_fan
                    WHERE price <= %s
                    {size_condition}
                    ORDER BY price ASC
                    LIMIT 1
                """
                cursor.execute(fallback_query, (max_price,))
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError("Не удалось найти подходящую систему охлаждения в рамках бюджета")
                
                print(f"[DEBUG] Найден fallback вариант: {result['name']}")

            # 6. Валидация и преобразование данных через модель
            try:
                fan_model = CaseFanModel.from_orm(result)
                actual_cfm = fan_model.max_airflow or 0
                
                if actual_cfm < required_cfm:
                    print(f"[WARNING] Фактический CFM ({actual_cfm}) ниже требуемого ({required_cfm})")
                
                print("\n[DEBUG] ===== РЕЗУЛЬТАТ ПОДБОРА =====")
                print(f"Модель: {fan_model.name}")
                print(f"Воздушный поток: {actual_cfm} CFM")
                print(f"Размер: {fan_model.fan_size} мм")
                print(f"Цена: {fan_model.price} руб.")
                
                return fan_model.model_dump()
            
            except Exception as e:
                raise ValueError(f"Ошибка обработки данных вентилятора: {str(e)}")

def run_cooling_selection_test(
    input_data_2nd_stage: Dict[str, Any],
    chosen_power_supply: Dict[str, Any]
) -> None:
    """Тестовая функция для проверки подбора охлаждения"""
    print("===== ТЕСТИРОВАНИЕ ПОДБОРА СИСТЕМЫ ОХЛАЖДЕНИЯ =====")
    try:
        cooling_info = select_cooling_system(input_data_2nd_stage, chosen_power_supply)
        print("\nРезультат:")
        print(json.dumps(cooling_info, indent=2, ensure_ascii=False))
    except ValueError as e:
        print(f"\nОшибка: {e}")

# Пример вызова тестовой функции
if __name__ == "__main__":
    
    
    input_data_2nd_stage = {
    "status": "success",
    "message": "Данные пользователя успешно разобраны.",
    "user_request": {
        "game": {
        "title": "cyberpunk_2077",
        "graphics": {
            "quality": "high",
            "target_fps": 240,
            "resolution": "1080",
            "ray_tracing": False,
            "dlss": "disabled",
            "fsr": "disabled"
        }
        },
        "budget": {
        "amount": 120000,
        "allocation_method": "percentage_based"
        },
        "components": {
        "mandatory": {
            "cpu": "any",
            "gpu": "any",
            "dimm": "any",
            "ssd_m2": "any",
            "motherboard": "any",
            "power_supply": "any"
        },
        "optional": {
            "cooling": "any",
            "pc_case": "small_size",
            "cpu_cooler": "any"
        }
        },
        "allocations": {
        "mandatory": {
            "method": "percentage_based",
            "percentage_based": {
            "cpu_percentage": 25,
            "gpu_percentage": 40,
            "dimm_percentage": 40,
            "ssd_m2_percentage": 15,
            "motherboard_percentage": 20,
            "power_supply_percentage": 15
            }
        },
        "optional": {
            "method": "percentage_based",
            "percentage_based": {
            "cooling_percentage": 3,
            "pc_case_percentage": 1,
            "cpu_cooler_percentage": 1
            }
        }
        }
    }
    }

    chosen_power_supply = {
        "id": 878,
        "name": "Блок питания Thermaltake Toughpower GF A3 Snow 850W - TT Premium Edition [PS-TPD-0850FNFAGE-N] белый",
        "price": 15299,
        "wattage": 850,
        "form_factor": "ATX",
        "cable_management": "полностью модульный",
        "cable_sleeving": False,
        "main_connector": "24 pin",
        "cpu_connectors": "2 x 4+4 pin",
        "pcie_connectors": "5 x 6+2 pin, 16 pin (12VHPWR)",
        "sata_connectors": 8,
        "molex_connectors": 8,
        "floppy_connector": True,
        "cooling_type": "активная",
        "fan_size": 120120,
        "hybrid_mode": True,
        "certification_80plus": "Gold",
        "pfc_type": "активный",
        "length": 140,
        "width": 150,
        "height": 86,
        "weight": 2.89
    }
    run_cooling_selection_test(input_data_2nd_stage, chosen_power_supply)
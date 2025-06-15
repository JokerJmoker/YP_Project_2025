import datetime
from typing import Dict, Any, Optional
from psycopg2.extras import DictCursor
import sys
import os
import json
import re
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.ai_db.database import Database
from ai.models.components.power_supply import PowerSupplyModel

def map_motherboard_to_psu_form_factor(mb_form_factor: str) -> str:
    """Сопоставляет форм-фактор материнской платы с форм-фактором блока питания"""
    mapping = {
        "E-ATX": "ATX",
        "Micro-ATX": "ATX",
        "Mini-DTX": "ATX",
        "Mini-ITX": "SFX",  # Чаще используют SFX для Mini-ITX
        "SSI EEB": "ATX",
        "Standard-ATX": "ATX",
        "нестандартный": "ATX"  # По умолчанию ATX для нестандартных
    }
    return mapping.get(mb_form_factor, "ATX")

# Настройка логгера
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import re
from typing import Dict, Any

def get_recommended_certification(gpu_info: Dict[str, Any]) -> str:
    """
    Определяет рекомендуемый стандарт 80 Plus на основе модели видеокарты.
    Учитывает TDP, производителя и класс видеокарты.
    
    Args:
        gpu_info: Словарь с информацией о видеокарте
        
    Returns:
        Рекомендуемый сертификат 80 Plus (Titanium, Platinum, Gold, Bronze)
    """
    # Получаем модель из правильного поля
    gpu_model = gpu_info.get("gpu_model", "").lower()
    gpu_tdp = gpu_info.get("tdp", 0)
    
    try:
        # Для видеокарт NVIDIA
        if "rtx" in gpu_model or "geforce" in gpu_model:
            # Ищем номер модели в строке
            model_number_match = re.search(r'rtx?\s*(\d{4})', gpu_model) or re.search(r'(\d{4})', gpu_model)
            if not model_number_match:
                return "Bronze"
                
            model_number = int(model_number_match.group(1))
            
            # RTX 40/50 серия
            if model_number >= 5090:
                return "Titanium"
            elif model_number >= 5080:
                return "Platinum"
            elif model_number >= 5070:
                return "Gold" if gpu_tdp < 300 else "Platinum"
            elif model_number >= 5060:
                return "Gold"
            else:
                return "Bronze"
        
        # Для видеокарт AMD
        elif "rx" in gpu_model or "radeon" in gpu_model:
            # Ищем номер модели в строке
            model_number_match = re.search(r'rx\s*(\d{4})', gpu_model) or re.search(r'(\d{4})', gpu_model)
            if not model_number_match:
                return "Bronze"
                
            model_number = int(model_number_match.group(1))
            
            if model_number >= 7900:
                return "Platinum"
            elif model_number >= 7800:
                return "Gold" if gpu_tdp < 300 else "Platinum"
            elif model_number >= 7600:
                return "Gold"
            else:
                return "Bronze"
        
        # Для интегрированной графики и бюджетных решений
        return "Bronze"
        
    except Exception:
        return "Bronze"

def find_similar_power_supply(
    input_data_2nd_stage: Dict[str, Any],
    chosen_cpu: Dict[str, Any],
    chosen_gpu: Dict[str, Any],
    chosen_motherboard: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Подбор блока питания с учётом:
    - Если у GPU tdp None, используем recommended_psu без суммирования с CPU.
    - Иначе суммируем tdp CPU + tdp GPU с запасом.
    - Оптимизация по цене и форм-фактору.
    """
    try:
        user_request = input_data_2nd_stage["user_request"]
        method = user_request["allocations"]["mandatory"]["method"]

        if method == "fixed_price_based":
            max_price = user_request["allocations"]["mandatory"][method]["power_supply_max_price"]
            target_price = max_price * 0.9
        elif method == "percentage_based":
            total_budget = user_request["budget"]["amount"]
            ps_percentage = user_request["allocations"]["mandatory"][method]["power_supply_percentage"]
            max_price = round((ps_percentage / 100) * total_budget)
            target_price = max_price * 0.85
        else:
            raise ValueError(f"Unsupported allocation method: {method}")

        cpu_power = max(chosen_cpu.get("tdp", 0) or 0, chosen_cpu.get("base_tdp", 0) or 0)

        gpu_tdp = chosen_gpu.get("tdp")
        recommended_psu_wattage = chosen_gpu.get("recommended_psu")

        # Если tdp у GPU None, то используем recommended_psu как требуемую мощность (без сложения с CPU)
        if gpu_tdp is None:
            required_wattage = recommended_psu_wattage or 550  # запас по умолчанию, если None
        else:
            # Иначе суммируем tdp CPU + GPU
            gpu_power = gpu_tdp
            power_multiplier = 1.3 if gpu_power >= 250 else 1.2
            required_wattage = (cpu_power + gpu_power) * power_multiplier

        # Округляем к ближайшему стандартному значению из списка
        standard_wattages = [550, 650, 750, 850, 1000, 1200, 1600]
        required_wattage = min((w for w in standard_wattages if w >= required_wattage), default=1600)

        mb_form_factor = chosen_motherboard.get("form_factor", "Standard-ATX")
        psu_form_factor = map_motherboard_to_psu_form_factor(mb_form_factor)

        recommended_cert = get_recommended_certification(chosen_gpu)

        with Database() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT *,
                        ABS(price - %s) AS price_diff,
                        CASE 
                            WHEN certification_80plus = %s THEN 0
                            WHEN certification_80plus LIKE '%%Titanium%%' THEN 1
                            WHEN certification_80plus LIKE '%%Platinum%%' THEN 2
                            WHEN certification_80plus LIKE '%%Gold%%' THEN 3
                            WHEN certification_80plus LIKE '%%Silver%%' THEN 4
                            WHEN certification_80plus LIKE '%%Bronze%%' THEN 5
                            ELSE 6
                        END AS cert_priority
                    FROM pc_components.power_supply
                    WHERE CAST(NULLIF(REGEXP_REPLACE(wattage, '[^0-9]', '', 'g'), '') AS INTEGER) >= %s
                    AND form_factor = %s
                    AND price <= %s
                    ORDER BY 
                        price_diff ASC,
                        cert_priority,
                        wattage DESC
                    LIMIT 1
                """, (target_price, recommended_cert, required_wattage, psu_form_factor, max_price))
                
                result = cursor.fetchone()
                if result:
                    return dict(result)

                if psu_form_factor != "ATX":
                    cursor.execute("""
                        SELECT *,
                            ABS(price - %s) AS price_diff,
                            CASE 
                                WHEN certification_80plus = %s THEN 0
                                WHEN certification_80plus LIKE '%%Titanium%%' THEN 1
                                WHEN certification_80plus LIKE '%%Platinum%%' THEN 2
                                WHEN certification_80plus LIKE '%%Gold%%' THEN 3
                                WHEN certification_80plus LIKE '%%Silver%%' THEN 4
                                WHEN certification_80plus LIKE '%%Bronze%%' THEN 5
                                ELSE 6
                            END AS cert_priority
                        FROM pc_components.power_supply
                        WHERE CAST(NULLIF(REGEXP_REPLACE(wattage, '[^0-9]', '', 'g'), '') AS INTEGER) >= %s
                        AND form_factor = 'ATX'
                        AND price <= %s
                        ORDER BY 
                            price_diff ASC,
                            cert_priority,
                            wattage DESC
                        LIMIT 1
                    """, (target_price, recommended_cert, required_wattage, max_price))
                    result = cursor.fetchone()
                    if result:
                        return dict(result)

                cursor.execute("""
                    SELECT *,
                        ABS(price - %s) AS price_diff
                    FROM pc_components.power_supply
                    WHERE CAST(NULLIF(REGEXP_REPLACE(wattage, '[^0-9]', '', 'g'), '') AS INTEGER) >= %s
                    AND price <= %s
                    ORDER BY 
                        price_diff ASC,
                        wattage DESC
                    LIMIT 1
                """, (target_price, required_wattage, max_price))
                result = cursor.fetchone()
                if result:
                    return dict(result)

        return None
    except Exception as e:
        logger.error(f"Error in find_similar_power_supply: {e}", exc_info=True)
        return None
    

def run_power_supply_selection_test(
    input_data_2nd_stage: Dict[str, Any],
    chosen_cpu: Dict[str, Any], 
    chosen_gpu: Dict[str, Any],
    chosen_motherboard: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Тестирует подбор блока питания и выводит результат в формате JSON с красивым логом.
    """
    try:
        # Лог: старт теста
        print("===== ТЕСТИРОВАНИЕ ПОДБОРА БЛОКА ПИТАНИЯ =====")
        
        user_request = input_data_2nd_stage.get("user_request", {})
        method = user_request.get("allocations", {}).get("mandatory", {}).get("method", "unknown")
        logger.info(f"Метод выделения бюджета для блока питания: {method}")

        # Лог по бюджету
        if method == "fixed_price_based":
            max_price = user_request["allocations"]["mandatory"][method]["power_supply_max_price"]
            logger.info(f"Максимальная цена блока питания (фиксированная): {max_price}")
        elif method == "percentage_based":
            total_budget = user_request.get("budget", {}).get("amount", 0)
            ps_percentage = user_request["allocations"]["mandatory"][method]["power_supply_percentage"]
            max_price = round((ps_percentage / 100) * total_budget)
            logger.info(f"Максимальная цена блока питания (процент бюджета): {max_price}")
        else:
            logger.warning(f"Неизвестный метод распределения бюджета: {method}")
            max_price = None

        # Лог параметров CPU и GPU
        cpu_power = max(chosen_cpu.get("tdp", 0) or 0, chosen_cpu.get("base_tdp", 0) or 0)
        gpu_power = chosen_gpu.get("tdp")
        recommended_cert = get_recommended_certification(chosen_gpu)

        logger.info(f"Параметры CPU: TDP={cpu_power}")
        logger.info(f"Параметры GPU: модель='{chosen_gpu.get('gpu_model', 'неизвестно')}', TDP={gpu_power}")
        logger.info(f"Рекомендуемый сертификат 80 Plus для блока питания: {recommended_cert}")

        # Получаем подходящий блок питания
        power_supply_info = find_similar_power_supply(
            input_data_2nd_stage,
            chosen_cpu,
            chosen_gpu,
            chosen_motherboard
        )
        
        if not power_supply_info:
            logger.info("Совместимый блок питания не найден")
            return None
        
        # Преобразуем и выводим блок питания
        ps_model = PowerSupplyModel.from_orm(power_supply_info)
        ps_dict = ps_model.model_dump()

        logger.info(f"Выбран блок питания {ps_dict.get('name', 'неизвестно')} стоимостью {ps_dict.get('price', 'N/A')}")

        # Красивый вывод JSON
        print("\nНайден совместимый блок питания:")
        print(json.dumps(
            ps_dict,
            indent=4,
            ensure_ascii=False,
            default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o)
        ))

        return ps_dict

    except Exception as e:
        logger.error(f"Ошибка при подборе блока питания: {e}", exc_info=True)
        print(f"Ошибка при подборе блока питания: {str(e)}")
        return None

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
            "cooling": "water_cooling",
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

    chosen_cpu = {
    "id": 113,
    "name": "Процессор AMD Ryzen 5 7600X OEM",
    "price": 16799,
    "socket": "AM5",
    "tdp": 105,
    "base_tdp": 105,
    "cooler_included": True,
    "total_cores": 6,
    "performance_cores": 6,
    "efficiency_cores": 0,
    "max_threads": 12,
    "base_frequency": 4.7,
    "turbo_frequency": 5.3,
    "unlocked_multiplier": True,
    "memory_type": "DDR5",
    "max_memory": 128,
    "memory_channels": 2,
    "memory_frequency": 5200,
    "integrated_graphics": True,
    "gpu_model": "AMD Radeon Graphics",
    "pci_express": "PCIe 5.0",
    "pci_lanes": 24,
    "benchmark_rate": 17.67
    }
    chosen_gpu = {
    "id": 191,
    "name": "Видеокарта ASRock AMD Radeon RX 7700 XT Challenger OC [RX7700XT CL 12GO]",
    "price": 44999,
    "interface": "PCIe 4.0",
    "slot_width": "PCIe x16",
    "low_profile": False,
    "slots": "2.5",
    "length": 266,
    "width": 130,
    "thickness": 51,
    "tdp": None,
    "power_connectors": "2 x 8 pin",
    "recommended_psu": 750,
    "gpu_model": "Radeon RX 7700 XT",
    "architecture": "AMD RDNA 3",
    "vram_size": 12,
    "vram_type": "GDDR6",
    "bus_width": 192,
    "base_clock": 1900,
    "boost_clock": 2584,
    "cuda_cores": 3456,
    "ray_tracing": True,
    "tensor_cores": 0,
    "video_outputs": "3 x DisplayPort, HDMI",
    "max_resolution": "7680x4320 (8K Ultra HD)",
    "benchmark_rate": 55.64
    }

    chosen_motherboard = {
    "id": 421,
    "name": "Материнская плата MSI PRO X870-P WIFI",
    "price": 22499,
    "socket": "AM5",
    "chipset": "",
    "power_phases": 1421,
    "form_factor": "Standard-ATX",
    "height": 305,
    "width": 244,
    "memory_type": "DDR5",
    "memory_slots": 4,
    "memory_channels": 2,
    "max_memory": 256,
    "base_memory_freq": 5600,
    "oc_memory_freq": [
        5800,
        6000,
        6200,
        6400,
        6600,
        6800,
        7000,
        7200,
        7400,
        7600,
        7800,
        8000
    ],
    "memory_form_factor": "DIMM",
    "pcie_version": 0.0,
    "pcie_x16_slots": 1,
    "sli_crossfire": False,
    "sli_crossfire_count": 0,
    "nvme_support": True,
    "nvme_pcie_version": 0.0,
    "m2_slots": 3,
    "sata_ports": 4,
    "sata_raid": False,
    "nvme_raid": False,
    "cpu_fan_headers": 14,
    "aio_pump_headers": 1,
    "case_fan_4pin": 6,
    "case_fan_3pin": 0,
    "main_power": "24 pin",
    "cpu_power": "2 x 8 pin"
    }

    run_power_supply_selection_test(input_data_2nd_stage, chosen_cpu, chosen_gpu, chosen_motherboard)
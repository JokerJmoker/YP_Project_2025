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


import logging
import re
from typing import Dict, Any

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
    Улучшенный подбор блока питания с учетом:
    - класса видеокарты
    - близости к заданной цене
    - требуемой мощности с запасом
    - форм-фактора
    """
    try:
        # 1. Рассчитываем бюджет
        user_request = input_data_2nd_stage["user_request"]
        method = user_request["allocations"]["mandatory"]["method"]
        
        if method == "fixed_price_based":
            max_price = user_request["allocations"]["mandatory"][method]["power_supply_max_price"]
            target_price = max_price * 0.9  # Стремимся к 90% от максимального бюджета
        elif method == "percentage_based":
            total_budget = user_request["budget"]["amount"]
            ps_percentage = user_request["allocations"]["mandatory"][method]["power_supply_percentage"]
            max_price = round((ps_percentage / 100) * total_budget)
            target_price = max_price * 0.85  # Оптимальная цель - 85% от выделенного бюджета
        else:
            raise ValueError(f"Unsupported allocation method: {method}")

        # 2. Рассчитываем мощность с запасом
        cpu_power = max(chosen_cpu.get("tdp", 0), chosen_cpu.get("base_tdp", 0))
        gpu_power = chosen_gpu.get("tdp") or chosen_gpu.get("recommended_psu", 0)
        
        power_multiplier = 1.3 if chosen_gpu.get("tdp", 0) >= 250 else 1.2
        required_wattage = (cpu_power + gpu_power) * power_multiplier
        
        # Ближайшая стандартная мощность
        standard_wattages = [550, 650, 750, 850, 1000, 1200, 1600]
        required_wattage = min(w for w in standard_wattages if w >= required_wattage)

        # 3. Определяем форм-фактор
        mb_form_factor = chosen_motherboard.get("form_factor", "Standard-ATX")
        psu_form_factor = map_motherboard_to_psu_form_factor(mb_form_factor)

        # 4. Получаем рекомендуемый стандарт
        recommended_cert = get_recommended_certification(chosen_gpu)

        # 5. Ищем блок питания с оптимизацией по цене
        with Database() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                # Основной запрос с приоритетом по близости к целевой цене
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
                
                # Fallback 1: пробуем ATX если не нашли в нужном форм-факторе
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
                
                # Fallback 2: пробуем найти любой подходящий по мощности и цене
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
        print(f"Error in find_similar_power_supply: {e}")
        return None
    
def run_power_supply_selection_test(
    input_data_2nd_stage: Dict[str, Any],
    chosen_cpu: Dict[str, Any], 
    chosen_gpu: Dict[str, Any],
    chosen_motherboard: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Тестирует подбор блока питания и выводит результат в формате JSON.
    
    Args:
        input_data_2nd_stage: Данные пользователя и бюджет
        chosen_cpu: Выбранный процессор
        chosen_gpu: Выбранная видеокарта
        chosen_motherboard: Выбранная материнская плата
        
    Returns:
        Словарь с информацией о блоке питания в формате JSON или None
    """
    try:
        # Получаем данные блока питания
        power_supply_info = find_similar_power_supply(
            input_data_2nd_stage,
            chosen_cpu,
            chosen_gpu,
            chosen_motherboard
        )
        
        if not power_supply_info:
            print("Совместимый блок питания не найден")
            return None

        # Преобразуем в модель Pydantic
        ps_model = PowerSupplyModel.from_orm(power_supply_info)
        
        # Конвертируем модель в словарь
        ps_dict = ps_model.model_dump()
        
        # Выводим результат
        print("Найден совместимый блок питания:")
        print(json.dumps(
            ps_dict,
            indent=4,
            ensure_ascii=False,
            default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o)
        ))
        
        return ps_dict
        
    except Exception as e:
        print(f"Ошибка при подборе блока питания: {str(e)}")
        return None

input_data_2nd_stage = {
  "status": "success",
  "message": "Данные пользователя успешно разобраны.",
  "user_request": {
    "game": {
      "title": "cyberpunk_2077",
      "graphics": {
        "quality": "ultra",
        "target_fps": 60,
        "resolution": "2160",
        "ray_tracing": False,
        "dlss": "performance",
        "fsr": "disabled"
      }
    },
    "budget": {
      "amount": 200000,
      "allocation_method": "fixed_price_based"
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
        "pc_case": "normal_size",
        "cpu_cooler": "included_with_cpu"
      }
    },
    "allocations": {
      "mandatory": {
        "method": "fixed_price_based",
        "fixed_price_based": {
          "cpu_max_price": 40000,
          "gpu_max_price": 120000,
          "dimm_max_price": 15000,
          "ssd_m2_max_price": 12000,
          "motherboard_max_price": 20000,
          "power_supply_max_price": 15000
        }
      },
      "optional": {
        "method": "fixed_price_based",
        "fixed_price_based": {
          "cooling_max_price": 10000,
          "pc_case_max_price": 8000,
          "cpu_cooler_max_price": 0
        }
      }
    }
  }
}

chosen_cpu = {
    "id": 176,
    "name": "Процессор Intel Core i7-14700KF BOX",
    "price": 34999,
    "socket": "LGA 1700",
    "tdp": 253,
    "base_tdp": 125,
    "cooler_included": True,
    "total_cores": 20,
    "performance_cores": 8,
    "efficiency_cores": 12,
    "max_threads": 28,
    "base_frequency": 3.4,
    "turbo_frequency": 5.6,
    "unlocked_multiplier": True,
    "memory_type": "DDR4, DDR5",
    "max_memory": 192,
    "memory_channels": 2,
    "memory_frequency": 5600,
    "integrated_graphics": False,
    "gpu_model": "",
    "pci_express": "PCIe 5.0",
    "pci_lanes": 20,
    "benchmark_rate": 33.02
}
chosen_gpu = {
    "id": 293,
    "name": "Видеокарта KFA2 GeForce RTX 5070Ti ROCK(X) 3FAN RGB WHITE [57IZN6MDBVGK]",
    "price": 99999,
    "interface": "PCIe 5.0",
    "slot_width": "PCIe x16",
    "low_profile": False,
    "slots": "2.5",
    "length": 322,
    "width": 130,
    "thickness": 52,
    "tdp": 300,
    "power_connectors": "16 pin (12V-2x6)",
    "recommended_psu": 750,
    "gpu_model": "GeForce RTX 5070 Ti",
    "architecture": "NVIDIA Blackwell",
    "vram_size": 16,
    "vram_type": "GDDR7",
    "bus_width": 256,
    "base_clock": 2295,
    "boost_clock": 2512,
    "cuda_cores": 8960,
    "ray_tracing": True,
    "tensor_cores": 2,
    "video_outputs": "3 x DisplayPort, HDMI",
    "max_resolution": "7680x4320 (8K Ultra HD)",
    "benchmark_rate": 81.21
}

chosen_motherboard = {
    "id": 472,
    "name": "Материнская плата GIGABYTE Z790 AORUS MASTER X",
    "price": 33999,
    "socket": "LGA 1700",
    "chipset": "Intel Z790",
    "power_phases": 2012,
    "form_factor": "E-ATX",
    "height": 305,
    "width": 260,
    "memory_type": "DDR5",
    "memory_slots": 4,
    "memory_channels": 2,
    "max_memory": 256,
    "base_memory_freq": 4800,
    "oc_memory_freq": [
        5200,
        5400,
        5600,
        5800,
        6000,
        6200,
        6400,
        6600,
        6800,
        7000,
        7200,
        7400
    ],
    "memory_form_factor": "DIMM",
    "pcie_version": 0.0,
    "pcie_x16_slots": 1,
    "sli_crossfire": False,
    "sli_crossfire_count": 2,
    "nvme_support": True,
    "nvme_pcie_version": 0.0,
    "m2_slots": 5,
    "sata_ports": 4,
    "sata_raid": False,
    "nvme_raid": False,
    "cpu_fan_headers": 1414,
    "aio_pump_headers": 4,
    "case_fan_4pin": 4,
    "case_fan_3pin": 0,
    "main_power": "24 pin",
    "cpu_power": "2 x 8 pin"
}

run_power_supply_selection_test(input_data_2nd_stage, chosen_cpu, chosen_gpu, chosen_motherboard)
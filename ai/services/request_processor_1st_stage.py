from .parse_request_1st_stage import parse_game_settings
from ai_db.queries_1st_stage import get_recommended_config

def get_game_recommendation(conn, game_data, quality=None):
    """
    Получает рекомендованную конфигурацию для игры, объединяя парсинг настроек и запрос к БД.
    
    Args:
        conn: соединение с базой данных
        game_data: сырые данные о игре (словарь)
        quality: (опционально) приоритет качества графики, если не указан - берется из game_data
    
    Returns:
        Словарь с рекомендованной конфигурацией
    
    Raises:
        ValueError: если возникла ошибка при обработке
    """
    try:
        # Парсим настройки игры
        game_info = parse_game_settings(game_data)
        
        # Проверяем наличие необходимых данных
        if not game_info.get("graphics", {}).get("quality") and not quality:
            raise ValueError("Качество графики не указано ни в данных игры, ни в параметрах")
        
        # Определяем качество графики (приоритет у явно указанного параметра)
        target_quality = quality.lower() if quality else game_info["graphics"]["quality"].lower()
        
        # Получаем рекомендованную конфигурацию из БД
        config = get_recommended_config(conn, game_info, target_quality)
        
        return config
        
    except ValueError as e:
        raise ValueError(f"Ошибка при получении рекомендации: {str(e)}")
    except KeyError as e:
        raise ValueError(f"Отсутствует обязательное поле в данных: {str(e)}")
    except Exception as e:
        raise ValueError(f"Неожиданная ошибка при обработке: {str(e)}")
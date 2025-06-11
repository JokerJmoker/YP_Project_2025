from .parse_request import parse_user_request
from ai_db.queries_1st_stage import get_recommended_config

def get_game_recommendation(conn, user_data, quality=None):
    """
    Получает рекомендованную конфигурацию для игры, используя полную структуру user_data,
    парсит ее через parse_user_request, и обращается к БД.

    Args:
        conn: соединение с базой данных
        user_data: словарь с данными пользователя (включая user_selections)
        quality: (опционально) приоритет качества графики
    
    Returns:
        Словарь с рекомендованной конфигурацией
    
    Raises:
        ValueError: при ошибках обработки
    """
    try:
        # Парсим всю структуру запроса
        parsed_data = parse_user_request(user_data)

        # Извлекаем настройки игры
        game_info = parsed_data.get("game", {})

        # Получаем качество графики из параметров игры или используем переданное
        quality_in_game = game_info.get("graphics", {}).get("quality")
        if not quality_in_game and not quality:
            raise ValueError("Качество графики не указано ни в данных игры, ни в параметрах")

        target_quality = quality.lower() if quality else quality_in_game.lower()

        # Запрашиваем рекомендованную конфигурацию, передаем всю распарсенную игру и качество
        config = get_recommended_config(conn, game_info, target_quality)

        return config

    except ValueError as e:
        raise ValueError(f"Ошибка при получении рекомендации: {str(e)}")
    except KeyError as e:
        raise ValueError(f"Отсутствует обязательное поле в данных: {str(e)}")
    except Exception as e:
        raise ValueError(f"Неожиданная ошибка при обработке: {str(e)}")

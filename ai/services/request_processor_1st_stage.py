import logging
import pprint
from .parse_request import parse_user_request
from ai_db.queries_1st_stage import get_recommended_config
import json

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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    print("===== ТЕСТИРОВАНИЕ ПОДБОРА КОНФИГУРАЦИИ ДЛЯ ИГРЫ =====")

    try:
        logging.info("Начинаем разбор пользовательских данных")
        parsed_data = parse_user_request(user_data)
        logging.info("Данные успешно разобраны")

        game_info = parsed_data.get("game", {})
        quality_in_game = game_info.get("graphics", {}).get("quality")

        if not quality_in_game and not quality:
            logging.error("Качество графики не указано ни в данных игры, ни в параметрах")
            raise ValueError("Качество графики не указано ни в данных игры, ни в параметрах")

        target_quality = quality.lower() if quality else quality_in_game.lower()
        logging.info(f"Используемое качество графики: {target_quality}")

        config = get_recommended_config(conn, game_info, target_quality)
        logging.info("Рекомендация получена успешно")

        print("\nРезультат рекомендации:")
        print(json.dumps(config, indent=4, ensure_ascii=False))

        return config

    except ValueError as e:
        logging.error(f"Ошибка при получении рекомендации: {e}", exc_info=True)
        print(f"\n[ОШИБКА] {str(e)}")
        raise
    except KeyError as e:
        logging.error(f"Отсутствует обязательное поле: {e}", exc_info=True)
        print(f"\n[ОШИБКА] Отсутствует обязательное поле: {str(e)}")
        raise ValueError(f"Отсутствует обязательное поле в данных: {str(e)}")
    except Exception as e:
        logging.error(f"Неожиданная ошибка при обработке: {e}", exc_info=True)
        print(f"\n[ОШИБКА] Неожиданная ошибка: {str(e)}")
        raise ValueError(f"Неожиданная ошибка при обработке: {str(e)}")

import logging
import pprint
import json
from .parse_request import parse_user_request

def get_propriate_components(conn, data):
    """
    Черновая функция: отображает разобранные пользователем параметры
    и красиво выводит результат в консоль.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S"
    )
    print("===== ТЕСТИРОВАНИЕ ПОДБОРА КОМПОНЕНТОВ =====")
    try:
        logging.info("Начинаем разбор пользовательских данных")
        parsed = parse_user_request(data)
        logging.info("Пользовательские данные успешно разобраны")

        result = {
            "status": "success",
            "message": "Данные пользователя успешно разобраны.",
            "user_request": parsed
        }

        print("\nРезультат разбора запроса:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

        return result

    except Exception as e:
        logging.error(f"Ошибка при разборе данных: {e}", exc_info=True)
        error_result = {
            "status": "error",
            "message": "Ошибка при обработке пользовательских данных.",
            "details": str(e)
        }

        print("\n[ОШИБКА] Ошибка при разборе данных:")
        pprint.pprint(error_result, indent=4)

        return error_result

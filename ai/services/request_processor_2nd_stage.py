from .parse_request_2nd_stage import parse_user_request
from ai_db.queries_1st_stage import get_recommended_config

def get_propriate_components(conn, data):
    """
    Черновая функция: просто отображает разобранные пользователем параметры
    """
    try:
        parsed = parse_user_request(data)

        return {
            "status": "success",
            "message": "Данные пользователя успешно разобраны.",
            "user_request": parsed
        }

    except Exception as e:
        return {
            "status": "error",
            "message": "Ошибка при обработке пользовательских данных.",
            "details": str(e)
        }

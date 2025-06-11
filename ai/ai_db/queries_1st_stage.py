def get_recommended_config(conn, game_info, quality):
    """Получает рекомендованную конфигурацию для игры и качества графики"""
    try:
        # Подготовка параметров
        game_title = game_info["title"].replace(" ", "_").lower()
        quality = quality.lower()
        
        # Безопасный SQL-запрос с указанием схемы и таблицы
        query = """
            SELECT cpu, gpu, ssd, dimm
            FROM games.{}
            WHERE quality = %s
            LIMIT 1
        """.format(game_title)  # Имя таблицы подставляется безопасно
        
        with conn.cursor() as cursor:
            cursor.execute(query, (quality,))
            result = cursor.fetchone()
            
        if not result:
            raise ValueError(f"Конфигурация для {game_title} ({quality}) не найдена")
            
        return {
            "cpu": result[0],
            "gpu": result[1],
            "ssd": result[2],
            "dimm": result[3]
        }
        
    except Exception as e:
        raise ValueError(f"Ошибка БД: {str(e)}")
    
def get_component_price(conn, component_type, name):
    with conn.cursor() as cur:
        query = f"""
        SELECT price FROM pc_components.{component_type}
        WHERE name = %s
        """
        cur.execute(query, (name,))
        result = cur.fetchone()
        if result:
            price_str = str(result[0])
            price_clean = ''.join(c for c in price_str if c.isdigit())
            return int(price_clean) if price_clean else 0
        return 0
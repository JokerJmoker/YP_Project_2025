def get_recommended_config(conn, game_info, quality):
    """Получает рекомендованную конфигурацию для игры и качества графики"""
    try:
        # Подготовка параметров
        game_title = game_info["title"].replace(" ", "_").lower()
        quality = quality.lower()
        
        # Сначала проверим существование таблицы
        table_check = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'games' 
                AND table_name = %s
            )
        """
        
        with conn.cursor() as cursor:
            cursor.execute(table_check, (game_title,))
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                raise ValueError(f"Таблица для игры '{game_info['title']}' не найдена в базе данных")
        
            # Безопасный SQL-запрос с указанием схемы и таблицы
            query = """
                SELECT cpu, gpu, ssd_m2, dimm
                FROM games.{}
                WHERE quality = %s
                LIMIT 1
            """.format(game_title)
            
            cursor.execute(query, (quality,))
            result = cursor.fetchone()
            
        if not result:
            raise ValueError(f"Конфигурация для {game_info['title']} ({quality}) не найдена")
            
        return {
            "game": game_info["title"],
            "quality": quality,
            "cpu": result[0],
            "gpu": result[1],
            "ssd_m2": result[2],
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
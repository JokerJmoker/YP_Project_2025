def get_recommended_config(conn, game_title, quality):
    with conn.cursor() as cur:
        query = f"""
        SELECT cpu, gpu, ssd, dimm
        FROM games."{game_title}"
        WHERE preset = %s
        """
        cur.execute(query, (quality,))
        result = cur.fetchone()
        if not result:
            raise ValueError("Нет конфигурации для указанных параметров.")
        return {
            "cpu": result[0],
            "gpu": result[1],
            "ssd": result[2],
            "dimm": result[3]
        }

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
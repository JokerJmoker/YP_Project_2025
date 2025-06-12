def parse_float(s):
    if s is None:
        return None
    if isinstance(s, float):  # уже float — возвращаем как есть
        return s
    try:
        s = s.replace(',', '.').split()[0]
        return float(s)
    except:
        return None

def parse_int(s):
    if s is None:
        return None
    if isinstance(s, int):
        return s
    try:
        return int(s)
    except:
        return None


def parse_ghz(s):
    # Пример: "4.9 ГГц"
    if not s:
        return None
    s = s.lower().replace(',', '.')
    if 'ггц' in s:
        s = s.replace('ггц', '')
    return parse_float(s)

def parse_bool(s):
    if isinstance(s, bool):
        return s
    if not s:
        return False
    s = str(s).strip().lower()
    return s in ('yes', 'true', 'да', '1')

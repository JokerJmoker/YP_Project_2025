def parse_float(s):
    if not s:
        return None
    s = s.replace(',', '.').split()[0]
    try:
        return float(s)
    except:
        return None


def parse_int(s):
    if not s:
        return None
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
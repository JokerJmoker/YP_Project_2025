import re

def parse_int(value):
    """
    Преобразует значение в int, убирая нечисловые символы.
    Возвращает None, если не удалось распарсить.
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    try:
        value_str = str(value).strip()
        # Убираем все символы, кроме цифр и знака минус в начале
        clean_str = re.sub(r'[^\d-]', '', value_str)
        # Для пустой строки возвращаем None
        if not clean_str or clean_str == '-':
            return None
        return int(clean_str)
    except (ValueError, AttributeError):
        return None

def parse_float(value):
    """
    Преобразует значение в float, учитывая возможную запятую вместо точки,
    убирая лишние символы.
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        value_str = str(value).replace(',', '.').strip()
        # Оставляем цифры, точку и минус
        clean_str = re.sub(r'[^0-9.-]', '', value_str)
        if not clean_str or clean_str == '-' or clean_str == '.':
            return None
        return float(clean_str)
    except (ValueError, AttributeError):
        return None

def parse_bool(value):
    """
    Преобразует значение в булево.
    True для ['да', 'yes', 'true', '1', 'y', 'on'] (регистр игнорируется).
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ['да', 'yes', 'true', '1', 'y', 'on']
    if isinstance(value, int):
        return value == 1
    return False

def parse_ghz(s):
    """
    Парсит строку с частотой в ГГц, например "4.9 ГГц" -> 4.9 (float).
    """
    if not s:
        return None
    s = str(s).lower().replace(',', '.')
    if 'ггц' in s:
        s = s.replace('ггц', '')
    return parse_float(s)

def parse_psu_wattage(psu_value):
    """
    Парсит мощность блока питания, убирая 'W' и преобразуя в int.
    """
    if psu_value is None:
        return None
    if isinstance(psu_value, (int, float)):
        return int(psu_value)
    if isinstance(psu_value, str):
        return parse_int(psu_value.replace('W', '').strip())
    return None

def parse_iops(iops_value):
    """
    Парсит число IOPS, убирая 'IOPS', пробелы и запятые.
    """
    if iops_value is None:
        return None
    if isinstance(iops_value, (int, float)):
        return int(iops_value)
    if isinstance(iops_value, str):
        return parse_int(iops_value.replace('IOPS', '').replace(',', '').strip())
    return None

def parse_speed(speed_str):
    if speed_str is None:
        return None
    if isinstance(speed_str, (int, float)):
        return int(speed_str)
    if isinstance(speed_str, str):
        return parse_int(speed_str.replace('MB/s', '').strip())
    return None

def parse_memory_frequency(value):
    """
    Парсит строку вида "DDR4-3200, DDR5-5600" или "3200, 5600" и возвращает максимальную частоту (int) или None.
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        import re
        frequencies = []
        parts = value.split(',')
        for part in parts:
            # Ищем число после дефиса
            match = re.search(r'-(\d+)', part)
            if match:
                frequencies.append(int(match.group(1)))
            else:
                # Если нет дефиса, пытаемся найти число в строке
                digits = re.findall(r'\d+', part)
                if digits:
                    frequencies.append(int(digits[0]))
        if frequencies:
            return max(frequencies)
    return None

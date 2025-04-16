def safe_int_convert(text):
    try:
        text = text.strip()
        if text == '--' or text == '---' or not text:
            return 0
        return int(text)
    except (ValueError, TypeError):
        return 0

def safe_float_convert(text):
    try:
        text = text.strip()
        if text == '--' or text == '---' or not text:
            return 0
        return float(text)
    except (ValueError, TypeError):
        return 0

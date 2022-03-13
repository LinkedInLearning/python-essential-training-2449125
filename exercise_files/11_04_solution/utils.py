def is_number(val):
    try:
        float(val)
        return True
    except ValueError:
        return False
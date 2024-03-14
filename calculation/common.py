def calculate_percentage(general: int | float, current: int | float) -> int | float:
    if general != 0:
        return current * 100 / general
    return 0

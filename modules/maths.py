from math import ceil


def calculate_distance(pos_1: tuple, pos_2: tuple) -> float:
    return ((pos_1[0] - pos_2[0]) ** 2 + (pos_1[1] - pos_2[1]) ** 2) ** 0.5


def calculate_damage(speed: float, height: int) -> int:
    return ceil(speed * height / 3)

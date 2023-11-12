from pygame import Rect
from math import floor
from modules.parameters.parameters import TILESIZE

FRICTION = {
    "0": 1,
    "gr": 0.95,
    "pu": 0.95,
    "ye": 0.95
}
GRAVITY = 0.005


def apply_gravity(weight: float) -> float:
    return GRAVITY * weight


def area_x(x: float, y: float, speed: float, width: int, height: int) -> tuple:
    """Create an area\n
    USE FOR ONLY `x-axis`"""
    if speed >= 0:
        vector = 1
        rect = (floor((x + width-1) / TILESIZE),
                floor(y / TILESIZE),
                floor((x + width + speed) / TILESIZE + 1),
                floor((y + height - 1) / TILESIZE + 1))
    else:
        vector = -1
        rect = (floor(x / TILESIZE),
                floor(y / TILESIZE),
                floor((x + speed - 1) / TILESIZE - 1),
                floor((y + height - 1) / TILESIZE + 1))
    return rect, vector


def area_y(x: float, y: float, speed: float, width: int, height: int) -> tuple:
    """Create an area\n
    USE FOR ONLY `y-axis`"""
    if speed >= 0:
        vector = 1
        rect = (floor(x / TILESIZE),
                floor((y + height - 1) / TILESIZE),
                floor((x + width - 1) / TILESIZE + 1),
                floor((y + height + speed) / TILESIZE + 1))
    else:
        vector = -1
        rect = (floor(x / TILESIZE),
                floor(y / TILESIZE),
                floor((x + width + TILESIZE - 1) / TILESIZE),
                floor((y + speed - TILESIZE - 1) / TILESIZE))
    return rect, vector


def collision_x(area: tuple,
                matrix: list[list[str]]) -> tuple[int, int, str, int]:
    """Check every tile of object's rect if it's collided with walls.\n
    Returns tile's coordinates.\n
    USE FOR ONLY `x-axis`"""

    for col_index in range(area[0][0], area[0][2], area[1]):
        for row_index in range(area[0][1], area[0][3]):
            if matrix[row_index][col_index] != "0":
                return (col_index * TILESIZE, row_index * TILESIZE,
                        matrix[row_index][col_index])
    return (col_index * TILESIZE, row_index * TILESIZE,
            matrix[row_index][col_index])


def collision_y(area: tuple,
                matrix: list[list[str]]) -> tuple[int, int, str, int]:
    """Check every tile of object's rect if it's collided with walls.\n
    Returns tile's coordinates.\n
    USE FOR ONLY `y-axis`"""

    for row_index in range(area[0][1], area[0][3], area[1]):
        for col_index in range(area[0][0], area[0][2]):
            if matrix[row_index][col_index] != "0":
                return (col_index * TILESIZE, row_index * TILESIZE,
                        matrix[row_index][col_index])
    return (col_index * TILESIZE, row_index * TILESIZE,
            matrix[row_index][col_index])


def entityCollision(
    x_1: float, y_1: float, width_1: int, height_1: int,
    x_2: float, y_2: float, width_2: int, height_2: float
) -> bool:
    return Rect(x_1, y_1, width_1, height_1) \
        .colliderect(Rect(x_2, y_2, width_2, height_2))

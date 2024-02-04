from pygame import Rect
from math import floor
from modules.parameters.parameters import TILESIZE


GRAVITY = 0.005
FRICTION = {
    "0": 1,
    "gr": 0.95,
    "pu": 0.95,
    "ye": 0.95
}


def apply_gravity(weight: float) -> float:
    return GRAVITY * weight


def calc_area_x(x: float, y: float, speed: float, width: int, height: int) -> tuple:
    """Create an area\n\nUSE FOR ONLY `x-axis`"""

    if speed >= 0:
        vector = 1
        rect = (floor((x + width-1) / TILESIZE),            # left
                floor(y / TILESIZE),                        # top
                floor((x + width + speed) / TILESIZE + 1),  # right
                floor((y + height - 1) / TILESIZE + 1))     # bottom
    else:
        vector = -1
        rect = (floor(x / TILESIZE),                        # right
                floor(y / TILESIZE),                        # top
                floor((x + speed - 1) / TILESIZE - 1),      # left
                floor((y + height - 1) / TILESIZE + 1))     # bottom
    return rect, vector


def calc_area_y(x: float, y: float, speed: float, width: int, height: int) -> tuple:
    """Create an area\n\nUSE FOR ONLY `y-axis`"""

    if speed >= 0:
        vector = 1
        rect = (floor(x / TILESIZE),                           # left
                floor((y + height - 1) / TILESIZE),            # top
                floor((x + width - 1) / TILESIZE + 1),         # right
                floor((y + height + speed) / TILESIZE + 1))    # bottom
    else:
        vector = -1
        rect = (floor(x / TILESIZE),                           # left
                floor(y / TILESIZE),                           # bottom
                floor((x + width + TILESIZE - 1) / TILESIZE),  # right
                floor((y + speed - TILESIZE - 1) / TILESIZE))  # top
    return rect, vector


def check_collision_x(area: tuple, matrix: list[list[str]]) -> tuple[int, int, str, int]:
    """Check every tile of object's rect if it's collided with walls.\n
    Returns tile's coordinates.\n
    USE FOR ONLY `x-axis`"""

    for col_index in range(area[0][0], area[0][2], area[1]):
        for row_index in range(area[0][1], area[0][3]):
            if matrix[row_index][col_index] != "0":
                return (col_index * TILESIZE, row_index * TILESIZE,
                        matrix[row_index][col_index])
    return (col_index * TILESIZE, row_index * TILESIZE, matrix[row_index][col_index])


def check_collision_y(area: tuple, matrix: list[list[str]]) -> tuple[int, int, str, int]:
    """Check every tile of object's rect if it's collided with walls.\n
    Returns tile's coordinates.\n
    USE FOR ONLY `y-axis`"""

    for row_index in range(area[0][1], area[0][3], area[1]):
        for col_index in range(area[0][0], area[0][2]):
            if matrix[row_index][col_index] != "0":
                return (col_index * TILESIZE, row_index * TILESIZE,
                        matrix[row_index][col_index])
    return (col_index * TILESIZE, row_index * TILESIZE, matrix[row_index][col_index])


def entity_collision(
    x_1: float, y_1: float, width_1: int, height_1: int,
    x_2: float, y_2: float, width_2: int, height_2: int
) -> bool:
    """Check the collision between two areas"""

    return (x_1 <= x_2 <= x_1 + width_1
            or x_1 <= x_2 + width_2 <= x_1 + width_2)\
        and (y_1 <= y_2 <= y_1 + height_1
             or y_1 <= y_2 + height_2 <= y_1 + height_2)


def entity_collision_pg(
    x_1: float, y_1: float, width_1: int, height_1: int,
    x_2: float, y_2: float, width_2: int, height_2: float
) -> bool:
    """Check the collision between two areas using `pygame.Rect.colliderect`"""
    return Rect(x_1, y_1, width_1, height_1).colliderect(Rect(x_2, y_2, width_2, height_2))

import pygame
from math import sin
from modules.parameters.parameters import screenRes

pygame.mixer.init()


def lsd(color: float, brightness: int) -> tuple:
    return (abs(int(sin(color) * brightness)),
            abs(int(sin(color+1) * brightness)),
            abs(int(sin(color+2) * brightness)))

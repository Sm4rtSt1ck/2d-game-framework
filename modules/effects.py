import pygame
from math import sin
from modules.parameters.options import fonts_path

pygame.mixer.init()
pygame.font.init()


font_default = "JosefinSans/JosefinSans-Medium.ttf", 20


class SpeechBubble:
    def __init__(
        self,
        coords: tuple[float, float],
        bg_color: tuple[int, int, int],
        text: str, text_color: tuple[int, int, int],
        font: tuple[str, int] = font_default
    ) -> None:
        self.x, self.y = coords
        self.bg_color = bg_color
        self.text = text
        self.font = pygame.font.Font(fonts_path+font[0], font[1])
        self.font_size = font[1]
        self.width = min(self.font_size * 15, self.font_size * len(text) // 2) + self.font_size * 2
        self.height = self.font_size * (len(text) // 30 + 3)
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(bg_color)
        for line in range(len(text)//30+1):
            self.surface.blit(
                self.font.render(self.text[30*line:30*line+30], True, text_color),
                (self.font_size, self.font_size * (line+1)))


def lsd(color: float, brightness: int) -> tuple:
    return (abs(int(sin(color) * brightness)),
            abs(int(sin(color+1) * brightness)),
            abs(int(sin(color+2) * brightness)))


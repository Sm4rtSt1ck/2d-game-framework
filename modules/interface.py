import pygame
from modules.parameters.colors import *
from modules.parameters.parameters import (TILESIZE, images_path, screen_res,
                                           fonts_path)

pygame.font.init()


font_default = "JosefinSans/JosefinSans-Medium.ttf", 30


def nothing(): return


def change_color(color: tuple) -> tuple:
    r = color[0] * 0.5
    g = color[1] * 0.5
    b = color[2] * 0.5
    return r, g, b


class Label:
    def __init__(
        self,
        coords: tuple,
        size: tuple,
        color: tuple,
        text: str = "",
        text_color: tuple = (255, 255, 255),
        font: tuple = font_default
    ) -> None:

        self.coords = (screen_res[0] * coords[0] / 100,
                       screen_res[1] * coords[1] / 100)
        self.size = (screen_res[0] * size[0] / 100,
                     screen_res[1] * size[1] / 100)
        self.color = color[:3]
        self.alpha = color[3] if len(color) == 4 else 255
        self.rect = pygame.Rect(0, 0, *self.size)
        self.rect.center = self.coords
        self.text_color = text_color

        # Text
        self.font = pygame.font.Font(fonts_path+font[0], font[1])
        self.text = self.font.render(text, False, self.text_color)
        self.text_pos = (
            self.rect.w // 2 - self.text.get_rect().w // 2,
            self.rect.h // 2 - self.text.get_rect().h // 2)

        # Label surface
        self.surface_default = pygame.Surface(self.size)
        self.surface_default.fill(self.color)
        self.surface_default.blit(self.text, self.text_pos)
        self.surface_default.set_alpha(self.alpha)
        self.surface_default.set_colorkey(TRANSPARENT)
        self.surface = self.surface_default

    def change_text(self, text: str, color: tuple = None) -> None:
        self.text = self.font.render(
            text, False, color if color else self.text_color)
        self.text_pos = (
            self.rect.w // 2 - self.text.get_rect().w // 2,
            self.rect.h // 2 - self.text.get_rect().h // 2)
        self.surface_default.fill(self.color)
        self.surface_default.blit(self.text, self.text_pos)

    def change_background(self, color: tuple) -> None:
        """Change the label background color"""
        self.color = color[:3]
        self.alpha = color[3] if len(color) == 4 else 255
        self.surface_default = pygame.Surface(self.size)
        self.surface_default.fill(self.color)
        self.surface_default.blit(self.text, self.text_pos)
        self.surface_default.set_alpha(self.alpha)
        self.surface = self.surface_default

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.rect)


class Button(Label):
    def __init__(
        self,
        coords: tuple,
        size: tuple,
        color: tuple,
        text: str = "",
        text_color: tuple = (255, 255, 255),
        font: tuple = font_default,
        color2: tuple = None,
        func=nothing,
        *args
    ) -> None:
        super().__init__(coords, size, color, text, text_color, font)

        self.func = func
        self.args = args
        self.pressed: bool = False

        # When button is being pressed
        self.surface_pressed = pygame.Surface(self.size)
        self.surface_pressed.fill(
            color2 if color2 is not None else change_color(self.color))
        self.surface_pressed.blit(self.text, self.text_pos)
        self.surface_pressed.set_alpha(self.alpha)
        self.surface_pressed.set_colorkey(TRANSPARENT)

    def on_press(self):
        self.pressed = True

        self.surface = self.surface_pressed

    def on_release(self, doFunc: bool):
        self.pressed = False
        if doFunc:
            self.func(*self.args)

        self.surface = self.surface_default


def make_button_table(
    x: int, y: int,
    range_start: int, range_end: int, cols: int,
    col_distance: int, row_distance: int,
    button_width: int, button_height: int,
    color: tuple,
    text_color: tuple, font: tuple = font_default,
    color2: tuple = None,
    func=nothing,
    *args
) -> list:

    return ([
            Button((x + (button-1) % cols * col_distance,
                    y + (button-1) // cols * row_distance),
                   (button_width, button_height),
                   color, str(button), text_color, font, color2,
                   func, args[0].replace("*", str(button)), *args[1:])
            for button in range(range_start, range_end)
            ])


class SwitchButton(Button):
    def __init__(
        self,
        coords: tuple,
        size: tuple,
        color: tuple,
        text: str = "",
        text_color: tuple = (255, 255, 255),
        color2: tuple = None,
        text2: str = None,
        text2_color: tuple = None,
        font: tuple = font_default,
        func=nothing,
        *args
    ) -> None:
        super().__init__(coords=coords, size=size, color=color, text=text,
                         text_color=text_color, font=font, func=func, *args)

        self.activated: bool = False

        # Color
        if not color2:
            color2 = color
        self.color2 = color2[:3]
        self.alpha2 = color2[3] if len(color2) == 4 else self.alpha

        # Text
        self.text2 = self.font.render(
            text2 if text2 else text, True,
            text2_color if text2_color else text_color)
        self.text2_pos: tuple = (
            self.rect.w // 2 - self.text2.get_rect().w // 2,
            self.rect.h // 2 - self.text2.get_rect().h // 2)

        # When button is being idle and activated
        self.surface_activated = pygame.Surface(self.size)
        self.surface_activated.fill(self.color2)
        self.surface_activated.blit(self.text2, self.text2_pos)
        self.surface_activated.set_alpha(self.alpha2)
        self.surface_activated.set_colorkey(TRANSPARENT)
        # When button is being pressed and activated
        self.surface_pressed_activated = pygame.Surface(self.size)
        self.surface_pressed_activated.fill(change_color(self.color2))
        self.surface_pressed_activated.blit(self.text2, self.text2_pos)
        self.surface_pressed_activated.set_alpha(self.alpha2)
        self.surface_pressed_activated.set_colorkey(TRANSPARENT)

    def on_press(self) -> None:
        self.pressed = True

        if self.activated:
            self.surface = self.surface_pressed_activated
        else:
            self.surface = self.surface_pressed

    def on_release(self, doFunc: bool) -> None:
        self.pressed = False
        if doFunc:
            self.activated = not self.activated
            self.func(*self.args)

        if self.activated:
            self.surface = self.surface_activated
        else:
            self.surface = self.surface_default


class Slider(Button):
    def __init__(
        self,
        coords: tuple,
        size: tuple,
        points: int,
        background_color: tuple,
        text: str,
        color: tuple,
        font: tuple = font_default,
        func=nothing,
        *args
    ) -> None:

        super().__init__(coords, size, background_color,
                         text, color, font, color, func, *args)

        self.coords = (screen_res[0] * coords[0] / 100,
                       screen_res[1] * coords[1] / 100)
        self.size = (screen_res[0] * size[0] / 100,
                     screen_res[1] * size[1] / 100)
        self.points = points
        self.interval = (self.size[0] - 20) / (points - 1)
        self.color = color
        self.background_color = background_color
        self.rect = pygame.Rect(0, 0, *self.size)
        self.rect.center = self.coords
        self.surface = self.create_surface()
        self.surface.set_colorkey(TRANSPARENT)

        self.current_point = 0

    def create_surface(self) -> pygame.Surface:
        surface = pygame.Surface(self.size)
        surface.fill(self.background_color)
        pygame.draw.line(surface, self.color, (10, self.size[1] / 2),
                         (self.size[0] - 10, self.size[1] / 2), 5)
        for point in range(self.points):
            pygame.draw.circle(surface, self.color, (10+point*self.interval,
                               self.size[1] / 2), self.size[1] / 4)
        return surface

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.rect)


class Table:
    def __init__(
        self,
        coords: tuple,
        rows: int,
        cols: int,
        labels: dict[str, Label] = {},
        buttons: set[Button] = set()
    ) -> None:
        self.coords = (screen_res[0] * coords[0] / 100,
                       screen_res[1] * coords[1] / 100)
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.rect.center = self.coords
        self.matrix = [[] * cols] * rows  # может возникнуть прикол
        self.labels = labels
        self.buttons = buttons
        self.update_surface()

    def addRow(self, index: int = None) -> None:
        self.matrix.insert(index, []) if index else self.matrix.append([])

    def addCol(self, index: int = None) -> None:
        if not index:
            index = len(self.matrix[0]) - 1
        for row in self.matrix:
            row.insert(index, [])

    def insertLabel(self, col: int, row: int, label: Label) -> None:
        self.matrix[row][col] = label
        self.update_surface()

    def get_width(self):
        width = 0
        for row in self.matrix:
            width = max(width, sum([label.rect.w for label in row]))
        return width

    def get_height(self):
        height = 0
        for row in self.matrix:
            try:
                height += max([label.rect.h for label in row])
            except ValueError:
                pass
        return height

    def update_surface(self) -> None:
        self.surface = pygame.Surface((self.get_width(), self.get_height()))

    def press_button(self, mouse_pos: tuple) -> None:
        for button in self.buttons:
            if button.rect.collidepoint(mouse_pos):
                button.on_press()

    def release_button(self, mouse_pos: tuple) -> None:
        for button in self.buttons:
            if button.pressed:
                button.on_release(button.rect.collidepoint(mouse_pos))

    def update(self, surface: pygame.Surface) -> None:
        for label in self.labels:
            label.draw(self.surface)
        for button in self.buttons:
            button.draw(self.surface)
        surface.blit(self.surface, self.rect)


class MiniMap:
    def __init__(self, level_matrix: list[list[str]], coords: tuple[int, int],
                 size: int, transparency: int) -> None:
        self.coords = (screen_res[0] * coords[0] / 100,
                       screen_res[1] * coords[1] / 100)
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = self.coords
        self.surface = self.create_surface(level_matrix)
        self.surface = pygame.transform.scale(
            self.surface,
            (self.surface.get_width() * size // 100,
             self.surface.get_height() * size // 100))
        self.surface.set_alpha(transparency)

    def create_surface(self, matrix: list[list[str]]) -> pygame.Surface:
        """Create a top view map of a level"""
        surface = pygame.Surface(
            (len(matrix[0]) * TILESIZE, len(matrix) * TILESIZE))
        for row_index, row in enumerate(matrix):
            for col_index, tile in enumerate(row):
                if tile == "0":
                    continue
                coords = col_index * TILESIZE, row_index * TILESIZE
                pygame.draw.rect(surface, COLORS[tile],
                                 (*coords, TILESIZE, TILESIZE))
        return surface

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.rect)


class Menu:
    def __init__(
        self,
        background_path: str = None,
        labels: dict = {},
        buttons: set = set()
    ) -> None:

        self.labels = labels
        self.buttons = buttons

        self.surface = pygame.Surface(screen_res)
        self.surface.set_colorkey(TRANSPARENT)
        self.surface.fill(TRANSPARENT)
        if background_path:
            self.surface.blit(
                pygame.transform.scale(
                    pygame.image.load(
                        images_path + background_path).convert_alpha(),
                    screen_res),
                (0, 0))

    def press_button(self, mouse_pos: tuple) -> None:
        for button in self.buttons:
            if button.rect.collidepoint(mouse_pos):
                button.on_press()
                return True
        return False

    def release_button(self, mouse_pos: tuple) -> None:
        for button in self.buttons:
            if button.pressed:
                button.on_release(button.rect.collidepoint(mouse_pos))
                return True
        return False

    def update(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, (0, 0))

        for label in self.labels.values():
            label.draw(surface)
        for button in self.buttons:
            button.draw(surface)

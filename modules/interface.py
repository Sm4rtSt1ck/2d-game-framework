import pygame
from modules.parameters.colors import *
from modules.parameters.parameters import (TILESIZE, images_path, screenRes,
                                           settings)

pygame.font.init()


fonts_path = settings["fonts_path"]
font_default = "JosefinSans/JosefinSans-Medium.ttf", 30


def nothing(): return


def changeColor(color: tuple) -> tuple:
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
        textColor: tuple = (255, 255, 255),
        font: tuple = font_default
    ) -> None:

        self.coords = (screenRes[0] * coords[0] / 100,
                       screenRes[1] * coords[1] / 100)
        self.size = (screenRes[0] * size[0] / 100,
                     screenRes[1] * size[1] / 100)
        self.color = color[:3]
        self.alpha = color[3] if len(color) == 4 else 255
        self.rect = pygame.Rect(0, 0, *self.size)
        self.rect.center = self.coords
        self.textColor = textColor

        # Text
        self.font = pygame.font.Font(fonts_path+font[0], font[1])
        self.text = self.font.render(text, False, self.textColor)
        self.textPos = (
            self.rect.w // 2 - self.text.get_rect().w // 2,
            self.rect.h // 2 - self.text.get_rect().h // 2)

        # Label surface
        self.surface_default = pygame.Surface(self.size)
        self.surface_default.fill(self.color)
        self.surface_default.blit(self.text, self.textPos)
        self.surface_default.set_alpha(self.alpha)
        self.surface_default.set_colorkey(TRANSPARENT)
        self.surface = self.surface_default

    def changeText(self, text: str, color: tuple = None) -> None:
        self.text = self.font.render(
            text, False, color if color else self.textColor)
        self.textPos = (
            self.rect.w // 2 - self.text.get_rect().w // 2,
            self.rect.h // 2 - self.text.get_rect().h // 2)
        self.surface_default.fill(self.color)
        self.surface_default.blit(self.text, self.textPos)

    def changeBackground(self, color: tuple) -> None:
        """Change the label background color"""
        self.color = color[:3]
        self.alpha = color[3] if len(color) == 4 else 255
        self.surface_default = pygame.Surface(self.size)
        self.surface_default.fill(self.color)
        self.surface_default.blit(self.text, self.textPos)
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
            color2 if color2 is not None else changeColor(self.color))
        self.surface_pressed.blit(self.text, self.textPos)
        self.surface_pressed.set_alpha(self.alpha)
        self.surface_pressed.set_colorkey(TRANSPARENT)

    def onPress(self):
        self.pressed = True

        self.surface = self.surface_pressed

    def onRelease(self, doFunc: bool):
        self.pressed = False
        if doFunc:
            self.func(*self.args)

        self.surface = self.surface_default


def makeButtonTable(
    x: int, y: int,
    rangeStart: int, rangeEnd: int, cols: int,
    colDistance: int, rowDistance: int,
    buttonWidth: int, buttonHeight: int,
    color: tuple,
    textColor: tuple, font: tuple = font_default,
    color2: tuple = None,
    func=nothing,
    *args
) -> list:

    return ([
            Button((x + (button-1) % cols * colDistance,
                    y + (button-1) // cols * rowDistance),
                   (buttonWidth, buttonHeight),
                   color, str(button), textColor, font, color2,
                   func, args[0].replace("*", str(button)), *args[1:])
            for button in range(rangeStart, rangeEnd)
            ])


class ToggledButton(Button):
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
        super().__init__(
            coords, size, color, text, text_color, font, func, *args)

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
        self.text2Pos: tuple = (
            self.rect.w // 2 - self.text2.get_rect().w // 2,
            self.rect.h // 2 - self.text2.get_rect().h // 2)

        # When button is being idle and activated
        self.surface_activated = pygame.Surface(self.size)
        self.surface_activated.fill(self.color2)
        self.surface_activated.blit(self.text2, self.text2Pos)
        self.surface_activated.set_alpha(self.alpha2)
        self.surface_activated.set_colorkey(TRANSPARENT)
        # When button is being pressed and activated
        self.surface_pressedActivated = pygame.Surface(self.size)
        self.surface_pressedActivated.fill(changeColor(self.color2))
        self.surface_pressedActivated.blit(self.text2, self.text2Pos)
        self.surface_pressedActivated.set_alpha(self.alpha2)
        self.surface_pressedActivated.set_colorkey(TRANSPARENT)

    def onPress(self) -> None:
        self.pressed = True

        if self.activated:
            self.surface = self.surface_pressedActivated
        else:
            self.surface = self.surface_pressed

    def onRelease(self, doFunc: bool) -> None:
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
        backgroundColor: tuple,
        text: str,
        color: tuple,
        font: tuple = font_default,
        func=nothing,
        *args
    ) -> None:

        super().__init__(coords, size, backgroundColor,
                         text, color, font, color, func, *args)

        self.coords = (screenRes[0] * coords[0] / 100,
                       screenRes[1] * coords[1] / 100)
        self.size = (screenRes[0] * size[0] / 100,
                     screenRes[1] * size[1] / 100)
        self.points = points
        self.interval = (self.size[0] - 20) / (points - 1)
        self.color = color
        self.backgroundColor = backgroundColor
        self.rect = pygame.Rect(0, 0, *self.size)
        self.rect.center = self.coords
        self.surface = self.createSurface()
        self.surface.set_colorkey(TRANSPARENT)

        self.currentPoint = 0

    def createSurface(self) -> pygame.Surface:
        surface = pygame.Surface(self.size)
        surface.fill(self.backgroundColor)
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
        self.coords = (screenRes[0] * coords[0] / 100,
                       screenRes[1] * coords[1] / 100)
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.rect.center = self.coords
        self.matrix = [[] * cols] * rows  # может возникнуть прикол
        self.labels = labels
        self.buttons = buttons
        self.updateSurface()

    def addRow(self, index: int = None) -> None:
        self.matrix.insert(index, []) if index else self.matrix.append([])

    def addCol(self, index: int = None) -> None:
        if not index:
            index = len(self.matrix[0]) - 1
        for row in self.matrix:
            row.insert(index, [])

    def insertLabel(self, col: int, row: int, label: Label) -> None:
        self.matrix[row][col] = label
        self.updateSurface()

    def getWidth(self):
        width = 0
        for row in self.matrix:
            width = max(width, sum([label.rect.w for label in row]))
        return width

    def getHeight(self):
        height = 0
        for row in self.matrix:
            try:
                height += max([label.rect.h for label in row])
            except ValueError:
                pass
        return height

    def updateSurface(self) -> None:
        self.surface = pygame.Surface((self.getWidth(), self.getHeight()))

    def pressButton(self, mousePos: tuple) -> None:
        for button in self.buttons:
            if button.rect.collidepoint(mousePos):
                button.onPress()

    def releaseButton(self, mousePos: tuple) -> None:
        for button in self.buttons:
            if button.pressed:
                button.onRelease(button.rect.collidepoint(mousePos))

    def update(self, surface: pygame.Surface) -> None:
        for label in self.labels:
            label.draw(self.surface)
        for button in self.buttons:
            button.draw(self.surface)
        surface.blit(self.surface, self.rect)


class MiniMap:
    def __init__(self, levelMatrix: list[list[str]], coords: tuple[int, int],
                 size: int, transparency: int) -> None:
        self.coords = (screenRes[0] * coords[0] / 100,
                       screenRes[1] * coords[1] / 100)
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.center = self.coords
        self.surface = self.createSurface(levelMatrix)
        self.surface = pygame.transform.scale(
            self.surface,
            (self.surface.get_width() * size / 100,
             self.surface.get_height() * size / 100))
        self.surface.set_alpha(transparency)

    def createSurface(self, matrix: list[list[str]]) -> pygame.Surface:
        """Create a top view map of a level"""
        surface = pygame.Surface(
            (len(matrix[0]) * TILESIZE, len(matrix) * TILESIZE))
        for rowIndex, row in enumerate(matrix):
            for colIndex, tile in enumerate(row):
                if tile == "0":
                    continue
                coords = colIndex * TILESIZE, rowIndex * TILESIZE
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

        self.surface = pygame.Surface(screenRes)
        self.surface.set_colorkey(TRANSPARENT)
        self.surface.fill(TRANSPARENT)
        if background_path:
            self.surface.blit(
                pygame.transform.scale(
                    pygame.image.load(
                        images_path + background_path).convert_alpha(),
                    screenRes),
                (0, 0))

    def pressButton(self, mousePos: tuple) -> None:
        for button in self.buttons:
            if button.rect.collidepoint(mousePos):
                button.onPress()

    def releaseButton(self, mousePos: tuple) -> None:
        for button in self.buttons:
            if button.pressed:
                button.onRelease(button.rect.collidepoint(mousePos))

    def update(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, (0, 0))

        for label in self.labels.values():
            label.draw(surface)
        for button in self.buttons:
            button.draw(surface)

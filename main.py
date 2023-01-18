import pygame
from modules import game
from modules.parameters.parameters import screenRes, fps


running = True
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load("resources/icon.ico"))
pygame.display.set_caption("2D Game Engine")
screen = pygame.display.set_mode(screenRes)
mousePos = pygame.mouse.get_pos()
mouseButtons = set()
keyboardKeys = set()
game.init()


def onMouseButton(button: int, pressed: bool) -> None:
    if not pressed:
        mouseButtons.remove(button)
        if button == pygame.BUTTON_LEFT:
            game.currentMenu.releaseButton(mousePos)
        return

    mouseButtons.add(button)

    if button == pygame.BUTTON_LEFT:
        game.currentMenu.pressButton(mousePos)


def onKeyboardKey(key: int, pressed: bool) -> None:
    if not pressed:
        keyboardKeys.remove(key)
        return

    keyboardKeys.add(key)


def update(dt: int) -> None:
    game.update(screen, keyboardKeys, mouseButtons, mousePos, clock, dt)
    pygame.display.flip()


def eventHandling() -> None:
    global running, mousePos

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                running = False
            case pygame.MOUSEBUTTONDOWN:
                onMouseButton(event.button, True)
            case pygame.MOUSEBUTTONUP:
                onMouseButton(event.button, False)
            case pygame.KEYDOWN:
                onKeyboardKey(event.key, True)
            case pygame.KEYUP:
                onKeyboardKey(event.key, False)
            case pygame.MOUSEMOTION:
                mousePos = pygame.mouse.get_pos()
            case pygame.WINDOWRESIZED:
                pass


def main() -> None:
    while running:
        dt = clock.tick(fps)
        eventHandling()
        update(dt)

    pygame.quit()


if __name__ == "__main__":
    main()

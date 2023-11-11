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
pressedButtons = set()
releasedButtons = set()
keyboardKeys = set()
pressedKeys = set()
releasedKeys = set()
game.init()


def onMouseButton(button: int, pressed: bool) -> None:
    if not pressed:
        if button != pygame.BUTTON_LEFT\
                or not game.currentMenu.releaseButton(mousePos):
            mouseButtons.remove(button)
            releasedButtons.add(button)
        return

    if button != pygame.BUTTON_LEFT\
            or not game.currentMenu.pressButton(mousePos):
        mouseButtons.add(button)
        pressedButtons.add(button)


def onKeyboardKey(key: int, pressed: bool) -> None:
    if not pressed:
        keyboardKeys.remove(key)
        releasedKeys.add(key)
        return

    keyboardKeys.add(key)
    pressedKeys.add(key)


def update(dt: int) -> None:
    game.update(surface=screen, keyboardKeys=keyboardKeys,
                pressedKeys=pressedKeys, releasedKeys=releasedKeys,
                mouseButtons=mouseButtons, pressedButtons=pressedButtons,
                releasedButtons=releasedButtons, mousePos=mousePos,
                clock=clock, dt=dt)
    pygame.display.flip()


def eventHandling() -> None:
    global running, mousePos

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                running = False
                game.exitGame()
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

        pressedButtons.clear()
        releasedButtons.clear()
        pressedKeys.clear()
        releasedKeys.clear()

    pygame.quit()


if __name__ == "__main__":
    main()

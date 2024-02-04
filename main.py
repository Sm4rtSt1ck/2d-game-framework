import pygame
from modules import game
from modules.parameters.options import screen_res, fps, title, icon_path


running = True
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load(icon_path))
pygame.display.set_caption(title)
screen = pygame.display.set_mode(screen_res)
mouse_pos = pygame.mouse.get_pos()
mouse_buttons = set()
pressed_buttons = set()
released_buttons = set()
keyboard_keys = set()
pressed_keys = set()
released_keys = set()
game.init()


def on_mouse_button(button: int, pressed: bool) -> None:
    if not pressed:
        if button != pygame.BUTTON_LEFT\
                or not game.current_menu.release_button(mouse_pos):
            mouse_buttons.remove(button)
            released_buttons.add(button)
        return

    if button != pygame.BUTTON_LEFT\
            or not game.current_menu.press_button(mouse_pos):
        mouse_buttons.add(button)
        pressed_buttons.add(button)


def on_keyboard_key(key: int, pressed: bool) -> None:
    if not pressed:
        keyboard_keys.remove(key)
        released_keys.add(key)
        return

    keyboard_keys.add(key)
    pressed_keys.add(key)


def update(dt: int) -> None:
    game.update(surface=screen, keyboard_keys=keyboard_keys,
                pressed_keys=pressed_keys, released_keys=released_keys,
                mouse_buttons=mouse_buttons, pressed_buttons=pressed_buttons,
                released_buttons=released_buttons, mouse_pos=mouse_pos,
                clock=clock, dt=dt)
    pygame.display.flip()


def event_handling() -> None:
    global running, mouse_pos

    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                running = False
                game.exit_game()
            case pygame.MOUSEBUTTONDOWN:
                on_mouse_button(event.button, True)
            case pygame.MOUSEBUTTONUP:
                on_mouse_button(event.button, False)
            case pygame.KEYDOWN:
                on_keyboard_key(event.key, True)
            case pygame.KEYUP:
                on_keyboard_key(event.key, False)
            case pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
            case pygame.WINDOWRESIZED:
                pass


def main() -> None:
    while running:
        dt = clock.tick(fps)
        event_handling()
        update(dt)

        pressed_buttons.clear()
        released_buttons.clear()
        pressed_keys.clear()
        released_keys.clear()

    pygame.quit()


if __name__ == "__main__":
    main()

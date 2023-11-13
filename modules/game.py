import pygame
from os import execv
from sys import executable as sys_exec, argv as sys_argv
from modules import entities, level
from modules.interface import (Button, SwitchButton, Label, Menu, MiniMap,
                               Slider, make_button_table)
from modules.parameters.colors import *
from modules.parameters.parameters import (fps, images_path,
                                           level_when_game_started, music_path,
                                           save_changes, screen_center,
                                           screen_res, sensitivity, volume)

pygame.mixer.init()


game_status: int
current_menu: Menu
current_map: level.Level


# Menu


def goto_menu() -> None:
    global game_status, current_map, current_menu

    # sound_menu = pygame.mixer.Sound(music_path+"main_menu.wav")
    # sound_menu.set_volume(volume)
    # sound_menu.play()

    current_map = None
    game_status = 0
    pygame.mouse.set_visible(1)

    goto_menu_main()


def goto_menu_main() -> None:
    global current_menu
    current_menu = menu_main


def goto_menu_editing() -> None:
    global current_menu
    current_menu = menu_editing_level_selection


def goto_menu_options() -> None:
    global current_menu
    current_menu = menu_options


def goto_menu_level_selection() -> None:
    global current_menu
    current_menu = menu_level_selection


# Editing


def editing_save_changes() -> None:
    current_map.save_changes()


def editing_change_brush():
    current_map.change_brush()
    current_menu.labels["brush"].change_text(current_map.brush)
    current_menu.labels["brush"].change_background(COLORS[current_map.brush])


def editing_change_brush_mode():
    current_map.change_brush_mode()


def goto_edit(level_name: str) -> None:
    global current_map, current_menu, game_status
    current_map = level.EditLevel(level_name)
    current_menu = menu_editing
    game_status = 2


# Other


def goto_game(level_name: str) -> None:
    global game_status, current_map, current_menu, player, mini_map
    current_map = level.World(level_name)
    mini_map = MiniMap(current_map.matrix_terrain, (85, 0), 15, 150)
    current_menu = menu_in_game
    player = entities.Player(coords=current_map.spawn, max_health=100,
                             max_speed=0.7, acceleration=0.01, weight=1,
                             jump_strength=1.5)
    game_status = 1


def change_level(level_name: str) -> None:
    global current_map, mini_map
    current_map = level.World(level_name)
    mini_map = MiniMap(current_map.matrix_terrain, (85, 0), 15, 150)
    player.x, player.y = current_map.spawn


def apply_changes() -> None:
    """Save all settings"""

    save_changes(fps=fps, screen_resolution=screen_res,
                volume=volume, sensitivity=sensitivity)


def exit_game() -> None:
    apply_changes()
    quit()


def update(surface: pygame.Surface, keyboard_keys: set, pressed_keys: set,
           released_keys: set, mouse_buttons: set, pressed_buttons: set,
           released_buttons: set, mouse_pos: tuple,
           clock: pygame.time.Clock, dt: float) -> None:
    """Game tick"""

    if game_status == 1:
        # surface.fill(BLACK)
        current_map.update(surface, dt, player)

        if pygame.K_w in keyboard_keys:
            player.jump()
        if pygame.K_a in keyboard_keys:
            player.move_left(dt)
        if pygame.K_d in keyboard_keys:
            player.move_right(dt)
        if pygame.K_1 in keyboard_keys:
            player.change_slot(0)
        if pygame.K_2 in keyboard_keys:
            player.change_slot(1)
        if pygame.K_3 in keyboard_keys:
            player.change_slot(2)
        if pygame.K_4 in keyboard_keys:
            player.change_slot(3)
        if pygame.K_5 in keyboard_keys:
            player.change_slot(4)

        if pygame.BUTTON_LEFT in mouse_buttons:
            player.attack(mouse_pos)

        player.update(current_map.matrix_terrain,
                      current_map.matrix_triggers, surface, dt)
        match player.triggered[2]:
            case "0":
                pass
            case "CL":
                change_level(current_map.info["next"])

        # if player.triggered:
        #     match player.triggered[2]:
        #         case "1": screamer(surface)
        mini_map.draw(surface)
        current_menu.labels["fps"].change_text(f"FPS: {round(clock.get_fps())}")
        current_menu.labels["health"].change_text(f"{player.get_health()}+")

    elif game_status == 2:
        current_map.update(mouse_pos, surface)

        if pygame.BUTTON_LEFT in mouse_buttons:
            if pygame.BUTTON_LEFT in pressed_buttons:
                current_map.set_start_mouse_pos(mouse_pos)
            current_map.change_tile()
        else:
            if pygame.BUTTON_LEFT in released_buttons:
                current_map.change_tile(False, True)
        if pygame.BUTTON_RIGHT in mouse_buttons:
            if pygame.BUTTON_RIGHT in pressed_buttons:
                current_map.set_start_mouse_pos(mouse_pos)
            current_map.change_tile(True)
        else:
            if pygame.BUTTON_RIGHT in released_buttons:
                current_map.change_tile(True, True)

    current_menu.update(surface)


def init():
    global game_status, current_menu, menu_main, menu_editing, menu_options, \
        menu_in_game, menu_level_selection, menu_editing_level_selection

    menu_main = Menu(
        "backgrounds/menu_main.png",
        buttons={
            Button((50, 25), (20, 13), BLACK, "PLAY", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 60),
                   DARK_GRAY, goto_menu_level_selection),
            Button((50, 40), (25, 13), BLACK, "EDIT", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 60),
                   DARK_GRAY, goto_menu_editing),
            Button((50, 55), (25, 13), BLACK, "OPTIONS", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 60),
                   DARK_GRAY, goto_menu_options),
            Button((50, 70), (20, 13), BLACK, "EXIT", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 60),
                   DARK_GRAY, exit_game)
        }
    )
    menu_level_selection = Menu(
        "backgrounds/menu_main.png",
        labels={
            "title": Label((50, 15), (80, 30), TRANSPARENT, "SELECT LEVEL",
                           BLACK, ("JosefinSans/JosefinSans-Bold.ttf", 100))
        },
        buttons={
            Button((9, 16), (16, 9), BLACK, "BACK", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 30),
                   DARK_GRAY, goto_menu_main),
            *make_button_table(15, 35, 1, 3, 5, 17, 25, 5, 10, BLACK, WHITE,
                             ("JosefinSans/JosefinSans-Bold.ttf", 30),
                             DARK_GRAY, goto_game, "test_*")
        }
    )
    menu_editing_level_selection = Menu(
        "backgrounds/menu_main.png",
        labels={
            "title": Label((50, 15), (80, 30), TRANSPARENT, "LEVEL EDITOR",
                           BLACK, ("JosefinSans/JosefinSans-Bold.ttf", 100))
        },
        buttons={
            Button((9, 16), (16, 9), BLACK, "BACK", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 30),
                   DARK_GRAY, goto_menu_main),
            *make_button_table(15, 35, 1, 3, 5, 17, 25, 5, 10, BLACK, WHITE,
                             ("JosefinSans/JosefinSans-Bold.ttf", 30),
                             DARK_GRAY, goto_edit, "test_*")
        }
    )
    menu_editing = Menu(
        labels={
            "matrix": Label((30, 15), (10, 5), (255, 255, 0, 100), "MATRIX",
                            (60, 30, 85)),
            "brush": Label((70, 15), (10, 5), (255, 255, 0, 100), "BRUSH",
                           (60, 30, 85))
        },
        buttons={
            Button((70, 25), (10, 10), (255, 255, 0, 100), "CHANGE BRUSH",
                   BLUE, func=editing_change_brush),
            SwitchButton((30, 25), (10, 10), (255, 255, 0, 100), "PEN", BLUE,
                         (255, 255, 0), "FILLING", RED,
                         func=editing_change_brush_mode),
            Button((90, 10), (10, 10), (255, 255, 0, 100), "SAVE", BLUE,
                   func=editing_save_changes)
        }
    )
    menu_options = Menu(
        "backgrounds/menu_main.png",
        labels={
            "title": Label((50, 15), (80, 30), TRANSPARENT, "OPTIONS", BLACK,
                           ("JosefinSans/JosefinSans-Bold.ttf", 100))
        },
        buttons={
            Button((9, 16), (16, 9), BLACK, "BACK", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 30),
                   DARK_GRAY, goto_menu_main),
            Button((50, 80), (16, 9), BLACK, "APPLY", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 50),
                   DARK_GRAY, apply_changes),
            Slider((50, 50), (10, 5), 5, BLACK, "aboba", WHITE)
        }
    )
    menu_in_game = Menu(
        labels={
            "health": Label((10, 90), (10, 10), TRANSPARENT,
                            "+100", LIGHT_GRAY,
                            ("JosefinSans/JosefinSans-Bold.ttf", 60)),
            "fps": Label((3, 3), (5, 5), TRANSPARENT,
                         "FPS: 0", LIGHT_GRAY,
                         ("JosefinSans/JosefinSans-Bold.ttf", 18))
        }
    )

    goto_menu()

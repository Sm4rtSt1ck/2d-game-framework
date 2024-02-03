import pygame
from json import load as json_load
from modules import entities, level
from modules.interface import \
    Button, SwitchButton, Label, Menu, MiniMap, Slider, make_button_table
from modules.parameters.colors import *
from modules.parameters.parameters import \
    fps, images_path, level_when_game_started, music_path, save_changes, \
        screen_center, screen_res, sensitivity, volume

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
    current_menu = menus["menu_main"]


def goto_menu_editing() -> None:
    global current_menu
    current_menu = menus["menu_editing_level_selection"]


def goto_menu_options() -> None:
    global current_menu
    current_menu = menus["menu_options"]


def goto_menu_level_selection() -> None:
    global current_menu
    current_menu = menus["menu_level_selection"]


# Editing


def editing_save_changes() -> None:
    current_map.save_changes()


def editing_change_brush():
    current_map.change_brush()
    current_menu.labels["brush"].change_text(current_map.brush)
    current_menu.labels["brush"].change_background(COLORS_SHORT[current_map.brush])


def editing_change_brush_mode():
    current_map.change_brush_mode()


def goto_edit(level_name: str) -> None:
    global current_map, current_menu, game_status
    current_map = level.EditLevel(level_name)
    current_menu = menus["menu_editing"]
    game_status = 2


# Other


def goto_game(level_name: str) -> None:
    global game_status, current_map, current_menu, player, mini_map
    current_map = level.World(level_name)
    mini_map = MiniMap(current_map.matrix_terrain, (85, 0), 15, 150)
    current_menu = menus["menu_in_game"]
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
    global game_status, current_menu, menus

    menus = {}
    with open("settings/layout.json") as layout:
        layout = json_load(layout)
        for menu_name, menu_data in layout.items():
            menus[menu_name] = Menu(
                background_path=menu_data["background_path"]
                    if "background_path" in menu_data else None,
                labels={
                    name: Label(
                        coords=data["coords"],
                        size=data["size"],
                        color=COLORS[data["color"]]
                            if isinstance(data["color"], str) else data["color"],
                        text=data["text"],
                        text_color=COLORS[data["text_color"]]
                            if isinstance(data["text_color"], str) else data["text_color"],
                        font=data["font"] if "font" in data else None
                    ) for name, data in menu_data['labels'].items()
                } if "labels" in menu_data else {},
                buttons={
                    Button(
                        coords=data["coords"],
                        size=data["size"],
                        color=COLORS[data["color"]]
                            if isinstance(data["color"], str) else data["color"],
                        text=data["text"],
                        text_color=COLORS[data["text_color"]]
                            if isinstance(data["text_color"], str) else data["text_color"],
                        font=data["font"] if "font" in data else None,
                        color2=COLORS[data["color2"]]
                            if "color2" in data and isinstance(data["color2"], str)
                            else data["color2"] if "color2" in data else None,
                        func=globals()[data["function"]]
                            if "function" in data else None
                    ) for data in menu_data['buttons']
                } if "buttons" in menu_data else {}
            )
            if "button_tables" in menu_data:
                for button_table in range(len(menu_data["button_tables"])):
                    data = menu_data["button_tables"][button_table]
                    for button in make_button_table(
                            coords=data["coords"],
                            range_limits=data["range"],
                            cols=data["cols"],
                            distances=data["distances"],
                            button_size=data["button_size"],
                            color=COLORS[data["color"]]
                                if isinstance(data["color"], str) else data["color"],
                            text_color=COLORS[data["text_color"]]
                                if isinstance(data["text_color"], str) else data["text_color"],
                            font=data["font"],
                            color2=COLORS[data["color2"]]
                                if isinstance(data["color2"], str) else data["color2"],
                            func=globals()[data["function"]],
                            args=data["function_arguments"]
                        ):
                        menus[menu_name].buttons.add(button)

    goto_menu()

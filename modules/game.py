import pygame
from os import execv
from sys import executable as sys_exec, argv as sys_argv
from modules import entities, level
from modules.interface import (Button, SwitchButton, Label, Menu, MiniMap,
                               Slider, makeButtonTable)
from modules.parameters.colors import *
from modules.parameters.parameters import (fps, images_path,
                                           level_when_game_started, music_path,
                                           saveChanges, screenCenter,
                                           screenRes, sensitivity, volume)

pygame.mixer.init()


gameStatus: int
currentMenu: Menu
currentMap: level.Level


# Menu


def goto_menu() -> None:
    global gameStatus, currentMap, currentMenu

    # sound_menu = pygame.mixer.Sound(music_path+"main_menu.wav")
    # sound_menu.set_volume(volume)
    # sound_menu.play()

    currentMap = None
    gameStatus = 0
    pygame.mouse.set_visible(1)

    goto_menu_main()


def goto_menu_main() -> None:
    global currentMenu
    currentMenu = menu_main


def goto_menu_editing() -> None:
    global currentMenu
    currentMenu = menu_editingLevelSelection


def goto_menu_options() -> None:
    global currentMenu
    currentMenu = menu_options


def goto_menu_levelSelection() -> None:
    global currentMenu
    currentMenu = menu_levelSelection


# Editing


def editing_saveChanges() -> None:
    currentMap.saveChanges()


def editing_changeBrush():
    currentMap.changeBrush()
    currentMenu.labels["brush"].changeText(currentMap.brush)
    currentMenu.labels["brush"].changeBackground(COLORS[currentMap.brush])


def editing_changeBrushMode():
    currentMap.changeBrushMode()


def goto_edit(level_name: str) -> None:
    global currentMap, currentMenu, gameStatus
    currentMap = level.EditLevel(level_name)
    currentMenu = menu_editing
    gameStatus = 2


# Other


def goto_game(level_name: str) -> None:
    global gameStatus, currentMap, currentMenu, player, miniMap
    currentMap = level.World(level_name)
    miniMap = MiniMap(currentMap.matrix_terrain, (85, 0), 15, 150)
    currentMenu = menu_inGame
    player = entities.Player(coords=currentMap.spawn, maxHealth=100,
                             maxSpeed=0.7, acceleration=0.01, weight=1,
                             jumpStrength=1.5)
    gameStatus = 1


def changeLevel(level_name: str) -> None:
    global currentMap, miniMap
    currentMap = level.World(level_name)
    miniMap = MiniMap(currentMap.matrix_terrain, (85, 0), 15, 150)
    player.x, player.y = currentMap.spawn


def apply_changes() -> None:
    """Save all settings and restart the game"""

    saveChanges(fps=fps, screen_resolution=screenRes,
                volume=volume, sensitivity=sensitivity)
    execv(sys_exec, ['python'] + sys_argv)


def exitGame() -> None:
    apply_changes()
    quit()


def update(surface: pygame.Surface, keyboardKeys: set, pressedKeys: set,
           releasedKeys: set, mouseButtons: set, pressedButtons: set,
           releasedButtons: set, mousePos: tuple,
           clock: pygame.time.Clock, dt: float) -> None:
    """Game tick"""

    if gameStatus == 1:
        # surface.fill(BLACK)
        currentMap.update(surface, dt, player)

        if pygame.K_w in keyboardKeys:
            player.jump()
        if pygame.K_a in keyboardKeys:
            player.moveLeft(dt)
        if pygame.K_d in keyboardKeys:
            player.moveRight(dt)
        if pygame.K_1 in keyboardKeys:
            player.changeSlot(0)
        if pygame.K_2 in keyboardKeys:
            player.changeSlot(1)
        if pygame.K_3 in keyboardKeys:
            player.changeSlot(2)
        if pygame.K_4 in keyboardKeys:
            player.changeSlot(3)
        if pygame.K_5 in keyboardKeys:
            player.changeSlot(4)

        if pygame.BUTTON_LEFT in mouseButtons:
            player.attack(mousePos)

        player.update(currentMap.matrix_terrain,
                      currentMap.matrix_triggers, surface, dt)
        match player.triggered[2]:
            case "0":
                pass
            case "CL":
                changeLevel(currentMap.info["next"])

        # if player.triggered:
        #     match player.triggered[2]:
        #         case "1": screamer(surface)
        miniMap.draw(surface)
        currentMenu.labels["fps"].changeText(f"FPS: {round(clock.get_fps())}")
        currentMenu.labels["health"].changeText(f"{player.health}+")

    elif gameStatus == 2:
        currentMap.update(mousePos, surface)

        if pygame.BUTTON_LEFT in mouseButtons:
            if pygame.BUTTON_LEFT in pressedButtons:
                currentMap.setStartMousePos(mousePos)
            currentMap.changeTile()
        else:
            if pygame.BUTTON_LEFT in releasedButtons:
                currentMap.changeTile(False, True)
        if pygame.BUTTON_RIGHT in mouseButtons:
            if pygame.BUTTON_RIGHT in pressedButtons:
                currentMap.setStartMousePos(mousePos)
            currentMap.changeTile(True)
        else:
            if pygame.BUTTON_RIGHT in releasedButtons:
                currentMap.changeTile(True, True)

    currentMenu.update(surface)


def init():
    global gameStatus, currentMenu, menu_main, menu_editing, menu_options, \
        menu_inGame, menu_levelSelection, menu_editingLevelSelection

    menu_main = Menu(
        "backgrounds/menu_main.png",
        buttons={
            Button((50, 25), (20, 13), BLACK, "PLAY", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 60),
                   DARK_GRAY, goto_menu_levelSelection),
            Button((50, 40), (25, 13), BLACK, "EDIT", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 60),
                   DARK_GRAY, goto_menu_editing),
            Button((50, 55), (25, 13), BLACK, "OPTIONS", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 60),
                   DARK_GRAY, goto_menu_options),
            Button((50, 70), (20, 13), BLACK, "EXIT", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 60),
                   DARK_GRAY, exitGame)
        }
    )
    menu_levelSelection = Menu(
        "backgrounds/menu_main.png",
        labels={
            "title": Label((50, 15), (80, 30), TRANSPARENT, "SELECT LEVEL",
                           BLACK, ("JosefinSans/JosefinSans-Bold.ttf", 100))
        },
        buttons={
            Button((9, 16), (16, 9), BLACK, "BACK", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 30),
                   DARK_GRAY, goto_menu_main),
            *makeButtonTable(15, 35, 1, 3, 5, 17, 25, 5, 10, BLACK, WHITE,
                             ("JosefinSans/JosefinSans-Bold.ttf", 30),
                             DARK_GRAY, goto_game, "test_*")
        }
    )
    menu_editingLevelSelection = Menu(
        "backgrounds/menu_main.png",
        labels={
            "title": Label((50, 15), (80, 30), TRANSPARENT, "LEVEL EDITOR",
                           BLACK, ("JosefinSans/JosefinSans-Bold.ttf", 100))
        },
        buttons={
            Button((9, 16), (16, 9), BLACK, "BACK", WHITE,
                   ("JosefinSans/JosefinSans-Bold.ttf", 30),
                   DARK_GRAY, goto_menu_main),
            *makeButtonTable(15, 35, 1, 3, 5, 17, 25, 5, 10, BLACK, WHITE,
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
                   BLUE, func=editing_changeBrush),
            SwitchButton((30, 25), (10, 10), (255, 255, 0, 100), "PEN", BLUE,
                         (255, 255, 0), "FILLING", RED,
                         func=editing_changeBrushMode),
            Button((90, 10), (10, 10), (255, 255, 0, 100), "SAVE", BLUE,
                   func=editing_saveChanges)
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
    menu_inGame = Menu(
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

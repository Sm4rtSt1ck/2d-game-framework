from json import load as load_json, dump as json_dump


with open("settings/project_settings.json") as settings:
    settings = load_json(settings)
images_path = settings["images_path"]
music_path = settings["music_path"]
fonts_path = settings["fonts_path"]
icon_path = settings["icon"]
title = settings["title"]
TILESIZE = settings["tilesize"]

with open("settings/world_settings.json") as world_settings:
    world_settings = load_json(world_settings)
GRAVITY = world_settings["gravity"]
FRICTION = world_settings["friction"]

with open("settings/preferences.json") as preferences:
    preferences = load_json(preferences)
screen_res = tuple(preferences["screen_resolution"])
screen_center = screen_res[0] / 2, screen_res[1] / 2
sensitivity = preferences["sensitivity"]
fps = preferences["fps"]
volume = preferences["volume"]
level_when_game_started = preferences["current_level"]


def save_changes(**parameters) -> None:
    preferences_updated = preferences.copy()
    for parameter, value in parameters.items():
        preferences_updated[parameter] = value
    with open("settings/preferences.json", "w") as settings_raw:
        json_dump(preferences_updated, settings_raw, indent=4)

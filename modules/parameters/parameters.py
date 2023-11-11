from json import load as load_json, dump as json_dump


TILESIZE = 16


with open("settings/settings.json") as settings:
    settings = load_json(settings)

screenRes = tuple(settings["screen_resolution"])
screenCenter = screenRes[0] / 2, screenRes[1] / 2
sensitivity = settings["sensitivity"]
fps = settings["fps"]
images_path = settings["images_path"]
music_path = settings["music_path"]
volume = settings["volume"]
level_when_game_started = settings["current_level"]
fonts_path = settings["fonts_path"]


def saveChanges(**parameters) -> None:
    settings_updated = settings.copy()
    for parameter, value in parameters.items():
        settings_updated[parameter] = value
    with open("settings/settings.json", "w") as settings_raw:
        json_dump(settings_updated, settings_raw, indent=4)

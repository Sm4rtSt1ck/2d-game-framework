import pygame
from json import load as load_json
from modules.parameters.options import TILESIZE, screen_res
from modules.parameters.colors import COLORS_SHORT
from modules import entities


class Level:
    """Main level class"""

    def __init__(self, name: str) -> None:
        """Load level"""
        self.path = "maps/" + name
        # Load matrices
        self.matrix_terrain = self.load_matrix("terrain")
        self.matrix_entities = self.load_matrix("entities")
        self.matrix_triggers = self.load_matrix("triggers")
        # Create surfaces
        self.surface = pygame.Surface((len(self.matrix_terrain[0]) * TILESIZE,
                                       len(self.matrix_terrain) * TILESIZE))
        self.surface_terrain = self.create_surface(self.matrix_terrain)

    def load_matrix(self, name: str) -> list[list[str]]:
        """Create a matrix of a layer"""

        with open(self.path+"/"+name+".map", "r", encoding="utf-8") as f:
            return [row.split() for row in f.read().split("\n")]

    def create_surface(self, matrix: list[list[str]],
                       transparency: int = 100) -> pygame.Surface:
        """Create a surface of a layer"""

        surface = pygame.Surface(screen_res)
        surface.set_alpha(transparency)
        for row_index, row in enumerate(matrix):
            for col_index, tile in enumerate(row):
                if tile == "0":
                    continue
                x, y = col_index * TILESIZE, row_index * TILESIZE
                pygame.draw.rect(surface, COLORS_SHORT[tile], (x, y, TILESIZE, TILESIZE))
        return surface

    def update(self) -> None:
        self.surface.blit(self.surface_terrain, (0, 0))


class World(Level):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.spawn = (0, 0)
        # Info about this level (previous and next levels, etc)
        self.info = load_json(open(self.path + "/info.json"))
        # Other
        self.entities = self.spawnEntities(self.matrix_entities)

    def spawnEntities(self, matrix: list):
        """Create an object of all entities in level"""

        entities.idles.clear()
        entities.movables.clear()
        entities.bullets.clear()
        entities.characters.clear()
        entities.fighters.clear()
        for row_index, row in enumerate(matrix):
            for col_index, tile in enumerate(row):
                if tile == "0":
                    continue
                coords = col_index * TILESIZE, row_index * TILESIZE
                match tile:
                    # Set player spawn
                    case "SP":
                        self.spawn = coords
                    # Spawn different
                    case "TM":
                        entities.movables.append(entities.TestMovable(coords))
                    # Spawn fighters
                    case "TF":
                        entities.fighters.append(entities.TestFighter(coords))
        return entities

    def update(self, surface: pygame.Surface, dt: int, player) -> None:
        super().update()
        # Bullets
        for bullet in self.entities.bullets:
            bullet.update(self.matrix_terrain, self.matrix_triggers, self.surface, dt,
                          {*self.entities.idles, *self.entities.movables,
                           *self.entities.characters, *self.entities.fighters})
        # Idles
        for idle in self.entities.idles:
            idle.update(dt, self.surface)
            if not idle.is_alive():
                self.entities.idles.remove(idle)
        # Movables
        for movable in self.entities.movables:
            movable.update(self.matrix_terrain, self.matrix_triggers, self.surface, dt)
            if not movable.is_alive():
                self.entities.movables.remove(movable)
        # Characters
        for character in self.entities.characters:
            character.update(self.matrix_terrain, self.matrix_triggers, self.surface, dt)
            if not character.is_alive():
                self.entities.characters.remove(character)
        # Fighters
        for fighter in self.entities.fighters:
            fighter.update(self.matrix_terrain, self.matrix_triggers,
                           (player,), self.surface, dt)
            if not fighter.is_alive():
                self.entities.fighters.remove(fighter)

        surface.blit(self.surface, (0, 0))


class EditLevel(Level):
    def __init__(self, name: str) -> None:
        super().__init__(name)

        self.surface_entities = self.create_surface(self.matrix_entities, 50)
        self.suraface_triggers = self.create_surface(self.matrix_triggers, 50)
        self.current_matrix = self.matrix_terrain
        self.current_surface = self.surface_terrain

        # Other
        self.brush = "wh"
        self.brush_mode = 1
        self.start_mouse_pos = (0, 0)
        self.current_mouse_pos = (0, 0)

    def change_brush(self):
        """If I don't rewrite this method, I'll go f*ck myself"""
        self.brush = tuple(COLORS_SHORT.keys())[(
            tuple(COLORS_SHORT.keys()).index(self.brush) + 1
            if tuple(COLORS_SHORT.keys()).index(self.brush) != len(COLORS_SHORT)-1 else 0)]

    def change_tile(self, clear: bool = False, apply: bool = False) -> None:
        """Uses pen or filling tool to change tiles with current brush"""
        if self.brush_mode == 1:
            self.current_matrix[self.current_mouse_pos[1]][self.current_mouse_pos[0]]\
                = "0" if clear else self.brush
            pygame.draw.rect(
                self.current_surface,
                (0, 0, 0, 0) if clear else COLORS_SHORT[self.brush],
                (self.current_mouse_pos[0] * TILESIZE,
                 self.current_mouse_pos[1] * TILESIZE, TILESIZE, TILESIZE))
        elif self.brush_mode == 2:
            if apply:
                for row_index in range(min(self.start_mouse_pos[1], self.current_mouse_pos[1]),
                                       max(self.start_mouse_pos[1], self.current_mouse_pos[1])):
                    for col_index in range(min(self.start_mouse_pos[0], self.current_mouse_pos[0]),
                                           max(self.start_mouse_pos[0], self.current_mouse_pos[0])):
                        self.current_matrix[row_index][col_index] = "0" if clear else self.brush
            pygame.draw.rect(
                self.current_surface if apply else self.surface,
                (0, 0, 0, 0) if clear else COLORS_SHORT[self.brush],
                (min(self.start_mouse_pos[0], self.current_mouse_pos[0]) * TILESIZE,
                 min(self.start_mouse_pos[1], self.current_mouse_pos[1]) * TILESIZE,
                 abs(self.start_mouse_pos[0] - self.current_mouse_pos[0]) * TILESIZE,
                 abs(self.start_mouse_pos[1] - self.current_mouse_pos[1]) * TILESIZE))

    def change_brush_mode(self) -> None:
        self.brush_mode = 1 if self.brush_mode == 2 else 2

    def set_start_mouse_pos(self, mouse_pos: tuple) -> None:
        self.start_mouse_pos = mouse_pos[0] // TILESIZE, mouse_pos[1] // TILESIZE

    def save_changes(self) -> None:
        """Save all changes to .map files"""
        with open(self.path+"/terrain.map", "w") as data:
            data.write("\n".join([" ".join(row) for row in self.matrix_terrain]))
        with open(self.path+"/entities.map", "w") as data:
            data.write("\n".join([" ".join(row) for row in self.matrix_entities]))
        with open(self.path+"/triggers.map", "w") as data:
            data.write("\n".join([" ".join(row) for row in self.matrix_triggers]))

    def update(self, mouse_pos: tuple, surface: pygame.Surface) -> None:
        super().update()

        self.current_mouse_pos = mouse_pos[0] // TILESIZE, mouse_pos[1] // TILESIZE

        surface.blit(self.surface, (0, 0))

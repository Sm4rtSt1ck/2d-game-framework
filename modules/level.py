import pygame
from json import load as load_json
from modules.parameters.parameters import TILESIZE, screenRes
from modules.parameters.colors import COLORS


class Level:
    """Main level class"""

    def __init__(self, name: str) -> None:
        """Load level"""
        self.spawn = (0, 0)
        self.path = "maps/" + name
        self.info = load_json(open(self.path + "/info.json"))
        # Load matrices
        self.matrix_terrain = self.loadMatrix("terrain")
        self.matrix_entities = self.loadMatrix("entities")
        self.matrix_triggers = self.loadMatrix("triggers")
        # Create surfaces
        self.surface = pygame.Surface((len(self.matrix_terrain[0]) * TILESIZE,
                                       len(self.matrix_terrain) * TILESIZE))
        self.surface_terrain = self.createSurface(self.matrix_terrain)
        # Other
        self.entities = self.spawnEntities(self.matrix_entities)

    def loadMatrix(self, name: str) -> list[list[str]]:
        """Create a matrix of a layer"""
        with open(self.path+"/"+name+".map", "r", encoding="utf-8") as f:
            return [row.split() for row in f.read().split("\n")]

    def createSurface(self, matrix: list[list[str]]) -> pygame.Surface:
        surface = pygame.Surface(screenRes)
        for rowIndex, row in enumerate(matrix):
            for colIndex, tile in enumerate(row):
                if tile == "0":
                    continue
                x, y = colIndex * TILESIZE, rowIndex * TILESIZE
                pygame.draw.rect(surface, COLORS[tile],
                                 (x, y, TILESIZE, TILESIZE))
        return surface

    def spawnEntities(self, matrix: list):
        """Create an object of all entities in level"""
        from modules import entities
        entities.idles.clear()
        entities.movables.clear()
        entities.bullets.clear()
        entities.characters.clear()
        entities.fighters.clear()
        for rowIndex, row in enumerate(matrix):
            for colIndex, tile in enumerate(row):
                if tile == "0":
                    continue
                coords = colIndex * TILESIZE, rowIndex * TILESIZE
                match tile:
                    # Set player spawn
                    case "1":
                        self.spawn = coords
                    # Spawn different
                    case "2":
                        entities.movables.append(entities.TestMovable(coords))
                    # Spawn fighters
                    case "100":
                        entities.fighters.append(entities.TestFighter(coords))
        # return entitiesSet
        return entities

    def update(self, surface: pygame.Surface, dt: int, player) -> None:
        self.surface.blit(self.surface_terrain, (0, 0))

        # Bullets
        for bullet in self.entities.bullets:
            bullet.update(self.matrix_terrain, self.matrix_triggers,
                          self.surface, dt,
                          {*self.entities.idles, *self.entities.movables,
                           *self.entities.characters, *self.entities.fighters})
        # Idles
        for idle in self.entities.idles:
            idle.update(self.surface, dt)
            if not idle.alive:
                self.entities.idles.remove(idle)
        # Movables
        for movable in self.entities.movables:
            movable.update(self.matrix_terrain,
                           self.matrix_triggers, self.surface, dt)
            if not movable.alive:
                self.entities.movables.remove(movable)
        # Characters
        for character in self.entities.characters:
            character.update(self.matrix_terrain,
                             self.matrix_triggers, self.surface, dt)
            if not character.alive:
                self.entities.characters.remove(character)
        # Fighters
        for fighter in self.entities.fighters:
            fighter.update(self.matrix_terrain, self.matrix_triggers,
                           (player,), self.surface, dt)
            if not fighter.alive:
                self.entities.fighters.remove(fighter)

        # if fighter.triggered and fighter.triggered[2] == SOMETHING:
        #     figher.SOMETHING()

        surface.blit(self.surface, (0, 0))

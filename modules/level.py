import pygame
from json import load as load_json
from modules.parameters.parameters import TILESIZE, screenRes
from modules.parameters.colors import COLORS


class Level:
    """Main level class"""

    def __init__(self, name: str) -> None:
        """Load level"""
        self.path = "maps/" + name
        # Load matrices
        self.matrix_terrain = self.loadMatrix("terrain")
        self.matrix_entities = self.loadMatrix("entities")
        self.matrix_triggers = self.loadMatrix("triggers")
        # Create surfaces
        self.surface = pygame.Surface((len(self.matrix_terrain[0]) * TILESIZE,
                                       len(self.matrix_terrain) * TILESIZE))
        self.surface_terrain = self.createSurface(self.matrix_terrain)

    def loadMatrix(self, name: str) -> list[list[str]]:
        """Create a matrix of a layer"""
        with open(self.path+"/"+name+".map", "r", encoding="utf-8") as f:
            return [row.split() for row in f.read().split("\n")]

    def createSurface(self, matrix: list[list[str]],
                      transparency: int = 100) -> pygame.Surface:
        """Create a matrix of a layer"""
        surface = pygame.Surface(screenRes)
        surface.set_alpha(transparency)
        for rowIndex, row in enumerate(matrix):
            for colIndex, tile in enumerate(row):
                if tile == "0":
                    continue
                x, y = colIndex * TILESIZE, rowIndex * TILESIZE
                pygame.draw.rect(surface, COLORS[tile],
                                 (x, y, TILESIZE, TILESIZE))
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

        surface.blit(self.surface, (0, 0))


class EditLevel(Level):
    def __init__(self, name: str) -> None:
        super().__init__(name)

        self.surface_entities = self.createSurface(self.matrix_entities, 50)
        self.suraface_triggers = self.createSurface(self.matrix_triggers, 50)
        self.currentMatrix = self.matrix_terrain
        self.currentSurface = self.surface_terrain

        # Other
        self.brush = "wh"
        self.brushMode = 1
        self.startMousePos = (0, 0)
        self.currMousePos = (0, 0)

    def changeBrush(self):
        """If I don't rewrite this method, I'll go f*ck myself"""
        self.brush = tuple(COLORS.keys())[(
            tuple(COLORS.keys()).index(self.brush) + 1
            if tuple(COLORS.keys()).index(self.brush) != len(COLORS)-1 else 0)]

    def changeTile(self, clear: bool = False, apply: bool = False) -> None:
        """Uses pen or filling tool to change tiles with current brush"""
        if self.brushMode == 1:
            self.currentMatrix[self.currMousePos[1]][self.currMousePos[0]]\
                = "0" if clear else self.brush
            pygame.draw.rect(
                self.currentSurface,
                (0, 0, 0, 0) if clear else COLORS[self.brush],
                (self.currMousePos[0] * TILESIZE,
                 self.currMousePos[1] * TILESIZE, TILESIZE, TILESIZE))
        elif self.brushMode == 2:
            if apply:
                for rowIndex in range(min(self.startMousePos[1],
                                          self.currMousePos[1]),
                                      max(self.startMousePos[1],
                                          self.currMousePos[1])):
                    for colIndex in range(min(self.startMousePos[0],
                                              self.currMousePos[0]),
                                          max(self.startMousePos[0],
                                              self.currMousePos[0])):
                        self.currentMatrix[rowIndex][colIndex] =\
                            "0" if clear else self.brush
            pygame.draw.rect(
                self.currentSurface if apply else self.surface,
                (0, 0, 0, 0) if clear else COLORS[self.brush],
                (min(self.startMousePos[0], self.currMousePos[0]) * TILESIZE,
                 min(self.startMousePos[1], self.currMousePos[1]) * TILESIZE,
                 abs(self.startMousePos[0] - self.currMousePos[0]) * TILESIZE,
                 abs(self.startMousePos[1] - self.currMousePos[1]) * TILESIZE))

    def changeBrushMode(self) -> None:
        self.brushMode = 1 if self.brushMode == 2 else 2

    def setStartMousePos(self, mousePos: tuple) -> None:
        self.startMousePos = mousePos[0] // TILESIZE, mousePos[1] // TILESIZE

    def saveChanges(self) -> None:
        """Save all changes to .map files"""
        with open(self.path+"/terrain.map", "w") as data:
            data.write("\n".join(
                [" ".join(row) for row in self.matrix_terrain]))
        with open(self.path+"/entities.map", "w") as data:
            data.write("\n".join(
                [" ".join(row) for row in self.matrix_entities]))
        with open(self.path+"/triggers.map", "w") as data:
            data.write("\n".join(
                [" ".join(row) for row in self.matrix_triggers]))

    def update(self, mousePos: tuple, surface: pygame.Surface) -> None:
        super().update()

        self.currMousePos = mousePos[0] // TILESIZE, mousePos[1] // TILESIZE

        surface.blit(self.surface, (0, 0))

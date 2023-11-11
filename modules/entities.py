import pygame
from math import sin, cos, degrees, atan2
from modules import maths, physics, weapons
from modules.parameters.parameters import TILESIZE, images_path


class SpriteSheet:
    def __init__(
        self,
        spritePath: str,
        cols: int, rows: int,
        frameDelay: int,
        rotation: float = 0,
        size: tuple[int, int] = None,
        colorKey: tuple[int, int, int] = None
    ) -> None:

        self.spriteSheetCols, self.spriteSheetRows = cols, rows
        self.frameDelay = frameDelay
        self.rotation = rotation

        self.sheet = pygame.image.load(images_path+spritePath)
        if size is not None:
            self.width, self.height = size
            self.sheet = pygame.transform.scale(self.sheet,
                                   (self.width * self.spriteSheetCols,
                                    self.height * self.spriteSheetRows))
        else:
            self.width, self.height = (
                self.sheet.get_width() // self.spriteSheetCols,
                self.sheet.get_height() // self.spriteSheetRows)
        if colorKey is not None:
            self.sheet.set_colorkey(colorKey)

        self.curCol, self.curRow = 0, 0
        self.shift_x, self.shift_y = 0, 0
        self.timePassedSinceFrame = 0

    def update(self, dt: int, surface: pygame.Surface) -> None:
        surface.blit(self.sheet, (self.x, self.y),
                     (self.shift_x, self.shift_y, self.width, self.height))
        self.timePassedSinceFrame += dt
        if self.timePassedSinceFrame >= self.frameDelay:
            self.timePassedSinceFrame = 0
            self.curCol += 1
            if self.curCol == self.spriteSheetCols:
                self.curCol = 0
                self.curRow += 1
                if self.curRow == self.spriteSheetRows:
                    self.curRow = 0
            self.shift_x = self.curCol * self.width
            self.shift_y = self.curRow * self.height


class Entity(SpriteSheet):
    def __init__(
        self,
        coords: tuple,
        maxHealth: int,
        spritePath: str,
        size: tuple[int, int] = None,
        rotation: float = 0,
        spriteSheetCols: int = 1, spriteSheetRows: int = 1,
        spriteFrameDelay: int = 0,
        spriteColorKey: tuple[int, int, int] = None
    ) -> None:

        super().__init__(spritePath=spritePath, cols=spriteSheetCols,
                         rows=spriteSheetRows, frameDelay=spriteFrameDelay,
                         size=size, rotation=rotation, colorKey=spriteColorKey)
        self.x, self.y = coords
        self.maxHealth = maxHealth
        self.health = self.maxHealth

        self.center = self.width / 2, self.height / 2
        self.eyes = self.x + self.center[0], self.y + self.center[1]

        self.alive = True

    def getDamage(self, damage: int) -> None:
        self.health -= damage

    def die(self) -> None:
        self.alive = False

    def checkCollision(self, x: int, y: int, width: int, height: int) -> bool:
        return (self.x <= x <= self.x + self.width
                or self.x <= x + width <= self.x + width)\
               and (self.y <= y <= self.y + self.height
                    or self.y <= y + height <= self.y + height)

    def update(self, dt: int, surface: pygame.Surface) -> None:
        super().update(dt=dt, surface=surface)
        if self.health <= 0:
            self.die()


idles: list[Entity] = list()


class Sprite(Entity):
    def __init__(
        self,
        coords: tuple[int, int],
        spritePath: str,
        size: tuple[int, int] = None,
        rotation: float = 0,
        spriteSheetCols: int = 1, spriteSheetRows: int = 1,
        spriteFrameDelay: int = 0, cycles: int = 1,  # -1 = infinite
        spriteColorKey: tuple[int, int, int] = None
    ) -> None:

        super().__init__(coords=coords, maxHealth=1, spritePath=spritePath,
                         size=size, rotation=rotation, spriteSheetCols=spriteSheetCols,
                         spriteSheetRows=spriteSheetRows,
                         spriteFrameDelay=spriteFrameDelay,
                         spriteColorKey=spriteColorKey)
        self.cycles = cycles
        self.curCycle = 0

    def update(self, dt: int, surface: pygame.Surface) -> None:
        super().update(dt, surface)
        if self.curRow == 0 and self.curCol == 0 and\
                self.timePassedSinceFrame == 0:
            self.curCycle += 1
        if self.curCycle == self.cycles:
            self.die()


class Movable(Entity):
    def __init__(
        self,
        coords: tuple,
        maxHealth: int,
        maxSpeed: float,
        acceleration: float,
        weight: float,
        spritePath: str = None,
        size: tuple = None,
        rotation: float = 0
    ) -> None:

        super().__init__(coords=coords, maxHealth=maxHealth,
                         spritePath=spritePath, size=size, rotation=rotation)

        self.maxSpeed = maxSpeed
        self.speed_x, self.speed_y = 0, 0
        self.speed: float = 0
        self.acceleration = acceleration
        self.weight = weight

        self.onGround: bool = False
        self.collided_x: tuple[int, int, str] = [self.x, self.y, "0"]
        self.collided_y: tuple[int, int, str] = [self.x, self.y, "0"]
        self.triggered: tuple[int, int, str] = [self.x, self.y, "0"]

    def moveRight(self, dt: float) -> None:
        dt_acceleration = self.acceleration * dt
        if self.speed_x < self.maxSpeed + dt_acceleration:
            self.speed_x += dt_acceleration

    def moveLeft(self, dt: float) -> None:
        dt_acceleration = self.acceleration * dt
        if self.speed_x > -self.maxSpeed - dt_acceleration:
            self.speed_x -= self.acceleration * dt

    def update(
        self,
        mapTerrain: list[list[str]],
        mapTriggers: list[list[str]],
        surface: pygame.Surface,
        dt: int
    ) -> None:
        """Update a character"""
        super().update(dt=dt, surface=surface)

        self.speed_x *= physics.FRICTION[self.collided_y[2]]

        dt_speed_x = self.speed_x * dt
        dt_speed_y = self.speed_y * dt

        # X collision
        area = physics.area_x(
            self.x, self.y, dt_speed_x, self.width, self.height)
        self.collided_x = physics.collision_x(area, mapTerrain)
        if self.collided_x[2] != "0":
            if area[1] == 1:
                self.x = self.collided_x[0] - self.width
            else:
                self.x = self.collided_x[0] + TILESIZE
            self.speed_x = 0
            triggered_x = (self.x, self.y, "0")
        else:
            self.x += dt_speed_x
            triggered_x = physics.collision_x(area, mapTriggers)

        # Y collision
        area = physics.area_y(
            self.x, self.y, dt_speed_y, self.width, self.height)
        self.collided_y = physics.collision_y(area, mapTerrain)
        if self.collided_y[2] != "0":
            if area[1] == 1:
                self.y = self.collided_y[1] - self.height
                self.onGround = True
            else:
                self.y = self.collided_y[1] + TILESIZE
            self.speed_y = 0
            triggered_y = (self.x, self.y, "0")
        else:
            self.y += dt_speed_y
            self.onGround = False
            triggered_y = physics.collision_y(area, mapTriggers)
            self.speed_y += physics.applyGravity(self.weight) * dt

        self.eyes = self.x + self.center[0], self.y + self.center[1]

        self.triggered = triggered_x if triggered_x[2] != "0" else triggered_y


movables: list[Movable] = list()


class Bullet(Movable):
    def __init__(
        self,
        coords: tuple[int, int],
        speed: float,
        weight: float,
        angle: float,
        spritePath: str = None,
        size: tuple = None
    ) -> None:
        super().__init__(coords=coords, maxHealth=1, maxSpeed=speed,
                         acceleration=0, weight=weight, spritePath=spritePath,
                         size=size, rotation=angle)
        self.sheet = pygame.transform.rotate(self.sheet, -degrees(self.rotation))
        self.speed_x, self.speed_y = cos(angle) * speed, sin(angle) * speed
        self.damage = maths.calculateDamage(speed, self.height)

    def die(self) -> None:
        super().die()
        idles.append(Sprite(coords=(self.x, self.y),
                            spritePath="other/spark.png", size=(20, 20),
                            rotation=self.rotation,
                            spriteSheetCols=6, spriteSheetRows=1,
                            spriteFrameDelay=30, cycles=1))
        bullets.remove(self)

    def update(
        self,
        mapTerrain: list[list[str]], mapTriggers: list[list[str]],
        surface: pygame.Surface,
        dt: int,
        entities: set[Entity]
    ) -> None:
        super().update(mapTerrain=mapTerrain, mapTriggers=mapTriggers,
                       surface=surface, dt=dt)
        for entity in entities:
            if self.checkCollision(entity.x, entity.y,
                                   entity.width, entity.height):
                entity.getDamage(self.damage)
                bullets.remove(self)
                return
        if self.collided_x[2] != "0" or self.collided_y[2] != "0":
            self.die()


bullets: list[Bullet] = list()


class Character(Movable):
    def __init__(
        self,
        coords: tuple,
        maxHealth: int,
        maxSpeed: float,
        acceleration: float,
        weight: float,
        jumpStrength: float,
        spritePath: str = None,
        size: tuple = None
    ) -> None:

        super().__init__(coords=coords, maxHealth=maxHealth, maxSpeed=maxSpeed,
                         acceleration=acceleration, weight=weight,
                         spritePath="characters/"+spritePath, size=size)
        self.jumpStrength = jumpStrength

    def jump(self) -> None:
        if self.onGround:
            self.speed_y = -self.jumpStrength
            self.onGround = False
            # self.speed_x *= 1.2

    def dialog(self) -> None: ...

    def attack(self, entity: Entity) -> None:
        entity.getDamage(self.attackDamage)

    def update(
        self,
        mapTerrain: list[list[str]],
        mapTriggers: list[list[str]],
        surface: pygame.Surface,
        dt: int
    ) -> None:
        super().update(mapTerrain=mapTerrain, mapTriggers=mapTriggers,
                       surface=surface, dt=dt)


characters: list[Character] = list()


class Fighter(Character):
    def __init__(
        self,
        coords: tuple,
        maxHealth: int,
        maxSpeed: float,
        acceleration: float,
        weight: float,
        jumpStrength: float,

        visionRange: int,
        attackDamage: int,
        attackRange: int,
        attackDelay: int,
        spritePath: str = None,
        size: tuple = None
    ) -> None:

        super().__init__(coords=coords, maxHealth=maxHealth, maxSpeed=maxSpeed,
                         acceleration=acceleration, weight=weight,
                         jumpStrength=jumpStrength, spritePath=spritePath,
                         size=size)

        self.visionRange = visionRange
        self.attackRange = attackRange
        self.attackDelay = attackDelay
        self.attackDamage = attackDamage

        self.timePassedSinceAttack = 0

    def interact(self, enemies: list[Entity], dt: int) -> None:
        """Interaction with enemies"""
        for enemy in enemies:
            distance = maths.calculateDistance(
                (self.x, self.y), (enemy.x, enemy.y))

            if self.attackRange < distance < self.visionRange:
                if self.eyes[0] > enemy.eyes[0]:
                    self.moveLeft(dt)
                else:
                    self.moveRight(dt)
                if self.collided_x[2] != "0":
                    self.jump()
            elif distance <= self.attackRange:
                self.attack(enemy)

    def attack(self, enemy: Entity) -> None:
        if self.timePassedSinceAttack >= self.attackDelay:
            enemy.getDamage(self.attackDamage)
            self.timePassedSinceAttack = 0

    def update(
        self,
        mapTerrain: list[list[str]],
        mapTriggers: list[list[str]],
        enemies: set[Entity],
        surface: pygame.Surface,
        dt: int
    ) -> None:
        super().update(mapTerrain=mapTerrain, mapTriggers=mapTriggers,
                       surface=surface, dt=dt)
        self.interact(enemies, dt)
        self.timePassedSinceAttack += dt


fighters: list[Fighter] = list()


class Player(Character):
    def __init__(
        self,
        coords: tuple,
        maxHealth: int,
        maxSpeed: float,
        acceleration: float,
        weight: float,
        jumpStrength: float,
        size: tuple = None
    ) -> None:

        super().__init__(coords=coords, maxHealth=maxHealth, maxSpeed=maxSpeed,
                         acceleration=acceleration, weight=weight,
                         jumpStrength=jumpStrength, spritePath="player.png",
                         size=size)
        self.slots = [0, 0, 0, 0, 0]

        # MUST BE DELETED!
        self.slots[1] = weapons.ShootingWeapon(
            caliber=10, bulletSpeed=1.5, shotDelay=140)
        self.selectedSlot = 1

    def attack(self, mousePos: tuple) -> None:
        angle = atan2(mousePos[1] - self.eyes[1], mousePos[0] - self.eyes[0])
        self.slots[self.selectedSlot].shoot(self.eyes, angle)

    def changeSlot(self, slot: int) -> None:
        if self.slots[slot] != 0:
            self.selectedSlot = slot

    def update(
        self,
        mapTerrain: list[list[str]],
        mapTriggers: list[list[str]],
        surface: pygame.Surface,
        dt: int
    ) -> None:
        super().update(mapTerrain=mapTerrain, mapTriggers=mapTriggers,
                       surface=surface, dt=dt)
        for tool in self.slots:
            if tool != 0:
                tool.update(self.x, self.y, dt, surface)


# TEST ENTITIES

class TestMovable(Movable):
    def __init__(
        self,
        coords: tuple
    ) -> None:
        super().__init__(coords=coords, maxHealth=100, maxSpeed=0,
                         acceleration=0, weight=1,
                         spritePath="characters/fighter_test.png",
                         size=(64, 64))


class TestFighter(Fighter):
    def __init__(
        self,
        coords: tuple
    ) -> None:

        super().__init__(coords=coords, maxHealth=100, maxSpeed=0.7,
                         acceleration=0.01, weight=1, jumpStrength=1.5,
                         visionRange=300, attackDamage=15, attackRange=120,
                         attackDelay=1000, spritePath="fighter_test.png",
                         size=(64, 64))

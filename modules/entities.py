import pygame
from math import sin, cos, degrees, atan2
from modules import maths, weapons
from modules.physics import *
from modules.parameters.options import TILESIZE, images_path, FRICTION


class SpriteSheet:
    def __init__(
        self,
        sprite_path: str,
        cols: int, rows: int,
        frame_delay: int,
        rotation: float = 0,
        size: tuple[int, int] = None,
        colorkey: tuple[int, int, int] = None
    ) -> None:

        self.sprite_sheet_cols, self.sprite_sheet_rows = cols, rows
        self.frame_delay = frame_delay
        self.rotation = rotation

        self.sheet = pygame.image.load(images_path+sprite_path)
        if size is not None:
            self._width, self._height = size
            self.sheet = pygame.transform.scale(
                self.sheet, (self._width * self.sprite_sheet_cols,
                             self._height * self.sprite_sheet_rows))
        else:
            self._width = self.sheet.get_width() // self.sprite_sheet_cols
            self._height = self.sheet.get_height() // self.sprite_sheet_rows
        if colorkey is not None:
            self.sheet.set_colorkey(colorkey)

        self.current_col, self.current_row = 0, 0
        self.shift_x, self.shift_y = 0, 0
        self.time_passed_since_frame = 0

    def get_size(self) -> tuple[int, int]:
        return self._width, self._height

    def update(self, dt: int, surface: pygame.Surface) -> None:
        surface.blit(self.sheet, (self.x, self.y),
                     (self.shift_x, self.shift_y, self._width, self._height))
        self.time_passed_since_frame += dt
        if self.time_passed_since_frame >= self.frame_delay:
            self.time_passed_since_frame = 0
            self.current_col += 1
            if self.current_col == self.sprite_sheet_cols:
                self.current_col = 0
                self.current_row += 1
                if self.current_row == self.sprite_sheet_rows:
                    self.current_row = 0
            self.shift_x = self.current_col * self._width
            self.shift_y = self.current_row * self._height


class Entity(SpriteSheet):
    def __init__(
        self,
        coords: tuple,
        max_health: int,
        sprite_path: str,
        size: tuple[int, int] = None,
        rotation: float = 0,
        sprite_sheet_cols: int = 1, sprite_sheet_rows: int = 1,
        sprite_frame_delay: int = 0,
        sprite_color_key: tuple[int, int, int] = None
    ) -> None:

        super().__init__(sprite_path=sprite_path, cols=sprite_sheet_cols,
                         rows=sprite_sheet_rows, frame_delay=sprite_frame_delay,
                         size=size, rotation=rotation, colorkey=sprite_color_key)
        self.x, self.y = coords
        self.max_health = max_health
        self.__health = max_health

        self.center = self._width / 2, self._height / 2
        self.eyes = self.x + self.center[0], self.y + self.center[1]

        self.__alive = True

    def take_damage(self, damage: int) -> None:
        self.__health -= damage

    def _die(self) -> None:
        self.__alive = False

    def get_health(self) -> int:
        return self.__health

    def is_alive(self) -> bool:
        return self.__alive

    def update(self, dt: int, surface: pygame.Surface) -> None:
        super().update(dt=dt, surface=surface)
        if self.__health <= 0:
            self._die()


idles: list[Entity] = list()


class Sprite(Entity):
    def __init__(
        self,
        coords: tuple[int, int],
        sprite_path: str,
        size: tuple[int, int] = None,
        rotation: float = 0,
        sprite_sheet_cols: int = 1, sprite_sheet_rows: int = 1,
        sprite_frame_delay: int = 0, cycles: int = 1,  # -1 = infinite
        sprite_color_key: tuple[int, int, int] = None
    ) -> None:

        super().__init__(coords=coords, max_health=1, sprite_path=sprite_path,
                         size=size, rotation=rotation, sprite_sheet_cols=sprite_sheet_cols,
                         sprite_sheet_rows=sprite_sheet_rows,
                         sprite_frame_delay=sprite_frame_delay,
                         sprite_color_key=sprite_color_key)
        self.cycles = cycles
        self.current_cycle = 0

    def update(self, dt: int, surface: pygame.Surface) -> None:
        super().update(dt, surface)
        if self.current_row == 0 and self.current_col == 0 and\
                self.time_passed_since_frame == 0:
            self.current_cycle += 1
        if self.current_cycle == self.cycles:
            self._die()


class Movable(Entity):
    def __init__(
        self,
        coords: tuple,
        max_health: int,
        max_speed: float,
        acceleration: float,
        weight: float,
        sprite_path: str = None,
        size: tuple = None,
        rotation: float = 0
    ) -> None:

        super().__init__(coords=coords, max_health=max_health,
                         sprite_path=sprite_path, size=size, rotation=rotation)

        self._max_speed = max_speed
        self._speed_x, self._speed_y = 0, 0
        self._acceleration = acceleration
        self._weight = weight

        self._on_ground: bool = False
        self.collided_x: tuple[int, int, str] = [self.x, self.y, "0"]
        self.collided_y: tuple[int, int, str] = [self.x, self.y, "0"]
        self.triggered: tuple[int, int, str] = [self.x, self.y, "0"]

    def move_right(self, dt: float) -> None:
        dt_acceleration = self._acceleration * dt
        if self._speed_x < self._max_speed + dt_acceleration:
            self._speed_x += dt_acceleration

    def move_left(self, dt: float) -> None:
        dt_acceleration = self._acceleration * dt
        if self._speed_x > -self._max_speed - dt_acceleration:
            self._speed_x -= self._acceleration * dt

    def update(
        self,
        map_terrain: list[list[str]],
        map_triggers: list[list[str]],
        surface: pygame.Surface,
        dt: int
    ) -> None:
        """Update a character"""
        super().update(dt=dt, surface=surface)

        self._speed_x *= FRICTION[self.collided_y[2]]

        dt_speed_x = self._speed_x * dt
        dt_speed_y = self._speed_y * dt

        # X collision
        area = calc_area_x(
            self.x, self.y, dt_speed_x, self._width, self._height)
        self.collided_x = check_collision_x(area, map_terrain)
        if self.collided_x[2] != "0":
            if area[1] == 1:
                self.x = self.collided_x[0] - self._width
            else:
                self.x = self.collided_x[0] + TILESIZE
            self._speed_x = 0
            triggered_x = (self.x, self.y, "0")
        else:
            self.x += dt_speed_x
            triggered_x = check_collision_x(area, map_triggers)

        # Y collision
        area = calc_area_y(
            self.x, self.y, dt_speed_y, self._width, self._height)
        self.collided_y = check_collision_y(area, map_terrain)
        if self.collided_y[2] != "0":
            if area[1] == 1:
                self.y = self.collided_y[1] - self._height
                self._on_ground = True
            else:
                self.y = self.collided_y[1] + TILESIZE
            self._speed_y = 0
            triggered_y = (self.x, self.y, "0")
        else:
            self.y += dt_speed_y
            self._on_ground = False
            triggered_y = check_collision_y(area, map_triggers)
            self._speed_y += apply_gravity(self._weight) * dt

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
        sprite_path: str = None,
        size: tuple = None
    ) -> None:
        super().__init__(coords=coords, max_health=1, max_speed=speed,
                         acceleration=0, weight=weight, sprite_path=sprite_path,
                         size=size, rotation=angle)
        self.sheet = pygame.transform.rotate(self.sheet, -degrees(self.rotation))
        self._speed_x, self._speed_y = cos(angle) * speed, sin(angle) * speed
        self.__damage = maths.calculate_damage(speed, self._height)

    def _die(self) -> None:
        super()._die()
        idles.append(Sprite(coords=(self.x, self.y),
                            sprite_path="other/spark.png", size=(20, 20),
                            rotation=self.rotation,
                            sprite_sheet_cols=6, sprite_sheet_rows=1,
                            sprite_frame_delay=30, cycles=1))
        bullets.remove(self)

    def update(
        self,
        map_terrain: list[list[str]], map_triggers: list[list[str]],
        surface: pygame.Surface,
        dt: int,
        entities: set[Entity]
    ) -> None:
        super().update(map_terrain=map_terrain, map_triggers=map_triggers,
                       surface=surface, dt=dt)
        for entity in entities:
            if entity_collision(self.x, self.y, self._width, self._height,
                                        entity.x, entity.y,
                                        *entity.get_size()):
                entity.take_damage(self.__damage)
                bullets.remove(self)
                return
        if self.collided_x[2] != "0" or self.collided_y[2] != "0":
            self._die()


bullets: list[Bullet] = list()


class Character(Movable):
    def __init__(
        self,
        coords: tuple,
        max_health: int,
        max_speed: float,
        acceleration: float,
        weight: float,
        jump_strength: float,
        sprite_path: str = None,
        size: tuple = None
    ) -> None:

        super().__init__(coords=coords, max_health=max_health, max_speed=max_speed,
                         acceleration=acceleration, weight=weight,
                         sprite_path="characters/"+sprite_path, size=size)
        self._jump_strength = jump_strength

    def jump(self) -> None:
        if self._on_ground:
            self._speed_y = -self._jump_strength
            self._on_ground = False
            # self._speed_x *= 1.2

    def dialog(self) -> None: ...

    def attack(self, entity: Entity) -> None:
        entity.take_damage(self._attack_damage)

    def update(
        self,
        map_terrain: list[list[str]],
        map_triggers: list[list[str]],
        surface: pygame.Surface,
        dt: int
    ) -> None:
        super().update(map_terrain=map_terrain, map_triggers=map_triggers,
                       surface=surface, dt=dt)


characters: list[Character] = list()


class Fighter(Character):
    def __init__(
        self,
        coords: tuple,
        max_health: int,
        max_speed: float,
        acceleration: float,
        weight: float,
        jump_strength: float,

        vision_range: int,
        attack_damage: int,
        attack_range: int,
        attack_delay: int,
        sprite_path: str = None,
        size: tuple = None
    ) -> None:

        super().__init__(coords=coords, max_health=max_health, max_speed=max_speed,
                         acceleration=acceleration, weight=weight,
                         jump_strength=jump_strength, sprite_path=sprite_path,
                         size=size)

        self._vision_range = vision_range
        self._attack_range = attack_range
        self._attack_delay = attack_delay
        self._attack_damage = attack_damage

        self._time_passed_since_attack = 0

    def interact(self, enemies: list[Entity], dt: int) -> None:
        """Interaction with enemies"""
        for enemy in enemies:
            distance = maths.calculate_distance(
                (self.x, self.y), (enemy.x, enemy.y))

            if self._attack_range < distance < self._vision_range:
                if self.eyes[0] > enemy.eyes[0]:
                    self.move_left(dt)
                else:
                    self.move_right(dt)
                if self.collided_x[2] != "0":
                    self.jump()
            elif distance <= self._attack_range:
                self.attack(enemy)

    def attack(self, enemy: Entity) -> None:
        if self._time_passed_since_attack >= self._attack_delay:
            enemy.take_damage(self._attack_damage)
            self._time_passed_since_attack = 0

    def update(
        self,
        map_terrain: list[list[str]],
        map_triggers: list[list[str]],
        enemies: set[Entity],
        surface: pygame.Surface,
        dt: int
    ) -> None:
        super().update(map_terrain=map_terrain, map_triggers=map_triggers,
                       surface=surface, dt=dt)
        self.interact(enemies, dt)
        self._time_passed_since_attack += dt


fighters: list[Fighter] = list()


class Player(Character):
    def __init__(
        self,
        coords: tuple,
        max_health: int,
        max_speed: float,
        acceleration: float,
        weight: float,
        jump_strength: float,
        size: tuple = None
    ) -> None:

        super().__init__(coords=coords, max_health=max_health, max_speed=max_speed,
                         acceleration=acceleration, weight=weight,
                         jump_strength=jump_strength, sprite_path="player.png",
                         size=size)
        self.__slots = [0, 0, 0, 0, 0]

        # MUST BE DELETED!
        self.__slots[1] = weapons.ShootingWeapon(
            caliber=10, bullet_speed=1.5, shot_delay=140)
        self.__selected_slot = 1

    def attack(self, mouse_pos: tuple) -> None:
        angle = atan2(mouse_pos[1] - self.eyes[1], mouse_pos[0] - self.eyes[0])
        self.__slots[self.__selected_slot].shoot(self.eyes, angle)

    def change_slot(self, slot: int) -> None:
        if self.__slots[slot] != 0:
            self.__selected_slot = slot

    def update(
        self,
        map_terrain: list[list[str]],
        map_triggers: list[list[str]],
        surface: pygame.Surface,
        dt: int
    ) -> None:
        super().update(map_terrain=map_terrain, map_triggers=map_triggers,
                       surface=surface, dt=dt)
        for tool in self.__slots:
            if tool != 0:
                tool.update(self.x, self.y, dt, surface)


# TEST ENTITIES

class TestMovable(Movable):
    def __init__(
        self,
        coords: tuple
    ) -> None:
        super().__init__(coords=coords, max_health=100, max_speed=0,
                         acceleration=0, weight=1,
                         sprite_path="characters/fighter_test.png",
                         size=(64, 64))


class TestFighter(Fighter):
    def __init__(
        self,
        coords: tuple
    ) -> None:

        super().__init__(coords=coords, max_health=100, max_speed=0.7,
                         acceleration=0.01, weight=1, jump_strength=1.5,
                         vision_range=300, attack_damage=15, attack_range=120,
                         attack_delay=1000, sprite_path="fighter_test.png",
                         size=(64, 64))

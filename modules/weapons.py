import pygame
from modules import entities
from modules.parameters.parameters import images_path


class ColdWeapon:
    def __init__(
        self,
        hit_distance: int,
        damage: int,
        hit_delay: int
    ) -> None:

        self.hit_distance = hit_distance
        self.damage = damage
        self.hit_delay = hit_delay

    def hit(self, entity) -> None:
        entity.get_damage(self.damage)


class ShootingWeapon:
    def __init__(
        self,
        caliber: float, bullet_speed: float, shot_delay: int,
        sprite_path: str = None
    ) -> None:

        self.caliber = caliber
        self.bullet_speed = bullet_speed
        self.shot_delay = shot_delay
        self.time_passed_since_shot = self.shot_delay

        if sprite_path is not None:
            self.sprite = pygame.image.load(
                images_path+"tools/"+sprite_path)
        else:
            self.sprite = pygame.Surface((30, 30))
            self.sprite.fill((255, 0, 255))

    def shoot(self, coords: tuple[int, int],
              angle: float) -> None:
        if self.time_passed_since_shot >= self.shot_delay:
            self.time_passed_since_shot = 0
            entities.bullets.append(
                entities.Bullet(coords=coords,
                                speed=self.bullet_speed,
                                weight=self.caliber*0.01,
                                angle=angle,
                                sprite_path="weapons/bullet.png",
                                size=(self.caliber, self.caliber)))

    def update(self, x, y, dt: int, surface: pygame.Surface) -> None:
        self.time_passed_since_shot += dt
        surface.blit(self.sprite, (x, y))

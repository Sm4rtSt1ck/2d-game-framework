import pygame
from modules import entities
from modules.parameters.parameters import images_path


class ColdWeapon:
    def __init__(
        self,
        hitDistance: int,
        damage: int,
        hitDelay: int
    ) -> None:

        self.hitDistance = hitDistance
        self.damage = damage
        self.hitDelay = hitDelay

    def hit(self, entity) -> None:
        entity.getDamage(self.damage)


class ShootingWeapon:
    def __init__(
        self,
        caliber: float, bulletSpeed: float, shotDelay: int,
        spritePath: str = None
    ) -> None:

        self.caliber = caliber
        self.bulletSpeed = bulletSpeed
        self.shotDelay = shotDelay
        self.timePassedSinceShot = self.shotDelay

        if spritePath is not None:
            self.sprite = pygame.image.load(
                images_path+"tools/"+spritePath)
        else:
            self.sprite = pygame.Surface((30, 30))
            self.sprite.fill((255, 0, 255))

    def shoot(self, coords: tuple[int, int],
              angle: float) -> None:
        if self.timePassedSinceShot >= self.shotDelay:
            self.timePassedSinceShot = 0
            entities.bullets.append(entities.Bullet(coords=coords,
                                    speed=self.bulletSpeed, weight=0.1,
                                    angle=angle,
                                    spritePath="weapons/bullet.png",
                                    size=(self.caliber, self.caliber)))

    def update(self, x, y, dt: int, surface: pygame.Surface) -> None:
        self.timePassedSinceShot += dt
        surface.blit(self.sprite, (x, y))

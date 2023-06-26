import arcade
import math
import random

class Bullet(arcade.Sprite):
    """Base class of a bullet. Return this sprite from another sprite's .fire() method

    Args:
        filename: The image of the bullet, str or path
        
        center_x: The bullet's x coordinate

        center_y: The bullet's y coordinate

        angle: sets the bullet's rotation and direction of travel in degrees

        damage: used in damage calculations on impact, this should be set to the firing 
                sprite's attack stat

        level: The level of the firing sprite. Used in damage calculations

        scale: the scale of the initial texture
    """

    def __init__(
        self,
        filename: str,
        center_x: float,
        center_y: float,
        angle: float,
        damage: float = 1,
        level: int = 1,
        scale: float = 1
    ):
        super().__init__(filename, scale=scale, center_x=center_x, center_y=center_y)
        self.angle = angle
        self.lifespan = 200
        self.damage = damage
        self.level = level
        self.max_velocity = 1500
        self.movement_behaviour = None
        self.moment_of_inertia = 50
        self.collision_type = 'bullet'
        self.change_x = self.max_velocity * math.cos(self.angle_radians)
        self.change_y = self.max_velocity * math.sin(self.angle_radians)
        self.mass = 1

    @property
    def angle_radians(self):
        return math.radians(self.angle)

    def update(self):
        """This is run every frame, note - don't call super().update() as Sprite logic
        is handled by the physics engine."""
        # kill the bullet if it's outlived its lifespan
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()

class RedLaser(Bullet):
    """Standard enemy laser. Fast but weak"""
    def __init__(self, center_x: float, center_y: float, angle: float, damage: float, level: int) -> None:
        super().__init__(':resources:images/space_shooter/laserRed01.png', center_x, center_y, angle, scale=0.5, damage=damage, level=level)
        self.change_x = self.max_velocity * math.cos(self.angle_radians + math.pi / 2)
        self.change_y = self.max_velocity * math.sin(self.angle_radians + math.pi / 2)
        self.mass = 0.2

class BlueLaser(Bullet):
    """Standard laser for the player. The initial weapon"""
    def __init__(self, center_x: float, center_y: float, angle: float, damage: float, level: int) -> None:
        super().__init__(
            ':resources:images/space_shooter/laserBlue01.png',
            center_x,
            center_y,
            angle,
            damage=damage,
            level=level,  
            scale=0.5
        )
        self.collision_type = 'player_bullet'
        self.mass = 0.5

class Saw(Bullet):
    """A slow moving heavy bullet, great for knocing asteroids"""
    def __init__(self, center_x: float, center_y: float, angle: float, damage: float, level: int) -> None:
        super().__init__(
            ':resources:images/enemies/saw.png',
             center_x,
             center_y,
             angle,
             damage=damage, 
             level=level, 
             scale=0.3
        )
        self.max_velocity = 500
        self.mass = 5
        self.change_x = self.max_velocity * math.cos(self.angle_radians + math.pi / 2)
        self.change_y = self.max_velocity * math.sin(self.angle_radians + math.pi / 2)
        

class Bouncy(Bullet):
    def __init__(self, center_x: float, center_y: float, angle: float, damage: float, level: int) -> None:
        filename = ""
        scale = 1
        super().__init__(filename, center_x, center_y, angle, damage, scale)
        self.collision_type = 'bouncy'
        raise NotImplementedError
        # TODO make class, get image,
        # behaviour should be to bounce of asteroids(default)
        # but also to bounce off screen edges. 
        # This should be fired at an angle to accentuate this behavior

class Orb(Bullet):
    """Dropped experience tokens

    These should be dropped by enemies when they are killed by a player action
    They should have a longer lifespan than a normal bullet, but still temporary, 
    giving the player motivation to move forward.

    Args:
        same as Bullet 

        exp: how much experience it is worth. Set by the dropping enemy. An orb drop should
        provide the same total exp regardless of the number dropped.
    """
    def __init__(self, center_x: float, center_y: float, angle: float, exp: float) -> None:
        super().__init__(':resources:images/items/star.png', center_x, center_y, angle, scale=0.2)
        self.exp = exp
        self.change_x = self.max_velocity * math.cos(self.angle_radians + math.pi / 2)
        self.change_y = self.max_velocity * math.sin(self.angle_radians + math.pi / 2)
        self.max_velocity = 100
        self.collision_type = 'orb'
        self.lifespan = 400 + random.randint(-50, 50) # stop all apearing and disapearing as one
        

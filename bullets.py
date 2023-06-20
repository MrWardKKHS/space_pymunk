import arcade
import math

class Bullet(arcade.Sprite):
    def __init__(self, filename, center_x, center_y, angle, damage=1, scale=1):
        super().__init__(filename, scale=scale, center_x=center_x, center_y=center_y)
        self.angle = angle
        self.lifespan = 200
        self.damage = damage
        self.max_velocity = 1500
        self.movement_behaviour = None
        self.moment_of_inertia = 50
        self.collision_type = 'bullet'
        self.change_x = self.max_velocity * math.cos(self.angle_radians)
        self.change_y = self.max_velocity * math.sin(self.angle_radians)
        self.mass = 1

    def on_collide(self):
        pass

    @property
    def angle_radians(self):
        return math.radians(self.angle)

    def update(self):
        # kill the bullet if it's outlived its lifespan
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()

class RedLaser(Bullet):
    """Standard enemy laser. Fast but weak"""
    def __init__(self, center_x, center_y, angle):
        super().__init__(':resources:images/space_shooter/laserRed01.png', center_x, center_y, angle, scale=0.5)
        self.change_x = self.max_velocity * math.cos(self.angle_radians + math.pi / 2)
        self.change_y = self.max_velocity * math.sin(self.angle_radians + math.pi / 2)
        self.mass = 0.2

class BlueLaser(Bullet):
    """Standard laser for the player. The initial weapon"""
    def __init__(self, center_x, center_y, angle):
        super().__init__(':resources:images/space_shooter/laserBlue01.png', center_x, center_y, angle, scale=0.5)
        self.collision_type = 'player_bullet'
        self.mass = 0.5

class Saw(Bullet):
    """A slow moving heavy bullet, great for knocing asteroids"""
    def __init__(self, center_x, center_y, angle):
        super().__init__(':resources:images/enemies/saw.png', center_x, center_y, angle, scale=0.3)
        self.max_velocity = 500
        self.mass = 5
        self.change_x = self.max_velocity * math.cos(self.angle_radians + math.pi / 2)
        self.change_y = self.max_velocity * math.sin(self.angle_radians + math.pi / 2)
        

class Bouncy(Bullet):
    def __init__(self, center_x, center_y, angle, damage=1, scale=1):
        super().__init__(filename, center_x, center_y, angle, damage, scale)
        self.collision_type = 'bouncy'
        raise NotImplementedError
        # TODO make class, get image,
        # behaviour should be to bounce of asteroids(default)
        # but also to bounce off screen edges. 
        # This should be fired at an angle to accentuate this behavior

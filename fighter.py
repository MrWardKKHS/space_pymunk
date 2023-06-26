import arcade
import random
from pyglet.math import Vec2
from typing import List
import math
from bullets import RedLaser, Saw, Orb
from pymunk import Body
from utils import get_physics_body
from state_machines import FighterStateMachine, StateMachine

class Enemy(arcade.Sprite):
    """Base sprite for enemies"""
    def __init__(self, filename: str = "", scale: float = 1, x: float = 0, y: float = 0, level: int = 1):
        super().__init__(filename, scale)
        self.center_x = x
        self.center_y = y
        self.level = level
        self.max_speed = 500
        self.max_force = 50
        self.forces: List[Vec2] = []
        self.health = math.floor((random.randint(40, 65) * 2 * level) / 30) + level + 10
        self.max_health = self.health
        self.attack = math.floor((random.randint(20, 35) * 2 * level) / 30) + 5
        self.defence = math.floor((random.randint(20, 35) * 2 * level) / 30) + 5
        self.base_experience = 20
        self.weapon_type = Saw
        # physics engine not available during init
        self.state_machine = StateMachine(self)

    @property
    def physics_body(self) -> Body:
        return get_physics_body(self.physics_engines[0], self)

    @property
    def experience(self):
        return (self.base_experience * self.level) // 7

    @property
    def angle_radians(self):
        return math.radians(self.angle)

    def drop_experience(self) -> List[Orb]:
        drops = random.randint(5, 10)
        exp = self.experience / drops
        orbs = []
        for i in range(drops):
            angle = 360 * random.random()
            orb = Orb(self.center_x, self.center_y, angle, exp)
            orbs.append(orb)
        return orbs

    def take_damage(self, damage, player_level):
        res = (((2 * player_level+2)*(damage/self.defence))/100) * random.randint(75, 100)
        self.health -= res
            
    def pymunk_moved(self, physics_engine: arcade.PymunkPhysicsEngine, dx, dy, d_angle) -> None:
        self.physics_body.angular_velocity *= 0.7
        net = Vec2()
        for force in self.forces:
            net += force

        net.limit(self.max_force)
        self.physics_body.apply_force_at_world_point((net.x, net.y), (self.center_x, self.center_y))
        vel = Vec2(self.physics_body.velocity.x, self.physics_body.velocity.y)
        self.forces.clear()
        # self.physics_body.angle = vel.heading - math.pi/2

    def update(self) -> None:
        self.state_machine.update()

class Fighter(Enemy):
    """
    An enemy in the game
    This class contains several default steering behaviours
    and logic to handle firing 
    """
    def __init__(self, x: int, y: int, level: int) -> None:
        super().__init__(
            ':resources:images/space_shooter/playerShip1_orange.png',
             scale=1,
             x=x,
             y=y,
             level=level
        )
        self.base_experience = 40

    def fire(self) -> List[arcade.Sprite]:
        bullets = []
        #x = self.center_x + 80 * math.cos(math.radians(self.angle))
        #y = self.center_y + 80 * math.sin(math.radians(self.angle))
        bullet = self.weapon_type(self.center_x, self.center_y, -self.angle, self.attack, self.level)
        bullets.append(bullet)
        return bullets

    def rotate_right(self) -> None:
        self.physics_body.angular_velocity += 3

    def rotate_left(self) -> None:
        self.physics_body.angular_velocity -= 3


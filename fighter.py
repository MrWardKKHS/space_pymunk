import arcade
from pyglet.math import Vec2
from typing import List
import math
from bullets import RedLaser, Saw
from pymunk import Body
from utils import get_physics_body
from state_machines import FighterStateMachine

class Sprite(arcade.Sprite):
    def __init__(self, filename: str = "", scale: float = 1, x: int = 0, y: int = 0, health: int = 20):
        super().__init__(filename, scale)
        self.center_x = x
        self.center_y = y
        self.max_speed = 500
        self.max_force = 50
        self.forces: List[Vec2] = []
        self.weapon_cooldown = 0
        self.health = health
        self.max_health = health
        self.weapon_type = Saw

    @property
    def physics_body(self) -> Body:
        return get_physics_body(self.physics_engines[0], self)


class Fighter(Sprite):
    """
    An enemy in the game
    This class contains several default steering behaviours
    and logic to handle firing 
    """
    def __init__(self, x: int, y: int, physics_engine: arcade.PymunkPhysicsEngine, health: int = 20 ):
        super().__init__(':resources:images/space_shooter/playerShip1_orange.png', scale=1, x=x, y=y, health=health)
        # physics engine not available during init
        self.state_machine = FighterStateMachine(self, physics_engine=physics_engine)

    def fire(self) -> List[arcade.Sprite]:
        bullets = []
        bullet = self.weapon_type(self.center_x, self.center_y, self.angle)
        bullets.append(bullet)
        self.weapon_cooldown = 0
        return bullets

    def pointing_at_target(self, target):
        """Calculate if the enemy is pointing at the target so it should fire if it can"""
        angle = math.radians(self.angle - 90)
        pos = Vec2(*self.physics_body.position) # The * is a little unpacking trick here
        target_pos = Vec2(target)
        vec_to_target = pos - target_pos
        angle_to_target = vec_to_target.heading
        # check if difference in angle is within some margin
        if abs(angle - angle_to_target) < math.pi/16:
            return True
        return False

    def pymunk_moved(self, physics_engine: arcade.PymunkPhysicsEngine, dx, dy, d_angle) -> None:
        self.physics_body.angular_velocity *= 0.7
        net = Vec2()
        for force in self.forces:
            net += force

        net.limit(self.max_force)
        self.physics_body.apply_force_at_world_point((net.x, net.y), (self.center_x, self.center_y))
        vel = Vec2(self.physics_body.velocity.x, self.physics_body.velocity.y)
        self.physics_body.angle = vel.heading - math.pi/2
        
    def rotate_right(self) -> None:
        self.physics_body.angular_velocity += 3

    def rotate_left(self) -> None:
        self.physics_body.angular_velocity -= 3

    def update(self):
        self.weapon_cooldown += 1
        self.state_machine.update()


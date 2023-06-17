import arcade
from pyglet.math import Vec2
from typing import List
import math
from bullets import RedLaser, Saw
from pymunk import Body
from utils import get_physics_body

class Fighter(arcade.Sprite):
    """
    An enemy in the game
    This class contains several default steering behaviours
    and logic to handle firing 
    """
    def __init__(self, x: int, y: int, health: int = 20):
        super().__init__(':resources:images/space_shooter/playerShip1_orange.png', 1)
        self.center_x = x
        self.center_y = y
        self.physics_body: Body = None
        self.max_speed = 500
        self.max_force = 50
        self.forces: List[Vec2] = []
        self.weapon_cooldown = 0
        self.health = health
        self.max_health = health
        self.weapon_type = RedLaser
        self.target = (0, 0)

    def seek(self, target: Vec2, arrive: bool = True) -> None:
        """
        A steering behaviour where the vehicle attempts to 
        move towards the target at the fastest possible rate
        """
        # get desired velocity
        pos = Vec2(self.center_x, self.center_y)
        force = target - pos

        # get current velocity
        vel = Vec2(self.physics_body.velocity.x, self.physics_body.velocity.y)

        slow_radius = 400
        if arrive and force.mag < slow_radius:
            desired_speed = -self.max_speed
        else:
            desired_speed = self.max_speed

        # scale it to the maximum speed
        force = force.from_magnitude(desired_speed)

        # take the difference between desired velocity and current velocity 
        # to get a change in velocity 
        force -= vel
        force.limit(self.max_force)

        # add the force to forces to add later
        self.forces.append(force)
        

    def flee(self, target: Vec2, _range: int = 200) -> None:
        """A steering behaviour where the vehicle attempts to 
            move away from the target at the fastest possible rate
        """
        if Vec2(self.center_x, self.center_y).distance(target) > _range:
            return 
            # get desired velocity
        pos = Vec2(self.center_x, self.center_y)
        force = target - pos
        force = -force

        # get current velocity
        vel = Vec2(self.physics_body.velocity.x, self.physics_body.velocity.y)
        desired_speed = self.max_speed

        # scale it to the maximum speed
        force = force.from_magnitude(desired_speed)

        # take the difference between desired velocity and current velocity 
        # to get a change in velocity 
        force -= vel

        force.limit(self.max_force)

        # add the force to forces to add later
        self.forces.append(force)


    def fire(self) -> List[arcade.Sprite]:
        bullets = []
        bullet = self.weapon_type(self.center_x, self.center_y, self.angle)
        bullets.append(bullet)
        self.weapon_cooldown = 0
        return bullets

    def pointing_at_target(self):
        """Calculate if the enemy is pointing at the target so it should fire if it can"""
        angle = math.radians(self.angle - 90)
        pos = Vec2(*self.physics_body.position) # The * is a little unpacking trick here
        target_pos = Vec2(*self.target)
        vec_to_target = pos - target_pos
        angle_to_target = vec_to_target.heading
        # check if difference in angle is within some margin
        if abs(angle - angle_to_target) < math.pi/16:
            return True
        return False

    def pymunk_moved(self, physics_engine:arcade.PymunkPhysicsEngine, dx, dy, d_angle) -> None:
        self.physics_body = get_physics_body(physics_engine, self)
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


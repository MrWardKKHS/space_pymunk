import random
import arcade
from pymunk import Body
from bullets import BlueLaser
from constants import * 
from utils import get_physics_body
from typing import List

class Player(arcade.Sprite):
    def __init__(self, player_num:int, colour:str, x: int, y: int):
        super().__init__(f":resources:images/space_shooter/playerShip1_{colour}.png", CHARACTER_SCAILING)

        # the physics body is not accessable when the sprite is first created as 
        # it needs to be registered with the physics engine after this step
        # It is set when the sprite is first moved by the physics engine
        self.physics_body: Body = None # pyright: ignore
        self.center_x = x
        self.center_y = y
        self.experience = 0
        self.next_level_at = 100
        self.level = 1
        self.attack = random.randint(10, 15)
        self.defence = random.randint(10, 35)
        self.health = random.randint(15, 55)

        try:# This is a holder for implementing multiple players in the future
            self.joystick = arcade.get_joysticks()[player_num]
            self.joystick.open()
            self.joystick.push_handlers(self)
        except IndexError:
            self.joystick = None

        self.weapon_type = BlueLaser

    def pymunk_moved(self, physics_engine:arcade.PymunkPhysicsEngine, dx, dy, d_angle):
        """
        This function automatically runs when the physics engine moves the sprite
        The arguments need to be as they are here and dx represents delta_x i.e the change in x
        """
        self.physics_body = get_physics_body(physics_engine, self)
        self.physics_body.angular_velocity *= 0.95
        if self.physics_body.position.y < -self.height:
            self.physics_body.position = (self.physics_body.position.x, HEIGHT + self.height)
        if self.physics_body.position.y > HEIGHT + self.height:
            self.physics_body.position = (self.physics_body.position.x, -self.height)

    def rotate_right(self):
        self.physics_body.angular_velocity += 0.6

    def rotate_left(self):
        self.physics_body.angular_velocity -= 0.6

    def fire(self) -> List[arcade.Sprite]:
        """Makes a bullet and returns it to be added to a spritelist elsewhere"""
        bullet = self.weapon_type(center_x=self.center_x, center_y=self.center_y, angle=-self.angle + 90, damage=self.attack, level=self.level)
        return [bullet]

    def gain_exp(self, exp):
        self.experience += exp
        if self.experience >= self.next_level_at:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience = self.experience - self.next_level_at
        self.next_level_at = (self.level + 1) ** 3
        self.attack += random.randint(0, 3)
        self.defence += random.randint(0, 3)
        self.health += random.randint(0, 5)
        self.stat_points = random.randint(3, 7)
        print(self.level, self.attack)
        if self.experience >= self.next_level_at:
            self.level_up()


    def take_damage(self, damage):
        """Loosely based on the Pokemon damage calculation"""
        res = (((2 * self.level+2)*(damage/self.defence))/100) * random.randint(75, 100)
        self.health -= res


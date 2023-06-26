from __future__ import annotations
import arcade
from typing import TYPE_CHECKING
import math
from pyglet.math import Vec2


if TYPE_CHECKING:
    from state_machines import StateMachine, FighterStateMachine


class BaseActivity:
    """Represents something to be done while in a given state,
    This can be one of many activities

    Args:
        state_machine: The state_machine of the sprite that is doing the activity
    """
    def execute(self, state_machine: StateMachine) -> None: # pyright: ignore
        """Do the activity"""
        pass

    def enter(self, state_machine: StateMachine) -> None: # pyright: ignore
        """Enter the activity
        Include any logic that is required when the activity is first run

        This it usedul as the class may be init-ed well before the activity is entered
        """
        pass

    def exit(self, state_machine: StateMachine) -> None: # pyright: ignore
        """Add any cleanup code here"""
        pass


class Seek(BaseActivity):
    def __init__(self, target: arcade.Sprite, arrive: bool = True, slow_radius: int = 400) -> None:
        """
        A steering behaviour where the vehicle attempts to 
        move towards the target at the fastest possible rate

        Args:
            target: a sprite to seek, we will continue seeting the 
                target even as its center_x and center_y change
            
            arrive: A bool saying if we would like the sprite to slow down
                as we get close to the target. This helps limit overshooting.

            slow_radius: The distance to start slowing down if arrive is set to true 
        """
        self.target = target
        self.arrive = arrive
        self.slow_radius = slow_radius
        # get desired velocity

    def execute(self, state_machine: StateMachine) -> None:
        """steer towards the target"""
        pos = Vec2(state_machine.sprite.center_x, state_machine.sprite.center_y)
        force = Vec2(self.target.center_x, self.target.center_y) - pos

        # get current velocity
        vel = Vec2(state_machine.sprite.physics_body.velocity.x, state_machine.sprite.physics_body.velocity.y)

        # if the arrive setting is true and we are inside the radius, 
        # Slow down proportionally to how close we are to the targer
        if self.arrive and force.mag < self.slow_radius:
            desired_speed = state_machine.sprite.max_speed * (self.slow_radius / force.mag)
        else:
            desired_speed = state_machine.sprite.max_speed

        # scale it to the maximum speed
        force = force.from_magnitude(desired_speed)

        # take the difference between desired velocity and current velocity 
        # to get a change in velocity 
        force -= vel
        force.limit(state_machine.sprite.max_force)

        # add the force to forces to add later
        state_machine.sprite.forces.append(force)

class Flee(BaseActivity):
    def __init__(self, target: arcade.Sprite, _range: int = 200) -> None:
        """A steering behaviour where the vehicle attempts to 
            move away from the target at the fastest possible rate
        Args:
            target: a sprite to seek, we will continue seeting the 
                target even as its center_x and center_y change
            
            _range: How close should we be to the target before we activate this behaviour 
                nb. _range to avoid overwritin the inbuilt range function.
        """
        self.target = target
        self._range = _range

    def execute(self, state_machine: StateMachine) -> None:
        if math.dist((state_machine.sprite.center_x, state_machine.sprite.center_y), (self.target.center_x, self.target.center_y)) > self._range:
            return 
            # get desired velocity
        pos = Vec2(state_machine.sprite.center_x, state_machine.sprite.center_y)
        force = Vec2(self.target.center_x, self.target.center_y) - pos
        force = -force

        # get current velocity
        vel = Vec2(state_machine.sprite.physics_body.velocity.x, state_machine.sprite.physics_body.velocity.y)
        desired_speed = state_machine.sprite.max_speed

        # scale it to the maximum speed
        force = force.from_magnitude(desired_speed)

        # take the difference between desired velocity and current velocity 
        # to get a change in velocity 
        force -= vel

        force.limit(state_machine.sprite.max_force)

        # add the force to forces to add later
        state_machine.sprite.forces.append(force)

class PointTowardsTargetActivity(BaseActivity):
    def __init__(self, target: arcade.Sprite) -> None:
        """
        A simple activity that sets the angle of the sprite to 
        point towards the target

        Args:
            target: a sprite to steer towards
        """
        self.target = target

    def execute(self, state_machine: StateMachine) -> None:
        dx =  state_machine.sprite.center_x - self.target.center_x
        dy = state_machine.sprite.center_y - self.target.center_y 

        angle = math.atan2(dy, dx)
        state_machine.sprite.physics_body.angle = angle + math.pi/2

class PointInDirectionOfTravelActivity(BaseActivity):
    def execute(self, state_machine: StateMachine) -> None:
        physics_body = state_machine.sprite.physics_body
        vel = Vec2(physics_body.velocity.x, physics_body.velocity.y)
        physics_body.angle = vel.heading - math.pi/2

class FireActivity(BaseActivity):
    """An activity that runs the sprites fire() method and adds any 
    sprites returned into the state_machine

    This activity should be pulled off the activity list immediately
    after executing to avoid being executed every frame, then 
    add a new instance of this activity to the state's activity list after some
    perid of time or other trigger"""

    def execute(self, state_machine: FighterStateMachine) -> None:
        bullets = state_machine.sprite.fire()
        for bullet in bullets:
            state_machine.bullet_list.append(bullet)
            state_machine.physics_engine.add_sprite(bullet, collision_type=bullet.collision_type, max_velocity=bullet.max_velocity, moment_of_inertia=bullet.moment_of_inertia, mass=bullet.mass, damping=0.99)
            state_machine.physics_engine.set_velocity(bullet, (bullet.change_x, bullet.change_y))

class HealActivity(BaseActivity):
    """Increase the sprite's health by one twelveth. 

    Similar to FireActivity this activity should immediately be removed after executing"""
    def execute(self, state_machine: StateMachine) -> None:
        state_machine.sprite.health += max(state_machine.sprite.max_health // 12, 1)

class AvoidObstaclesActivity(BaseActivity):
    """An activity that gives a sprite three detectors and sets a sprite to flee from
    any sprite in the obstacle list that is detected by any detector.

    The detectors move further out in relation to the sprites speed, to ensure that the
    sprite can still fit through gaps that are the same size as the sprite

    TODO: use the dot-produt of the two sprites to get a tangent vector to the detected sprite, 
    rather than a vector that points directly away from it.

    This class curretly accounts for the 90degree offset in the fighter sprite, correct before 
    using with correctly rotated sprites
    """
    def __init__(self, obstacles: arcade.SpriteList) -> None:
        super().__init__()
        self.front_detector = arcade.SpriteCircle(20, (0, 0, 255))
        self.left_detector = arcade.SpriteCircle(20, (255, 0, 0))
        self.right_detector = arcade.SpriteCircle(20, (0, 255, 0))
        self.obstacles = obstacles

    def execute(self, state_machine: StateMachine) -> None:
        # Move detectors relative to the sprite 
        vel = Vec2(state_machine.sprite.physics_body.velocity[0], state_machine.sprite.physics_body.velocity[1]).mag
        speed_scale = (vel / state_machine.sprite.max_speed)
        d = 120 * speed_scale + 20
        x = state_machine.sprite.center_x + d  * math.cos(state_machine.sprite.angle_radians - math.pi/2) 
        y = state_machine.sprite.center_y + d  * math.sin(state_machine.sprite.angle_radians - math.pi/2) 
        self.front_detector.position = (x, y)

        x = state_machine.sprite.center_x +  d * math.cos(state_machine.sprite.angle_radians)
        y = state_machine.sprite.center_y +  d * math.sin(state_machine.sprite.angle_radians) 
        self.left_detector.position = (x, y)

        x = state_machine.sprite.center_x + d * math.cos(state_machine.sprite.angle_radians + math.pi) 
        y = state_machine.sprite.center_y + d * math.sin(state_machine.sprite.angle_radians + math.pi) 
        self.right_detector.position = (x, y)

        left_high = arcade.check_for_collision_with_list(self.left_detector, self.obstacles) 
        right_high = arcade.check_for_collision_with_list(self.left_detector, self.obstacles) 
        front_high = arcade.check_for_collision_with_list(self.front_detector, self.obstacles) 
        
        # create a flat list of all obstacles that are detected, regardless of detector
        obstacles = []
        obstacles.extend(left_high)
        obstacles.extend(right_high)
        obstacles.extend(front_high)

        for obstacle in obstacles:
            pos = Vec2(state_machine.sprite.center_x, state_machine.sprite.center_y)
            force = Vec2(obstacle.center_x, obstacle.center_y) - pos
            force = -force

            # get current velocity
            vel = Vec2(state_machine.sprite.physics_body.velocity.x, state_machine.sprite.physics_body.velocity.y)
            desired_speed = 400 

            # scale it to the maximum speed
            force = force.from_magnitude(desired_speed)

            # take the difference between desired velocity and current velocity 
            # to get a change in velocity 
            force -= vel

            force.limit(state_machine.sprite.max_force)

            # add the force to forces to add later
            state_machine.sprite.forces.append(force)


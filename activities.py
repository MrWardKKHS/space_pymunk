from __future__ import annotations
from typing import TYPE_CHECKING
import math
from pyglet.math import Vec2

if TYPE_CHECKING:
    from state_machines import StateMachine


class BaseActivity:
    """Represents something to be done while in a given state,
    This can be one of many activities"""
    def execute(self, state_machine: StateMachine):
        """Do the activity"""
        pass

    def enter(self, state_machine: StateMachine):
        """Enter the activity
        Include any logic that is required when the activity is first run"""
        pass

    def exit(self, state_machine: StateMachine):
        """Add any cleanup code here"""
        pass


class Seek(BaseActivity):
    def __init__(self, target, arrive: bool = True) -> None:
        """
        A steering behaviour where the vehicle attempts to 
        move towards the target at the fastest possible rate

        Args:
            target: a sprite to seek, we will continue seeting the 
                target even as its center_x and center_y change
            
            arrive: A bool saying if we would like the sprite to slow down
                as we get close to the target. This helps limit overshooting.
        """
        self.target = target
        self.arrive = arrive
        # get desired velocity

    def execute(self, state_machine: StateMachine):
        """steer towards the target"""
        pos = Vec2(state_machine.sprite.center_x, state_machine.sprite.center_y)
        force = Vec2(self.target.center_x, self.target.center_y) - pos

        # get current velocity
        vel = Vec2(state_machine.sprite.physics_body.velocity.x, state_machine.sprite.physics_body.velocity.y)

        slow_radius = 400
        if self.arrive and force.mag < slow_radius:
            desired_speed = -state_machine.sprite.max_speed
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
    def __init__(self, target, _range: int = 200) -> None:
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

    def execute(self, state_machine: StateMachine):
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
    pass

class FireActivity(BaseActivity):
    pass

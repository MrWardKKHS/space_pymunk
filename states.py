from pyglet.math import Vec2
import arcade
import math
from typing import List, Tuple

# based on tutorial found here
# https://pavcreations.com/finite-state-machine-for-ai-enemy-controller-in-2d/2/#BaseState-class

class Decision:
    def decide(self, state_machine):
        pass

class BaseState:
    def execute(self, state_machine):
        pass

    def enter(self, state_machine):
        pass

    def exit(self, state_machine):
        pass

class RemainInState(BaseState):
    pass

class Activity(BaseState):
    pass

class Transition(BaseState):
    def __init__(self, decision, true_state, false_state) -> None:
        self.decision = decision
        self.true_state = true_state
        self.false_state = false_state

    def execute(self, state_machine):
        if self.decision.decide(state_machine) and not type(self.true_state) == RemainInState:
            state_machine.state.exit(state_machine)
            state_machine.state = self.true_state
            state_machine.state.enter(state_machine)

        elif not type(self.false_state) == RemainInState:
            state_machine.state.exit(state_machine)
            state_machine.state = self.false_state
            state_machine.state.enter(state_machine)

class State(BaseState):
    def __init__(self):
        self.activities: List[Activity] = []
        self.transitions: List[Transition] = []

    def execute(self, state_machine):
        for activity in self.activities:
            activity.execute(state_machine)

        for transition in self.transitions:
            transition.execute(state_machine)

    def enter(self, state_machine):
        for activity in self.activities:
            activity.enter(state_machine)
        for transition in self.transitions:
            transition.enter(state_machine)

    def exit(self, state_machine):
        for activity in self.activities:
            activity.exit(state_machine)
        for transition in self.transitions:
            transition.exit(state_machine)


class IdleState(BaseState):
    def enter(self, state_machine):
        state_machine.sprite.physics_body.velocity = (0, 0)

    def update(self):
        ...

class Seek(Activity):
    def __init__(self, target, arrive: bool = True) -> None:
        """
        A steering behaviour where the vehicle attempts to 
        move towards the target at the fastest possible rate
        """
        self.target = target
        self.arrive = arrive
        # get desired velocity

    def execute(self, state_machine):
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

class Flee(Activity):
    def __init__(self, target, _range: int = 200) -> None:
        """A steering behaviour where the vehicle attempts to 
            move away from the target at the fastest possible rate
        """
        self.target = target
        self._range = _range

    def execute(self, state_machine):
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


class LowHealthDecision(Decision):
    def __init__(self, health) -> None:
        self.health = health

    def decide(self, state_machine):
        return state_machine.sprite.health < self.health

class ArrivedAtPointDecision(Decision):
    def __init__(self, point: arcade.Sprite, margin: int)-> None:
        self.target = point
        self.margin = margin

    def decide(self, state_machine):
        return math.dist(state_machine.sprite.position, self.target.position) < self.margin

class SeekAndFleeState(State):
    def enter(self, state_machine):
        for target in state_machine.sprite.targets:
            self.activities.append(Seek(target))

        for flee_target in state_machine.sprite.flee_targets:
            self.activities.append(Flee(flee_target))

        self.transitions.append(
            Transition(
                LowHealthDecision(10), 
                NavigateToPointState((state_machine.sprite.center_x + 1000, state_machine.sprite.center_y)), 
                RemainInState()
            )
        )

    def __str__(self) -> str:
        return "Seeking Player"

class NavigateToPointState(State):
    def __init__(self, target: Tuple[int, int], speed=1):
        super().__init__()
        self.speed = speed
        self.target = arcade.Sprite(center_x=target[0], center_y=target[1])
    
    def enter(self, state_machine):
        self.activities.append(
            Seek(target=self.target)
        )
        self.transitions.append(
            Transition(
                ArrivedAtPointDecision(self.target, 20),
                SeekAndFleeState(),
                RemainInState()
            )
        )

    def __str__(self) -> str:
        return "Navigating to point"
                    



class PatrolState(State):
    def __init__(self, patrol_points: List[Tuple[int, int]], speed=1):
        super().__init__()
        self.patrol_points = patrol_points
        self.speed = speed
        self.activities.append(PatrolToPointActivity())

class ReturnToBaseState(State):
    pass

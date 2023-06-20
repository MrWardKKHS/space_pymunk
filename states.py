from __future__ import annotations
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from state_machines import FighterStateMachine, StateMachine 

import arcade
from typing import List, Tuple
from transitions import Transition
from activities import BaseActivity, Seek, Flee
from decisions import LowHealthDecision, ArrivedAtPointDecision, OutOfRange, WithinRangeDecision

# based on tutorial found here
# https://pavcreations.com/finite-state-machine-for-ai-enemy-controller-in-2d/2/#BaseState-class

class BaseState:
    def execute(self, state_machine: StateMachine):
        pass

    def enter(self, state_machine: StateMachine):
        pass

    def exit(self, state_machine: StateMachine):
        pass

class State(BaseState):
    def __init__(self):
        self.activities: List[BaseActivity] = []
        self.transitions: List[Transition] = []

    def execute(self, state_machine: StateMachine):
        for activity in self.activities:
            activity.execute(state_machine)

        for transition in self.transitions:
            transition.execute(state_machine)

    def enter(self, state_machine: StateMachine):
        for activity in self.activities:
            activity.enter(state_machine)
        for transition in self.transitions:
            transition.enter(state_machine)

    def exit(self, state_machine: StateMachine):
        for activity in self.activities:
            activity.exit(state_machine)
        for transition in self.transitions:
            transition.exit(state_machine)


class IdleState(BaseState):
    def enter(self, state_machine: StateMachine):
        state_machine.sprite.physics_body.velocity = (0, 0)

    def execute(self, state_machine: StateMachine):
        pass

class SeekAndFleeState(State):
    def enter(self, state_machine: FighterStateMachine):
        for target in state_machine.targets:
            self.activities.append(Seek(target))

        for flee_target in state_machine.flee_targets:
            self.activities.append(Flee(flee_target))

        self.transitions.append(
            Transition(
                LowHealthDecision(10), 
                NavigateToPointState((state_machine.sprite.center_x + 1000, state_machine.sprite.center_y)), 
                None
            )
        )

    def __str__(self) -> str:
        return "Seeking Player"

class NavigateToPointState(State):
    def __init__(self, target: Tuple[int, int], speed=1):
        super().__init__()
        self.speed = speed
        self.target = arcade.Sprite(center_x=target[0], center_y=target[1])
    
    def enter(self, state_machine: StateMachine):
        self.activities.append(
            Seek(target=self.target)
        )
        self.transitions.append(
            Transition(
                ArrivedAtPointDecision(self.target, 20),
                SeekAndFleeState(),
                None 
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


class FleeFromPlayer(State):
    pass


class PointAndShoot(State):
    def __init__(self, target):
        """Constantly point towards the target and fire when possible"""
        super().__init__()
        self.target = target

    def enter(self, state_machine):
        state_machine.sprite.body.velocity = (0, 0) 
        self.activities.append(PointTowardsTargetActivity())
        self.activities.append(FireActivity())
        
        self.transitions.append(
            Transition(
                WithinRangeDecision(self.target, 200),
                SeekAndFleeState(),
                None,
            )
        )
        self.transitions.append(
            Transition(
                OutOfRange(self.target, 400),
                SeekAndFleeState(),
                None,
            )
        )

    def __repr__(self) -> str:
        return "Firing!"

           



class Heal(State):
    pass



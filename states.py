from __future__ import annotations
from os import stat
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from state_machines import FighterStateMachine, StateMachine 

import arcade
from typing import List, Tuple
from transitions import Transition
from activities import AvoidObstaclesActivity, BaseActivity, PointInDirectionOfTravelActivity, Seek, Flee, PointTowardsTargetActivity, FireActivity, HealActivity
from decisions import LowHealthDecision, OutOfRange, TakenDamageDecision, TimeElapsedDecision, WithinRangeDecision, FullHealthDecision

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
        self.activities.append(Seek(state_machine.target))
        self.activities.append(PointInDirectionOfTravelActivity())
        self.activities.append(AvoidObstaclesActivity(state_machine.rocks))

        for flee_target in state_machine.flee_targets:
            self.activities.append(Flee(flee_target))

        self.transitions.append(
            Transition(
                LowHealthDecision(10), 
                FleeFromPlayer((state_machine.sprite.center_x + 3000, state_machine.sprite.center_y)), 
                None
            )
        )
        self.transitions.append(
            Transition(
                WithinRangeDecision(state_machine.target, outer_limit=800), 
                PointAndShoot(), 
                None
            )
        )

    def __str__(self) -> str:
        return "Seeking Player"

class NavigateToPointState(State):
    def __init__(self, target: Tuple[float, float]):
        super().__init__()
        self.target = arcade.Sprite(center_x=target[0], center_y=target[1])
    
    def enter(self, state_machine: StateMachine):
        self.activities.append(
            Seek(target=self.target)
        )
        self.activities.append(PointInDirectionOfTravelActivity())
        self.activities.append(AvoidObstaclesActivity(state_machine.rocks))

        self.transitions.append(
            Transition(
                WithinRangeDecision(self.target, 400),
                SeekAndFleeState(),
                None 
            )
        )

    def __str__(self) -> str:
        return "Run away!!"
                    
class PatrolState(State):
    def __init__(self, patrol_points: List[Tuple[int, int]], speed=1):
        super().__init__()
        self.patrol_points = patrol_points
        self.speed = speed
        # self.activities.append(PatrolToPointActivity())


class FleeFromPlayer(State):
    def __init__(self, target: Tuple[float, float]):
        super().__init__()
        self.target = arcade.Sprite(center_x=target[0], center_y=target[1])
    
    def enter(self, state_machine: StateMachine):
        self.activities.append(
            Seek(target=self.target)
        )
        self.activities.append(PointInDirectionOfTravelActivity())
        self.activities.append(AvoidObstaclesActivity(state_machine.rocks))

        self.transitions.append(
            Transition(
                WithinRangeDecision(self.target, 400),
                Heal(),
                None 
            )
        )

    def __str__(self) -> str:
        return "Fleeing!!"


class PointAndShoot(State):
    """Constantly point towards the target and fire when possible"""
    def enter(self, state_machine: FighterStateMachine):
        self.activities.append(FireActivity())
        self.activities.append(PointTowardsTargetActivity(state_machine.target))
        
#        self.transitions.append(
#            Transition(
#                WithinRangeDecision(state_machine.target, outer_limit=1000, inner_limit=700), 
#                None,
#                SeekAndFleeState(),
#            )
#        )
        self.transitions.append(
            Transition(
                TimeElapsedDecision(1.8),
                PointAndShoot(),
                None
            )
        )
        self.transitions.append(
            Transition(
                LowHealthDecision(10), 
                FleeFromPlayer((state_machine.sprite.center_x + 2000, state_machine.sprite.center_y)), 
                None
            )
        )
        self.transitions.append(
            Transition(
                TakenDamageDecision(state_machine.sprite.health), 
                NavigateToPointState((state_machine.sprite.center_x + 1000, state_machine.sprite.center_y)), 
                None
            )
        )

    def execute(self, state_machine: StateMachine):
        super().execute(state_machine)
        for activity in self.activities:
            if type(activity) == FireActivity:
                self.activities.remove(activity)
        state_machine.sprite.physics_body.velocity *= 0.99

    def __str__(self) -> str:
        return "Firing!"


class Heal(State):
    def enter(self, state_machine: FighterStateMachine):
        self.activities.append(HealActivity())
#        self.transitions.append(
#            Transition(
#                WithinRangeDecision(state_machine.target, outer_limit=1000, inner_limit=700), 
#                None,
#                SeekAndFleeState(),
#            )
#        )
        self.transitions.append(
            Transition(
                TimeElapsedDecision(1.2),
                Heal(), 
                None
            )
        )
        self.transitions.append(
            Transition(
                TakenDamageDecision(state_machine.sprite.health), 
                NavigateToPointState((state_machine.sprite.center_x + 1000, state_machine.sprite.center_y)), 
                None
            )
        )
        self.transitions.append(
            Transition(
                FullHealthDecision(), 
                SeekAndFleeState(), 
                None
            )
        )

    def execute(self, state_machine: StateMachine):
        super().execute(state_machine)
        for activity in self.activities:
            if type(activity) == HealActivity:
                self.activities.remove(activity)
        state_machine.sprite.physics_body.velocity *= 0.99

    def __str__(self) -> str:
        return "healing"

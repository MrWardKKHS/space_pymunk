from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from state_machines import StateMachine 
import arcade
import math


class Decision:
    """A class to hold a conditional. This represents an 'if' statement 
    that can be swapped out in a transition"""
    def decide(self, state_machine: StateMachine) -> bool:
        """Evaluate the decision"""
        return False


class LowHealthDecision(Decision):
    """Trigger when health drops below a threshold"""
    def __init__(self, health) -> None:
        self.lower_health_threshold = health

    def decide(self, state_machine: StateMachine) -> bool:
        return state_machine.sprite.health < self.lower_health_threshold 
    

class FullHealthDecision(Decision):
    """Trigger when an enemies health reacher their max_health"""
    def decide(self, state_machine: StateMachine) -> bool:
        return state_machine.sprite.health >= state_machine.sprite.max_health


class WithinRangeDecision(Decision):
    """Triggers when sprite is within some range of the target"""
    def __init__(self, point: arcade.Sprite, _range: int)-> None:
        self.target = point
        self.range = _range

    def decide(self, state_machine: StateMachine):
        return math.dist(state_machine.sprite.position, self.target.position) < self.range


class OutOfRange(Decision):
    """Triggers when an enemy gets outsige a given range"""
    def __init__(self, point: arcade.Sprite, _range: int)-> None:
        self.target = point
        self.range = _range

    def decide(self, state_machine: StateMachine):
        return math.dist(state_machine.sprite.position, self.target.position) > self.range


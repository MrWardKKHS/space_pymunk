from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from state_machines import StateMachine 
import arcade
import math
from time import time

class Decision:
    """A class to hold a conditional. This represents an 'if' statement 
    that can be swapped out in a transition"""
    def decide(self, state_machine: StateMachine) -> bool: # pyright: ignore
        """Evaluate the decision"""
        return False


class LowHealthDecision(Decision):
    """Trigger when health drops below a threshold

    Args:
        health_threshold: The value at which to trigget the decision
    """
    def __init__(self, health_threshold) -> None:
        self.lower_health_threshold = health_threshold

    def decide(self, state_machine: StateMachine) -> bool:
        return state_machine.sprite.health < self.lower_health_threshold 
    

class FullHealthDecision(Decision):
    """Trigger when an enemies health reacher their max_health"""
    def decide(self, state_machine: StateMachine) -> bool:
        return state_machine.sprite.health >= state_machine.sprite.max_health


class WithinRangeDecision(Decision):
    """Triggers when sprite is outside of some allowed band or range of the target
    
    Args:
        target: The sprite to check distance against

        outer_limit: The furthest point of the allowed range before trigering
        leave at math.inf if no outer limit is required i.e. only inner distance matters

        inner_limit: The closest the sprite can get to the target before triggering this decision.
        leave at 0 if only outer limit is required

    Useage examples:
        If an enemy needs to be activated 'pulled' when the player gets within 400 pixels
        place then initially on an idle state with a WithinRangeDecision(target, inner_limit=400) 
        that only uses the inner limit in a transition to their first active state. 

        If an enemy needs to start seeking the player when the player gets too far away, 
        use a WithinRangeDecision(target, outer_limit=400) in a transition to their seeking state 

        If there is only a small band of distances an enemy should be in before changing state, 
        use both with WithinRangeDecision(target, inner_limit=200, outer_limit=600) etc.
    """
    def __init__(self, target: arcade.Sprite, outer_limit: float = math.inf, inner_limit: float = 0)-> None:
        self.target = target
        self.outer_limit = outer_limit
        self.inner_limit = inner_limit

        if self.inner_limit >= self.outer_limit:
            raise ValueError('inner_limit must be smaller than outer_limit')

    def decide(self, state_machine: StateMachine):
        dist = math.dist(state_machine.sprite.position, self.target.position) 
        return self.inner_limit < dist < self.outer_limit


class TimeElapsedDecision(Decision):
    """Trigger after some elapsed time. Note this is independent of frame rate

    Args:
        duration: The time in seconds to wait before triggering
    """
    def __init__(self, duration: float) -> None:
        self.start_time = time()
        self.duration = duration

    def decide(self, state_machine: StateMachine):
        return time() - self.start_time >= self.duration

class TakenDamageDecision(Decision):
    """Trigger when damage is taken for any reason

    Args:
        initial_health: The health of the sprite when the transition is first made
    """
    def __init__(self, initial_health: float) -> None:
        self.initial_health = initial_health

    def decide(self, state_machine: StateMachine) -> bool:
        return state_machine.sprite.health < self.initial_health

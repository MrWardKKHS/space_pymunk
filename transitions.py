from __future__ import annotations
from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from state_machines import StateMachine 
    from states import State
    from decisions import Decision

class Transition:
    def __init__(self, decision: Decision, true_state: Union[State, None], false_state: Union[State, None]) -> None:
        self.decision = decision
        self.true_state = true_state
        self.false_state = false_state

    def execute(self, state_machine: StateMachine):
        if self.decision.decide(state_machine) and self.true_state:
            state_machine.state.exit(state_machine)
            state_machine.state = self.true_state
            state_machine.state.enter(state_machine)

        elif self.false_state:
            state_machine.state.exit(state_machine)
            state_machine.state = self.false_state
            state_machine.state.enter(state_machine)

    def enter(self, state_machine: StateMachine):
        pass
    
    def exit(self, state_machine: StateMachine):
        pass

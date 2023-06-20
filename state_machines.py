import arcade
from states import SeekAndFleeState, State

class StateMachine:
    def __init__(self, sprite, physics_engine: arcade.PymunkPhysicsEngine):
        self.sprite = sprite
        self.state = State()
        self.physics_engine = physics_engine

    def update(self):
        self.state.execute(self)

    def awake(self):
        pass

    def start(self):
        pass

class FighterStateMachine(StateMachine):
    def __init__(self, sprite, physics_engine: arcade.PymunkPhysicsEngine):
        super().__init__(sprite, physics_engine)
        self.targets = []
        self.flee_targets = []

    def awake(self):
        self.state = SeekAndFleeState()
        self.state.enter(self)


# Some of this should live in the enemy class
# Handle some of the enemy behaviour
# if enemy.weapon_cooldown > 100 and enemy.pointing_at_target():
#    self.handle_sprite_fire(enemy)

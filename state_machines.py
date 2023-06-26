from __future__ import annotations
import arcade
from typing import TYPE_CHECKING
from typing import List
from states import IdleState, SeekAndFleeState, State, WaitForPull


if TYPE_CHECKING:
    from bullets import Bullet
    from fighter import Fighter, Sprite
    from swarm_of_bees import Bee
    from player import Player



class StateMachine:
    def __init__(self, sprite: Sprite):
        self.sprite = sprite
        self.state = State()

    def update(self):
        self.state.execute(self)

    def awake(self):
        pass

    def start(self):
        pass

class FighterStateMachine(StateMachine):
    def __init__(self, sprite: Fighter, physics_engine: arcade.PymunkPhysicsEngine, bullet_list: arcade.SpriteList, player_sprite: Player, rocks: arcade.SpriteList):
        super().__init__(sprite)
        self.target = player_sprite
        self.flee_targets = []
        self.bullet_list = bullet_list
        self.physics_engine = physics_engine
        self.rocks = rocks

    def awake(self):
        self.state = SeekAndFleeState()
        self.state.enter(self)

class BeeStateMachine(StateMachine):
    def __init__(self, sprite: Bee, physics_engine: arcade.PymunkPhysicsEngine, player_sprite: Player):
        super().__init__(sprite)
        self.target = player_sprite
        self.physics_engine = physics_engine
        self.other_bees: List[Bee] = []
        self.state = WaitForPull(player_sprite)

    def awake(self):
        self.state.enter(self)

# Some of this should live in the enemy class
# Handle some of the enemy behaviour
# if enemy.weapon_cooldown > 100 and enemy.pointing_at_target():
#    self.handle_sprite_fire(enemy)

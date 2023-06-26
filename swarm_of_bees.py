from state_machines import BeeStateMachine
from random import randint
import arcade
from fighter import Enemy
from player import Player

class Swarm:
    """A container for bees to keep them attracted to 
    each other
    
    Assits in the initialisation for scene, physics engine etc.
    """
    def __init__(self, x: float, y: float, level: int, size: int, physics_engine: arcade.PymunkPhysicsEngine, player: Player, scene) -> None:
        # make lots of bees
        self.bees = []
        self.pulled = False
        for _ in range(size):
            bee = Bee(x + randint(-90, 90), y + randint(-90, 90), level, self)
            self.bees.append(bee)
            bee.state_machine = BeeStateMachine(bee, physics_engine, player)
            physics_engine.add_sprite(
                bee, 
                mass=bee.mass, 
                collision_type='bee', 
                max_velocity=bee.max_velocity, # TODO All of these litterals SHOULD be constants...
                moment_of_inertia=100, 
                damping=0.9
            )
            bee.state_machine.awake()

        # add other bees in swarm to each bee
        for bee in self.bees:
            for other_bee in self.bees:
                if other_bee is not bee:
                    bee.other_bees.append(other_bee)
        for bee in self.bees:
            scene['enemies'].append(bee)

    def kill(self):
        for bee in self.bees:
            bee.kill()


class Bee(Enemy):
    def __init__(self, x: float, y: float, level: int, swarm) -> None:
        super().__init__(
            ':resources:images/space_shooter/playerShip1_orange.png',
             scale=0.2,
             x=x,
             y=y,
             level=level,
        )
        self.swarm = swarm
        self.other_bees = []
        self.mass = 0.1
        self.max_velocity = 200

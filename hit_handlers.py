import arcade
from player import Player
from fighter import Fighter
from bullets import Bullet, Orb
from swarm_of_bees import Bee

"""Note: All collision handlers should return True or False to signify if 
Further processing is required"""

def enemy_hit_handler(enemy: Fighter, bullet: Bullet, arbiter, space, data):
    """When the enemy is hit by a bullet, take off that bullet's damage

    Kill the enemy if its health falls below 0
    """
    enemy.take_damage(bullet.damage, bullet.level)
    bullet.kill()

def kill_bullet(rock: arcade.Sprite, bullet: Bullet, arbiter, space, data):
    bullet.kill()

def no_collision(a, b, arbiter, space, data):
    """use as a begin handler to turn off interactions between layers"""
    return False

def pick_up_exp(player: Player, orb: Orb, arbiter, space, data):
    player.gain_exp(orb.exp)
    orb.kill()

    # Stop processing physics on this collision
    return False

def bee_hit_handler(player: Player, bee: Bee, arbiter, space, data):
    # TODO damage player, explosion
    bee.kill()

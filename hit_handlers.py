import arcade
from fighter import Fighter
from bullets import Bullet

def enemy_hit_handler(enemy: Fighter, bullet: Bullet, arbiter, space, data):
    """When the enemy is hit by a bullet, take off that bullet's damage

    Kill the enemy if its health falls below 0
    """
    enemy.health -= 1
    bullet.kill()
    if enemy.health <= 0:
        enemy.kill()

def kill_bullet(rock: arcade.Sprite, bullet: Bullet, arbiter, space, data):
    bullet.kill()

def no_collision(a, b, arbiter, space, data):
    pass

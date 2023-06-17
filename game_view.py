import random
import arcade
from arcade.pymunk_physics_engine import PymunkPhysicsEngine
from pyglet.math import Vec2
import math
from constants import *
from fighter import Fighter
from player import Player

class TestGame(arcade.Window):
    def __init__(self):
        super().__init__(WIDTH, HEIGHT, TITLE)

        self.player_sprite = Player(1, 'blue', 400, 400)
        self.scene = arcade.Scene()
        self.torque_left = False
        self.torque_right = False
        self.a_pressed = False
        self.d_pressed = False
        self.s_pressed = False
        self.w_pressed = False
        self.camera = arcade.Camera()
        self.physics_engine = PymunkPhysicsEngine()

        # load in the joystick. This could be in a try except
        # in case a joystick is not avalible
        try:
            self.joystick = arcade.get_joysticks()[0]
            self.joystick.open()
            self.joystick.push_handlers(self)
        except IndexError:
            self.joystick = None

        arcade.set_background_color(arcade.color.BLACK)
        self.setup()

    def setup(self):
        self.scene = arcade.Scene()
        # add lists. This would normally be handles by your tilemap
        self.scene.add_sprite_list("player")
        self.scene.add_sprite_list("rocks")
        self.scene.add_sprite_list("enemies")
        self.scene.add_sprite_list("enemy_bullets")
        self.scene.add_sprite_list("player_bullets")
        self.physics_engine = arcade.PymunkPhysicsEngine(damping=1.0)
        
        # The player accepts a joystick number and
        # color planning to add multiple players
        self.player_sprite = Player(0, "blue", 500, 400)
        self.scene.add_sprite("player", self.player_sprite)
        self.physics_engine.add_sprite(
                self.player_sprite,
                collision_type='player',
                max_velocity=800,
                moment_of_inertia=60,
                damping=0.5
        )

        for i in range(5):
            # helper function to reduce code duplication
            self.spawn_enemy()

        self.accelerating_up = False
        self.accelerating_down = False
        self.accelerating_left = False
        self.accelerating_right = False
        self.torque_left = False
        self.torque_right = False
        # another helper function to reduce code duplication
        # and to seperate out game logic
        self.make_rocks()

        def enemy_hit_handler(enemy, bullet, arbiter, space, data):
            """
            This is a requirement of any two sprite types that you want to have interact
            in this case the enemy and the bullet

            The other arguments need to be as listed here

            This code will run whenever there is a collision between the A and B sprite types
            notice the level of indentation on this function. 
            It is defined WITHIN the self.setup function
            """
            enemy.health -= 1
            bullet.kill()
            if enemy.health <= 0:
                enemy.kill()
                self.spawn_enemy()

        # add the collision handler between these two sprite types
        # the post_handler is the callback function to run after the collision is delt with
        self.physics_engine.add_collision_handler(
                'enemy', 
                'player_bullet', 
                post_handler=enemy_hit_handler
        )

    def spawn_enemy(self):
        """Create an enemy and add it to the enemy list AND the physics engine"""

        enemy = Fighter(
            random.randint(int(self.player_sprite.center_x + WIDTH), 
            int(self.player_sprite.center_x + 4 * WIDTH)), 
            random.randint(0, HEIGHT)
        )
        # Add the sprite to the physics engine including specifying the collision type
        self.physics_engine.add_sprite(
                enemy, 
                collision_type='enemy', 
                max_velocity=400, # All of these litterals SHOULD be constants...
                moment_of_inertia=100, 
                damping=0.9
        )
        self.scene['enemies'].append(enemy)

    def make_rocks(self):
        """make 500 random rocks, add them to the sprite lists and the physics_engine"""
        for i in range(500): # This literal too, should be a constant
            rock_choice = random.choice(ROCK_CHOICES)
            size = 0.5 + random.random() * (1 + ROCK_CHOICES.index(rock_choice)//2)
            rock = arcade.Sprite(
                f":resources:images/space_shooter/{rock_choice}",
                size,
                center_x=random.randint(-WIDTH*2, WIDTH*50),
                center_y=random.randint(-HEIGHT*2, HEIGHT*2),
            )
            change_x = random.randint(-ROCK_SPEED, ROCK_SPEED)
            change_y = random.randint(-ROCK_SPEED, ROCK_SPEED)
            self.scene["rocks"].append(rock)

            # Add the rock to the physics engine. 
            # The mass is proportional to the size cubed
            # To give the impression of correctly scaling the mass in 3D
            # Collision type sets this as a rock with the physics_engine
            # and makes the collisions correct
            # Body_type dynamic ensures the rock has correct physics for movin bodies
            # setting the velocity just below 1 means rocks wont incorectly bounce off
            # each other with MORE speed than when they entered
            self.physics_engine.add_sprite(
                rock, 
                mass=5*size**3, 
                collision_type='rock', 
                body_type=arcade.PymunkPhysicsEngine.DYNAMIC, 
                elasticity=0.98
            )
            # Set the initial speed of the rock
            self.physics_engine.set_velocity(rock, (change_x, change_y))

    def wrap_y_axis_for_rocks(self, rock):
        """If the rock if above or below the screen, wrap it to the top/bottom"""

        # get the physics_body of the rock from the engine.
        # This is to allow easy access to things like its position and other physical properties
        rock_physics_body = self.physics_engine.get_physics_object(rock).body
        if rock_physics_body.position.y < -rock.height:
            rock_physics_body.position = (rock_physics_body.position.x, HEIGHT + rock.height)
        if rock_physics_body.position.y > HEIGHT + rock.height:
            rock_physics_body.position = (rock_physics_body.position.x, -rock.height)

    def on_draw(self):
        self.clear()
        self.camera.use()
        self.scene.draw()
        for enemy in self.scene['enemies']:
            arcade.draw_xywh_rectangle_filled(enemy.center_x-10, enemy.center_y + 60, 80, 8, arcade.color.RED)
            arcade.draw_xywh_rectangle_filled(
                    enemy.center_x-10, 
                    enemy.center_y + 60, 
                    80 * enemy.health / enemy.max_health, 
                    8, 
                    arcade.color.GREEN
            )

    def handle_player_movement(self):
        # .apply_force_at_world_point() applies a force irrespective of a 
        # sprites rotation. If rotation is import (think applying a thruster)
        # use .apply_force_at_local_point()
        self.player_sprite.physics_body.apply_force_at_world_point((
                self.acc_x * PLAYER_ACCELERATION, 
                self.acc_y * PLAYER_ACCELERATION 
            ), 
            self.player_sprite.physics_body.position
        )

        # handle right left rotation from keypresses
        if self.torque_left:
            self.player_sprite.rotate_left()
        if self.torque_right:
            self.player_sprite.rotate_right()

    def update(self, delta_time):
        self.physics_engine.step()
        self.handle_player_movement()
        self.scene.update()

        # Fighters to seek the player
        for enemy in self.scene['enemies']:
            enemy.target = self.player_sprite.position
            # Handle some of the enemy behaviour
            # Some of this should live in the enemy class
            if enemy.weapon_cooldown > 100 and enemy.pointing_at_target():
                self.handle_sprite_fire(enemy)

            # Create a desired direction pointing straight towards the player.
            # Apply the enemy steering behaviour directly towards that point
            enemy.seek(Vec2(self.player_sprite.center_x, self.player_sprite.center_y))

            # and not bunch up
            for other in self.scene['enemies']:
                if enemy is not other:
                    target = Vec2(other.center_x, other.center_y)
                    # If an enemy is within 300px of another enemy, 
                    # runaway from that enemy
                    enemy.flee(target, 300)

        # reposition rocks if they drift outside of the y axis
        for rock in self.scene['rocks']:
            self.wrap_y_axis_for_rocks(rock)

        self.camera.move_to((self.player_sprite.center_x - WIDTH/4, 0))


    def handle_sprite_fire(self, sprite):
        """A helper function to seperate out player firing code"""
        bullets = sprite.fire()
        # TODO: Add bullet type on bullet. Distinguish player bullets with enemies??
        for bullet in bullets:
            self.scene['player_bullets'].append(bullet)
            self.physics_engine.add_sprite(bullet, collision_type=bullet.collision_type, max_velocity=bullet.max_velocity, moment_of_inertia=bullet.moment_of_inertia, mass=bullet.mass, damping=0.99)
            self.physics_engine.set_velocity(bullet, (bullet.change_x, bullet.change_y))

    def on_joybutton_press(self, _joystick, button):
        """
        Handle button presses on the joystick
        left right up down motion is allready handled in the Update function
        and don't require event handlers here
        """
        if button == 2: 
            self.handle_sprite_fire(self.player)
        if button == 5:
            self.torque_left = True
        if button == 4:
            self.torque_right = True
    
    def on_joybutton_release(self, _joystick, button):
        """Stop rotating when L R bumpers are released"""
        if button == 5:
            self.torque_left = False
        if button == 4:
            self.torque_right = False

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol== arcade.key.A:
            self.a_pressed = True
        if symbol== arcade.key.D:
            self.d_pressed = True
        if symbol== arcade.key.W:
            self.w_pressed = True
        if symbol== arcade.key.S:
            self.s_pressed = True
        if symbol == arcade.key.SPACE:
            self.handle_sprite_fire(self.player_sprite)
        if symbol == arcade.key.E:
            self.torque_left = True
        if symbol == arcade.key.Q:
            self.torque_right = True

    def on_key_release(self, symbol: int, modifiers: int):
        if symbol== arcade.key.A:
            self.a_pressed = False
        if symbol== arcade.key.D:
            self.d_pressed = False
        if symbol== arcade.key.W:
            self.w_pressed = False
        if symbol== arcade.key.S:
            self.s_pressed = False
        if symbol == arcade.key.E:
            self.torque_left = False
        if symbol == arcade.key.Q:
            self.torque_right = False

    @property
    def acc_x(self):
        if self.joystick:
            return self.joystick.x
        else:
            return self.d_pressed - self.a_pressed

    @property
    def acc_y(self):
        if self.joystick:
            return -self.joystick.y
        else:
            return self.w_pressed - self.s_pressed


def main():
    window = TestGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
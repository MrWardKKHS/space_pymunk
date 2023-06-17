import arcade
from pymunk.body import Body

def get_physics_body(physics_engine: arcade.PymunkPhysicsEngine, sprite: arcade.Sprite) -> Body:
    """Return a physics body to help with typing"""
    return physics_engine.get_physics_object(sprite).body

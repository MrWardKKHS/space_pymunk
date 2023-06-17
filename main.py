import arcade
from game_view import TestGame

def main():
    window = TestGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()

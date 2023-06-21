import arcade
from game_view import TestGame

def main():
    window = TestGame()
    window.setup()
    arcade.run()
    print('wazzup')

if __name__ == "__main__":
    main()

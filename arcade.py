import arcade
import random


SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Пешерный пацик"
PLAYER_SPEED = 5


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("images/.png")
import arcade
import random

TITLE = "proekt"
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 920
SCREEN_TITLE = "Castle Tiles"
TILE_SCALING = 0.8
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_FORCE = 12

COINS_PER_ROUND = 10


class Player(arcade.Sprite):

    def __init__(self):
        super().__init__()

        self.texture = arcade.load_texture('PICTURES/pacik/idle_viking.png')
        self.scale = 0.5
        self.width = 40
        self.height = 60

        self.center_x = 100
        self.center_y = 300
        self.change_x = 0
        self.change_y = 0
        self.speed = PLAYER_SPEED
        self.jump_force = JUMP_FORCE
        self.on_ground = False
        self.can_double_jump = False
        self.double_jump_used = False

        self.coins = 0
        self.total_coins = 0
        self.lives = 3

    def update(self):
        self.change_y -= GRAVITY

        self.center_x += self.change_x
        self.center_y += self.change_y

    def update_physics(self, collision_list):
        self.on_ground = False

        for platform in collision_list:
            if self.collides_with_sprite(platform):
                if self.change_y < 0:
                    self.bottom = platform.top
                    self.change_y = 0
                    self.on_ground = True
                    self.double_jump_used = False
                elif self.change_y > 0:
                    self.top = platform.bottom
                    self.change_y = 0
                elif self.change_x > 0:
                    self.right = platform.left
                    self.change_x = 0
                elif self.change_x < 0:
                    self.left = platform.right
                    self.change_x = 0

    def move_left(self):
        self.change_x = -self.speed

    def move_right(self):
        self.change_x = self.speed

    def stop_x(self):
        self.change_x = 0

    def jump(self):
        if self.on_ground:
            self.change_y = self.jump_force
            self.on_ground = False
            return True
        elif self.can_double_jump and not self.double_jump_used:
            self.change_y = self.jump_force * 0.8
            self.double_jump_used = True
            return True
        return False


class Coin(arcade.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.load_texture("PICTURES/skelet/217853.png")
        self.scale = 0.1
        self.center_x = x
        self.center_y = y
        self.collected = False


class Door(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.width = 40
        self.height = 80

    def draw(self):
        arcade.draw_lbwh_rectangle_filled(
            self.center_x - self.width / 2,
            self.center_y - self.height / 2,
            self.width, self.height,
            arcade.color.DARK_BROWN
        )
        arcade.draw_circle_filled(
            self.center_x - 10, self.center_y,
            4, arcade.color.GOLD
        )


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False

    def check_hover(self, mouse_x, mouse_y):
        self.is_hovered = (self.x - self.width / 2 < mouse_x < self.x + self.width / 2 and
                           self.y - self.height / 2 < mouse_y < self.y + self.height / 2)
        return self.is_hovered

    def check_click(self, mouse_x, mouse_y):
        return self.check_hover(mouse_x, mouse_y)

    def draw(self):
        color = self.hover_color if self.is_hovered else self.color

        arcade.draw_lbwh_rectangle_filled(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width, self.height,
            color
        )

        arcade.draw_lbwh_rectangle_outline(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width, self.height,
            arcade.color.WHITE, 3
        )

        arcade.draw_text(
            self.text,
            self.x, self.y - 10,
            self.text_color, 24,
            anchor_x="center", anchor_y="center"
        )


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.background = arcade.load_texture("PICTURES/backgrounds/lobby.jpg")

        self.player = None
        self.player_list = arcade.SpriteList()

        self.coin_list = arcade.SpriteList()

        self.tile_map = None
        self.door_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()

        self.left_pressed = False
        self.right_pressed = False
        self.space_pressed = False


        self.game_victory = False
        self.game_over = False
        self.round = 1

        self.restart_button = Button(
            SCREEN_WIDTH // 2, 150,
            200, 60,
            "ПЕРЕЗАПУСК",
            (0, 100, 200),
            (50, 150, 250),
            arcade.color.WHITE
        )

        self.setup()

    def setup(self):
        self.player = Player()
        self.player.position = (100, 300)
        self.player_list.append(self.player)

        try:
            map_name = "castle.tmx"
            self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

            for sprite in self.tile_map.sprite_lists["door"]:
                door = sprite
                self.door_list.append(door)


            self.collision_list = self.tile_map.sprite_lists["collision"]

        except Exception as e:
            platform = arcade.Sprite()
            platform.width = SCREEN_WIDTH
            platform.height = 50
            platform.center_x = SCREEN_WIDTH // 2
            platform.center_y = 50
            self.collision_list.append(platform)

            platform2 = arcade.Sprite()
            platform2.width = 200
            platform2.height = 20
            platform2.center_x = 500
            platform2.center_y = 300
            self.collision_list.append(platform2)

            door = Door(900, 100)
            self.door_list.append(door)

        self.spawn_coins(COINS_PER_ROUND)

        print(f"Раунд {self.round}. Монет на уровне: {len(self.coin_list)}")

    def spawn_coins(self, count):
        for i in range(count):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            coin = Coin(x, y)
            self.coin_list.append(coin)

    def next_round(self):
        """Переход к следующему раунду"""
        self.round += 1
        self.player.coins = 0
        self.spawn_coins(COINS_PER_ROUND)
        print(f"Раунд {self.round}! Появились новые монеты!")

    def on_draw(self):
        """Отрисовка"""
        self.clear()

        arcade.draw_texture_rect(
            self.background,
            arcade.XYWH(
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                SCREEN_WIDTH,
                SCREEN_HEIGHT
            )
        )

        self.collision_list.draw()
        self.door_list.draw()
        self.coin_list.draw()
        self.player_list.draw()

        arcade.draw_lbwh_rectangle_filled(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT - 80,
            200, 40,
            (0, 0, 0, 150)
        )

        lives_text = "❤️ " * self.player.lives
        arcade.draw_text(
            f"Жизни: {lives_text}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60,
            arcade.color.RED, 24,
            anchor_x="center", anchor_y="center"
        )

        arcade.draw_lbwh_rectangle_filled(
            SCREEN_WIDTH // 2 - 150,
            SCREEN_HEIGHT - 130,
            300, 40,
            (0, 0, 0, 150)
        )

        arcade.draw_text(
            f"Монеты раунда: {self.player.coins} / {COINS_PER_ROUND}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 110,
            arcade.color.GOLD, 24,
            anchor_x="center", anchor_y="center"
        )

        arcade.draw_text(
            f"Всего собрано: {self.player.total_coins}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
            arcade.color.WHITE, 18,
            anchor_x="center", anchor_y="center"
        )
        arcade.draw_text(
            f"Раунд: {self.round}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180,
            arcade.color.CYAN, 18,
            anchor_x="center", anchor_y="center"
        )

        if self.player.coins >= COINS_PER_ROUND:
            arcade.draw_lbwh_rectangle_filled(
                SCREEN_WIDTH // 2 - 200,
                SCREEN_HEIGHT - 220,
                400, 40,
                (0, 100, 0, 150)
            )

        if self.game_victory:
            arcade.draw_lbwh_rectangle_filled(
                0, 0,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                (0, 0, 0, 150)
            )

            arcade.draw_text(
                "ПОБЕДА!",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
                arcade.color.GOLD, 72,
                anchor_x="center", anchor_y="center"
            )

            arcade.draw_text(
                f"Вы собрали {self.player.total_coins} монет за {self.round - 1} раундов!",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                arcade.color.WHITE, 36,
                anchor_x="center", anchor_y="center"
            )

            self.restart_button.draw()

        elif self.game_over:
            arcade.draw_lbwh_rectangle_filled(
                0, 0,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                (0, 0, 0, 150)
            )

            arcade.draw_text(
                "ИГРА ОКОНЧЕНА",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
                arcade.color.RED, 72,
                anchor_x="center", anchor_y="center"
            )

            arcade.draw_text(
                f"Вы собрали {self.player.total_coins} монет",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                arcade.color.GOLD, 36,
                anchor_x="center", anchor_y="center"
            )

            self.restart_button.draw()

    def on_update(self, delta_time):
        if self.game_victory or self.game_over:
            return

        if self.left_pressed and not self.right_pressed:
            self.player.move_left()
        elif self.right_pressed and not self.left_pressed:
            self.player.move_right()
        else:
            self.player.stop_x()

        self.player.update()

        self.player.update_physics(self.collision_list)

        if self.player.center_y < -100:
            self.player.center_x = 100
            self.player.center_y = 300
            self.player.change_x = 0
            self.player.change_y = 0
            self.player.lives -= 1
            print(f"Потеряна жизнь! Осталось: {self.player.lives}")

            if self.player.lives <= 0:
                self.game_over = True
                print("Игра окончена!")

        coins_collected = []
        for coin in self.coin_list:
            if self.player.collides_with_sprite(coin):
                coin.collected = True
                self.player.coins += 1
                self.player.total_coins += 1
                coins_collected.append(coin)
                print(f"Монета собрана! Раунд: {self.player.coins}/{COINS_PER_ROUND}, Всего: {self.player.total_coins}")

        for coin in coins_collected:
            self.coin_list.remove(coin)

        if self.player.coins >= COINS_PER_ROUND:
            for door in self.door_list:
                if self.player.collides_with_sprite(door):
                    self.next_round()
                    break

        if self.space_pressed:
            if self.player.jump():
                pass
            self.space_pressed = False

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            self.space_pressed = True
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            self.space_pressed = False

    def on_mouse_motion(self, x, y, dx, dy):
        if self.game_victory or self.game_over:
            self.restart_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_victory or self.game_over:
            if self.restart_button.check_click(x, y):
                self.restart_game()

    def restart_game(self):
        print("Перезапуск игры...")

        self.player.center_x = 100
        self.player.center_y = 300
        self.player.change_x = 0
        self.player.change_y = 0
        self.player.coins = 0
        self.player.total_coins = 0
        self.player.lives = 3

        self.coin_list = arcade.SpriteList()
        self.spawn_coins(COINS_PER_ROUND)
        self.round = 1

        self.game_victory = False
        self.game_over = False

        print(f"Игра перезапущена. Раунд {self.round}. Монет на уровне: {len(self.coin_list)}")


def main():
    """Главная функция"""
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
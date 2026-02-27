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
CAMERA_LERP = 0.1
COINS_PER_ROUND = 10
ZOMBIE_COUNT = 5
LIFE_COST = 5


class Player(arcade.Sprite):

    def __init__(self):
        super().__init__()

        self.idle_texture = arcade.load_texture('PICTURES/pacik/idle_viking.png')
        self.jump_texture = arcade.load_texture('PICTURES/pacik/jump_viking.png')

        self.texture = self.idle_texture
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

        self.last_y = self.center_y

    def update(self):
        self.last_y = self.center_y
        self.change_y -= GRAVITY

        self.center_x += self.change_x
        self.center_y += self.change_y

        if not self.on_ground:
            self.texture = self.jump_texture
        else:
            self.texture = self.idle_texture

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

    def buy_life(self):

        if self.total_coins >= LIFE_COST:
            self.total_coins -= LIFE_COST
            self.lives += 1
            return True
        return False


class Zombie(arcade.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.texture = arcade.load_texture('PICTURES/pacik/krasni.png')
        self.scale = 0.4
        self.width = 40
        self.height = 60

        self.center_x = x
        self.center_y = y
        self.change_x = 0
        self.change_y = 0
        self.speed = 1.5
        self.direction = 1  # 1 - вправо, -1 - влево
        self.patrol_distance = 200
        self.start_x = x
        self.on_ground = False

    def update(self, platforms):

        self.change_y -= GRAVITY


        if abs(self.center_x - self.start_x) > self.patrol_distance:
            self.direction *= -1

        self.change_x = self.speed * self.direction


        self.center_x += self.change_x
        self.center_y += self.change_y


        self.on_ground = False
        for platform in platforms:
            if self.collides_with_sprite(platform):
                if self.change_y < 0:
                    self.bottom = platform.top
                    self.change_y = 0
                    self.on_ground = True
                elif self.change_y > 0:
                    self.top = platform.bottom
                    self.change_y = 0
                elif self.change_x > 0:
                    self.right = platform.left
                    self.change_x = 0
                elif self.change_x < 0:
                    self.left = platform.right
                    self.change_x = 0

    def draw(self):

        arcade.draw_lbwh_rectangle_filled(
            self.center_x - self.width / 2,
            self.center_y - self.height / 2,
            self.width, self.height,
            (100, 150, 50)  # Зеленый цвет
        )

        eye_offset = 5 if self.direction > 0 else -5
        arcade.draw_circle_filled(
            self.center_x - 8 + eye_offset, self.center_y + 10,
            4, (255, 0, 0)
        )
        arcade.draw_circle_filled(
            self.center_x + 8 + eye_offset, self.center_y + 10,
            4, (255, 0, 0)
        )


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


class ShopButton:


    def __init__(self):
        self.x = SCREEN_WIDTH - 100
        self.y = SCREEN_HEIGHT - 80
        self.width = 80
        self.height = 80
        self.is_hovered = False
        self.is_open = False

    def check_hover(self, mouse_x, mouse_y):
        self.is_hovered = (self.x - self.width / 2 < mouse_x < self.x + self.width / 2 and
                           self.y - self.height / 2 < mouse_y < self.y + self.height / 2)
        return self.is_hovered

    def check_click(self, mouse_x, mouse_y):
        return self.check_hover(mouse_x, mouse_y)

    def draw(self):

        if self.is_open:
            color = (100, 200, 100)  # Зеленый когда открыт
        elif self.is_hovered:
            color = (200, 200, 100)  # Желтый при наведении
        else:
            color = (100, 100, 200)  # Синий обычно


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
            "🛒",
            self.x, self.y,
            arcade.color.WHITE, 40,
            anchor_x="center", anchor_y="center"
        )

    def draw_shop_menu(self, player):

        if not self.is_open:
            return


        arcade.draw_lbwh_rectangle_filled(
            SCREEN_WIDTH // 2 - 250,
            SCREEN_HEIGHT // 2 - 200,
            500, 400,
            (50, 50, 80, 240)
        )

        arcade.draw_lbwh_rectangle_outline(
            SCREEN_WIDTH // 2 - 250,
            SCREEN_HEIGHT // 2 - 200,
            500, 400,
            arcade.color.GOLD, 3
        )


        arcade.draw_text(
            "МАГАЗИН",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150,
            arcade.color.GOLD, 36,
            anchor_x="center", anchor_y="center"
        )


        arcade.draw_text(
            f"Монеты: {player.total_coins}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100,
            arcade.color.YELLOW, 24,
            anchor_x="center", anchor_y="center"
        )


        arcade.draw_text(
            f"Жизни: {player.lives}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60,
            arcade.color.RED, 24,
            anchor_x="center", anchor_y="center"
        )


        can_afford = player.total_coins >= LIFE_COST
        price_color = arcade.color.GREEN if can_afford else arcade.color.RED


        arcade.draw_text(
            "❤️",
            SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2,
            arcade.color.RED, 40,
            anchor_x="center", anchor_y="center"
        )


        arcade.draw_text(
            f"Цена: {LIFE_COST} монет",
            SCREEN_WIDTH // 2 + 50, SCREEN_HEIGHT // 2,
            price_color, 20,
            anchor_x="center", anchor_y="center"
        )


        button_color = (0, 150, 0) if can_afford else (100, 100, 100)
        arcade.draw_lbwh_rectangle_filled(
            SCREEN_WIDTH // 2 - 75,
            SCREEN_HEIGHT // 2 - 60,
            150, 40,
            button_color
        )

        arcade.draw_text(
            "КУПИТЬ",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40,
            arcade.color.WHITE, 20,
            anchor_x="center", anchor_y="center"
        )


        arcade.draw_text(
            "Нажмите E для покупки, ESC для выхода",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120,
            arcade.color.LIGHT_GRAY, 16,
            anchor_x="center", anchor_y="center"
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


        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()

        self.background = arcade.load_texture("PICTURES/backgrounds/lobby.jpg")

        self.player = None
        self.player_list = arcade.SpriteList()

        self.coin_list = arcade.SpriteList()
        self.zombie_list = arcade.SpriteList()

        self.tile_map = None
        self.door_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()

        self.left_pressed = False
        self.right_pressed = False
        self.space_pressed = False
        self.e_pressed = False

        self.game_victory = False
        self.game_over = False
        self.game_state = "playing"
        self.round = 1


        self.shop_button = ShopButton()

        self.restart_button = Button(
            SCREEN_WIDTH // 2, 150,
            200, 60,
            "ПЕРЕЗАПУСК",
            (0, 100, 200),
            (50, 150, 250),
            arcade.color.WHITE
        )


        self.world_width = SCREEN_WIDTH
        self.world_height = SCREEN_HEIGHT

        self.setup()

    def _place_sprite_safely(self, sprite, max_attempts=100):
        for _ in range(max_attempts):
            sprite.position = (
                random.randint(50, self.world_width - 50),
                random.randint(50, self.world_height - 50)
            )
            collisions = arcade.check_for_collision_with_list(sprite, self.collision_list)
            if not collisions:
                return True
        return False

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


            self.world_width = int(self.tile_map.width * self.tile_map.tile_width * TILE_SCALING)
            self.world_height = int(self.tile_map.height * self.tile_map.tile_height * TILE_SCALING)

        except Exception as e:
            door = Door(1700, 100)
            self.door_list.append(door)


        self.spawn_coins(COINS_PER_ROUND)


        self.spawn_zombies(ZOMBIE_COUNT)

        print(f"Раунд {self.round}. Монет на уровне: {len(self.coin_list)}, Зомби: {len(self.zombie_list)}")
        print(f"Размер мира: {self.world_width} x {self.world_height}")

    def spawn_coins(self, count):
        coins_created = 0
        attempts = 0
        max_attempts = 1000

        while coins_created < count and attempts < max_attempts:
            attempts += 1
            x = random.randint(100, self.world_width - 100)
            y = random.randint(100, self.world_height - 100)
            coin = Coin(x, y)

            collision_with_platforms = arcade.check_for_collision_with_list(coin, self.collision_list)
            collision_with_zombies = arcade.check_for_collision_with_list(coin, self.zombie_list)

            if not collision_with_platforms and not collision_with_zombies:
                self.coin_list.append(coin)
                coins_created += 1

        print(f"Создано монет: {coins_created}")

    def spawn_zombies(self, count):
        zombies_created = 0
        attempts = 0
        max_attempts = 1000

        while zombies_created < count and attempts < max_attempts:
            attempts += 1
            x = random.randint(200, self.world_width - 200)
            y = 400

            for platform in self.collision_list:
                if abs(x - platform.center_x) < platform.width / 2:
                    y = platform.top + 30
                    break

            zombie = Zombie(x, y)

            collision_with_platforms = arcade.check_for_collision_with_list(zombie, self.collision_list)

            if not collision_with_platforms:
                self.zombie_list.append(zombie)
                zombies_created += 1

        print(f"Создано зомби: {zombies_created}")

    def next_round(self):
        self.round += 1
        self.player.coins = 0
        self.spawn_coins(COINS_PER_ROUND)
        self.spawn_zombies(2)
        print(f"Раунд {self.round}! Появились новые монеты и зомби!")

    def on_draw(self):
        """Отрисовка"""
        self.clear()

        self.world_camera.use()

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
        self.zombie_list.draw()
        self.player_list.draw()

        # 2) GUI
        self.gui_camera.use()

        # Интерфейс
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
            f"Зомби: {len(self.zombie_list)}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
            arcade.color.GREEN, 18,
            anchor_x="center", anchor_y="center"
        )

        arcade.draw_text(
            f"Всего монет: {self.player.total_coins}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180,
            arcade.color.WHITE, 18,
            anchor_x="center", anchor_y="center"
        )

        arcade.draw_text(
            f"Раунд: {self.round}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 210,
            arcade.color.CYAN, 18,
            anchor_x="center", anchor_y="center"
        )

        # Кнопка магазина в правом верхнем углу
        self.shop_button.draw()

        # Меню магазина
        if self.game_state == "shop":
            self.shop_button.draw_shop_menu(self.player)

        # Экран победы
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

        # Если мы в магазине, не обновляем игру
        if self.game_state == "shop":
            return

        # Управление
        if self.left_pressed and not self.right_pressed:
            self.player.move_left()
        elif self.right_pressed and not self.left_pressed:
            self.player.move_right()
        else:
            self.player.stop_x()

        self.player.update()
        self.player.update_physics(self.collision_list)

        # Проверка падения
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

        # Обновление зомби
        for zombie in self.zombie_list:
            zombie.update(self.collision_list)

        # Проверка столкновений с зомби
        zombies_to_remove = []
        for zombie in self.zombie_list:
            if self.player.collides_with_sprite(zombie):
                if self.player.change_y < 0 and self.player.bottom < zombie.center_y + 10:
                    zombies_to_remove.append(zombie)
                    print("Зомби убит прыжком на голову!")
                else:
                    self.player.lives -= 1
                    print(f"Зомби атаковал! Жизней осталось: {self.player.lives}")

                    if self.player.center_x < zombie.center_x:
                        self.player.center_x -= 50
                    else:
                        self.player.center_x += 50

                    if self.player.lives <= 0:
                        self.game_over = True
                        print("Игра окончена!")

        for zombie in zombies_to_remove:
            self.zombie_list.remove(zombie)

        # Сбор монет
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

        # Проверка двери
        if self.player.coins >= COINS_PER_ROUND:
            for door in self.door_list:
                if self.player.collides_with_sprite(door):
                    self.next_round()
                    break

        # Прыжок
        if self.space_pressed:
            if self.player.jump():
                pass
            self.space_pressed = False

        # Камера следует за игроком
        target_position = (
            self.player.center_x,
            self.player.center_y
        )

        half_width = SCREEN_WIDTH / 2
        half_height = SCREEN_HEIGHT / 2

        min_x = half_width
        max_x = self.world_width - half_width
        min_y = half_height
        max_y = self.world_height - half_height

        clamped_x = max(min_x, min(max_x, target_position[0]))
        clamped_y = max(min_y, min(max_y, target_position[1]))

        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            (clamped_x, clamped_y),
            CAMERA_LERP,
        )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            self.space_pressed = True
        elif key == arcade.key.E:
            if self.game_state == "shop":
                # Покупка в магазине
                if self.player.buy_life():
                    print(f"Куплена жизнь! Теперь жизней: {self.player.lives}")
            else:
                # Открытие магазина (всегда можно открыть, не нужно подходить)
                self.game_state = "shop"
                self.shop_button.is_open = True
        elif key == arcade.key.ESCAPE:
            if self.game_state == "shop":
                # Выход из магазина
                self.game_state = "playing"
                self.shop_button.is_open = False
            else:
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

        # Проверка наведения на кнопку магазина
        self.shop_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_victory or self.game_over:
            if self.restart_button.check_click(x, y):
                self.restart_game()

        # Клик по кнопке магазина
        if self.shop_button.check_click(x, y):
            if self.game_state == "shop":
                self.game_state = "playing"
                self.shop_button.is_open = False
            else:
                self.game_state = "shop"
                self.shop_button.is_open = True

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
        self.zombie_list = arcade.SpriteList()
        self.spawn_coins(COINS_PER_ROUND)
        self.spawn_zombies(ZOMBIE_COUNT)
        self.round = 1
        self.game_state = "playing"
        self.shop_button.is_open = False

        self.game_victory = False
        self.game_over = False

        # Сброс камеры
        self.world_camera.position = (self.player.center_x, self.player.center_y)

        print(
            f"Игра перезапущена. Раунд {self.round}. Монет на уровне: {len(self.coin_list)}, Зомби: {len(self.zombie_list)}")


def main():
    """Главная функция"""
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
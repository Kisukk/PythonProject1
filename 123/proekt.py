import arcade
import random

# Константы
TITLE = "proekt"
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 920
SCREEN_TITLE = "Castle Tiles"
TILE_SCALING = 0.8
SPEED = 5
GRAVITY = 0.5
JUMP_FORCE = 12


class Player(arcade.Sprite):
    """Класс игрока"""

    def __init__(self):
        super().__init__()

        # Загрузка текстуры игрока
        self.texture = arcade.load_texture('PICTURES/pacik/idle_viking.png')
        self.scale = 0.5
        self.width = 40
        self.height = 60

        # Физика
        self.center_x = 100
        self.center_y = 100
        self.change_x = 0
        self.change_y = 0
        self.speed = SPEED
        self.jump_force = JUMP_FORCE
        self.on_ground = False

        # Характеристики
        self.coins = 0
        self.lives = 3

    def update(self):
        """Обновление позиции"""
        self.center_x += self.change_x
        self.center_y += self.change_y

    def update_physics(self, collision_list):
        """Проверка столкновений с платформами"""
        self.on_ground = False

        for platform in collision_list:
            if self.collides_with_sprite(platform):
                if self.change_y < 0:  # Падение вниз
                    self.bottom = platform.top
                    self.change_y = 0
                    self.on_ground = True
                elif self.change_y > 0:  # Прыжок вверх
                    self.top = platform.bottom
                    self.change_y = 0
                elif self.change_x > 0:  # Движение вправо
                    self.right = platform.left
                    self.change_x = 0
                elif self.change_x < 0:  # Движение влево
                    self.left = platform.right
                    self.change_x = 0

    def move_left(self):
        """Движение влево"""
        self.change_x = -self.speed

    def move_right(self):
        """Движение вправо"""
        self.change_x = self.speed

    def stop_x(self):
        """Остановка по X"""
        self.change_x = 0

    def jump(self):
        """Прыжок"""
        if self.on_ground:
            self.change_y = self.jump_force
            self.on_ground = False


class Coin(arcade.Sprite):
    """Класс монеты"""

    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.load_texture("PICTURES/skelet/217853.png")
        self.scale = 0.1
        self.center_x = x
        self.center_y = y
        self.collected = False


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Фон
        self.background = arcade.load_texture("PICTURES/backgrounds/lobby.jpg")

        # Игрок
        self.player = None
        self.player_list = arcade.SpriteList()

        # Монеты
        self.coin_list = arcade.SpriteList()

        # Карта
        self.tile_map = None
        self.door_list = arcade.SpriteList()
        self.collision_list = arcade.SpriteList()

        # Физика
        self.physics_engine = None

        # Управление
        self.left_pressed = False
        self.right_pressed = False
        self.space_pressed = False

        self.setup()

    def setup(self):
        """Настройка игры"""
        # Создание игрока
        self.player = Player()
        self.player.position = (100, 100)
        self.player_list.append(self.player)

        # Загрузка тайловой карты
        try:
            map_name = "castle.tmx"
            self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

            # Загрузка списков спрайтов из карты
            if "door" in self.tile_map.sprite_lists:
                self.door_list = self.tile_map.sprite_lists["door"]

            if "collision" in self.tile_map.sprite_lists:
                self.collision_list = self.tile_map.sprite_lists["collision"]

            print("Карта загружена успешно")
        except Exception as e:
            print(f"Ошибка загрузки карты: {e}")

        # Создание физического движка
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            self.collision_list,
            gravity_constant=GRAVITY
        )

        # Создание монет
        for _ in range(10):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            coin = Coin(x, y)
            self.coin_list.append(coin)

    def on_draw(self):
        """Отрисовка"""
        self.clear()

        # Фон
        arcade.draw_texture_rect(
            self.background,
            arcade.XYWH(
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2,
                SCREEN_WIDTH,
                SCREEN_HEIGHT
            )
        )

        # Отрисовка объектов
        self.collision_list.draw()
        self.door_list.draw()
        self.coin_list.draw()
        self.player_list.draw()

        # UI
        arcade.draw_text(
            f"Монеты: {self.player.coins}",
            10, SCREEN_HEIGHT - 30,
            arcade.color.WHITE, 20
        )

        arcade.draw_text(
            f"Жизни: {self.player.lives}",
            10, SCREEN_HEIGHT - 60,
            arcade.color.RED, 20
        )

    def on_update(self, delta_time):
        """Обновление"""
        # Управление
        if self.left_pressed and not self.right_pressed:
            self.player.move_left()
        elif self.right_pressed and not self.left_pressed:
            self.player.move_right()
        else:
            self.player.stop_x()

        if self.space_pressed:
            self.player.jump()
            self.space_pressed = False  # Однократный прыжок

        # Обновление физики
        self.physics_engine.update()

        # Проверка сбора монет
        coins_collected = []
        for coin in self.coin_list:
            if self.player.collides_with_sprite(coin):
                coin.collected = True
                self.player.coins += 1
                coins_collected.append(coin)

        for coin in coins_collected:
            self.coin_list.remove(coin)

        # Проверка столкновения с дверью
        for door in self.door_list:
            if self.player.collides_with_sprite(door):
                print("Дверь открыта!")
                # Здесь можно добавить переход на следующий уровень

    def on_key_press(self, key, modifiers):
        """Обработка нажатия клавиш"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            self.space_pressed = True
        elif key == arcade.key.ESCAPE:
            arcade.close_window()

    def on_key_release(self, key, modifiers):
        """Обработка отпускания клавиш"""
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.UP or key == arcade.key.W or key == arcade.key.SPACE:
            self.space_pressed = False


def main():
    """Главная функция"""
    game = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
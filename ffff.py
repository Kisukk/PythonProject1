import arcade
import random

# Константы
TITLE = "proekt"
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 920
SCREEN_TITLE = "Castle Tiles"
TILE_SCALING = 0.8
PLAYER_SPEED = 5
GRAVITY = 0.5
JUMP_FORCE = 12

# Константы монет
COINS_PER_ROUND = 10  # По 10 монет за раунд


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
        self.center_y = 300
        self.change_x = 0
        self.change_y = 0
        self.speed = PLAYER_SPEED
        self.jump_force = JUMP_FORCE
        self.on_ground = False
        self.can_double_jump = False
        self.double_jump_used = False

        # Характеристики
        self.coins = 0
        self.total_coins = 0  # Всего собрано монет за все раунды
        self.lives = 3

    def update(self):
        """Обновление позиции с учетом гравитации"""
        # Применяем гравитацию
        self.change_y -= GRAVITY

        # Обновляем позицию
        self.center_x += self.change_x
        self.center_y += self.change_y

    def update_physics(self, collision_list):
        """Проверка столкновений с платформами"""
        self.on_ground = False

        for platform in collision_list:
            if self.collides_with_sprite(platform):
                # Столкновение сверху (падение на платформу)
                if self.change_y < 0:
                    self.bottom = platform.top
                    self.change_y = 0
                    self.on_ground = True
                    self.double_jump_used = False
                # Столкновение снизу (удар головой)
                elif self.change_y > 0:
                    self.top = platform.bottom
                    self.change_y = 0
                # Столкновение справа
                elif self.change_x > 0:
                    self.right = platform.left
                    self.change_x = 0
                # Столкновение слева
                elif self.change_x < 0:
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
            # Обычный прыжок
            self.change_y = self.jump_force
            self.on_ground = False
            return True
        elif self.can_double_jump and not self.double_jump_used:
            # Двойной прыжок
            self.change_y = self.jump_force * 0.8
            self.double_jump_used = True
            return True
        return False


class Coin(arcade.Sprite):
    """Класс монеты"""

    def __init__(self, x, y):
        super().__init__()
        self.texture = arcade.load_texture("PICTURES/skelet/217853.png")
        self.scale = 0.1
        self.center_x = x
        self.center_y = y
        self.collected = False


class Door(arcade.Sprite):
    """Класс двери"""

    def __init__(self, x, y):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.width = 40
        self.height = 80

    def draw(self):
        """Отрисовка двери"""
        arcade.draw_lbwh_rectangle_filled(
            self.center_x - self.width / 2,
            self.center_y - self.height / 2,
            self.width, self.height,
            arcade.color.DARK_BROWN
        )
        # Ручка
        arcade.draw_circle_filled(
            self.center_x - 10, self.center_y,
            4, arcade.color.GOLD
        )


class Button:
    """Класс кнопки"""

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
        """Проверка наведения мыши"""
        self.is_hovered = (self.x - self.width / 2 < mouse_x < self.x + self.width / 2 and
                           self.y - self.height / 2 < mouse_y < self.y + self.height / 2)
        return self.is_hovered

    def check_click(self, mouse_x, mouse_y):
        """Проверка клика"""
        return self.check_hover(mouse_x, mouse_y)

    def draw(self):
        """Отрисовка кнопки"""
        color = self.hover_color if self.is_hovered else self.color

        # Рисуем прямоугольник кнопки
        arcade.draw_lbwh_rectangle_filled(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width, self.height,
            color
        )

        # Рисуем обводку
        arcade.draw_lbwh_rectangle_outline(
            self.x - self.width / 2,
            self.y - self.height / 2,
            self.width, self.height,
            arcade.color.WHITE, 3
        )

        # Рисуем текст
        arcade.draw_text(
            self.text,
            self.x, self.y - 10,
            self.text_color, 24,
            anchor_x="center", anchor_y="center"
        )


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

        # Управление
        self.left_pressed = False
        self.right_pressed = False
        self.space_pressed = False

        # Состояние игры
        self.game_victory = False
        self.game_over = False
        self.round = 1  # Номер раунда

        # Кнопка перезапуска
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
        """Настройка игры"""
        # Создание игрока
        self.player = Player()
        self.player.position = (100, 300)
        self.player_list.append(self.player)

        # Загрузка тайловой карты
        try:
            map_name = "castle.tmx"
            self.tile_map = arcade.load_tilemap(map_name, scaling=TILE_SCALING)

            # Загрузка списков спрайтов из карты
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

            # Создаем тестовую дверь
            door = Door(900, 100)
            self.door_list.append(door)

        # Создание первых 10 монет
        self.spawn_coins(COINS_PER_ROUND)

        print(f"Раунд {self.round}. Монет на уровне: {len(self.coin_list)}")

    def spawn_coins(self, count):
        """Создание монет"""
        for i in range(count):
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            coin = Coin(x, y)
            self.coin_list.append(coin)

    def next_round(self):
        """Переход к следующему раунду"""
        self.round += 1
        self.player.coins = 0  # Сбрасываем монеты текущего раунда
        self.spawn_coins(COINS_PER_ROUND)  # Создаем новые 10 монет
        print(f"Раунд {self.round}! Появились новые монеты!")

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

        # UI - ЖИЗНИ ПО ЦЕНТРУ ЭКРАНА
        # Рисуем фон для жизней
        arcade.draw_lbwh_rectangle_filled(
            SCREEN_WIDTH // 2 - 100,
            SCREEN_HEIGHT - 80,
            200, 40,
            (0, 0, 0, 150)
        )

        # Рисуем жизни в виде сердечек
        lives_text = "❤️ " * self.player.lives
        arcade.draw_text(
            f"Жизни: {lives_text}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60,
            arcade.color.RED, 24,
            anchor_x="center", anchor_y="center"
        )

        # Счетчик монет текущего раунда
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

        # Общее количество монет
        arcade.draw_text(
            f"Всего собрано: {self.player.total_coins}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150,
            arcade.color.WHITE, 18,
            anchor_x="center", anchor_y="center"
        )

        # Номер раунда
        arcade.draw_text(
            f"Раунд: {self.round}",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180,
            arcade.color.CYAN, 18,
            anchor_x="center", anchor_y="center"
        )

        # Подсказка
        if self.player.coins >= COINS_PER_ROUND:
            arcade.draw_lbwh_rectangle_filled(
                SCREEN_WIDTH // 2 - 200,
                SCREEN_HEIGHT - 220,
                400, 40,
                (0, 100, 0, 150)
            )
            arcade.draw_text(
                "✅ Монет достаточно! Идите к двери!",
                SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200,
                arcade.color.GREEN, 20,
                anchor_x="center", anchor_y="center"
            )

        # ЭКРАН ПОБЕДЫ (если набрано 100 монет или больше)
        if self.game_victory:
            # Затемнение фона
            arcade.draw_lbwh_rectangle_filled(
                0, 0,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                (0, 0, 0, 150)
            )

            # Текст победы
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

            # Кнопка перезапуска
            self.restart_button.draw()

        # ЭКРАН ПРОИГРЫША
        elif self.game_over:
            # Затемнение фона
            arcade.draw_lbwh_rectangle_filled(
                0, 0,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                (0, 0, 0, 150)
            )

            # Текст проигрыша
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

            # Кнопка перезапуска
            self.restart_button.draw()

    def on_update(self, delta_time):
        """Обновление"""
        if self.game_victory or self.game_over:
            return

        # Управление
        if self.left_pressed and not self.right_pressed:
            self.player.move_left()
        elif self.right_pressed and not self.left_pressed:
            self.player.move_right()
        else:
            self.player.stop_x()

        # Обновление игрока (применение гравитации)
        self.player.update()

        # Проверка столкновений с платформами
        self.player.update_physics(self.collision_list)

        # Проверка падения за край экрана
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

        # Проверка сбора монет
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

        # Проверка столкновения с дверью
        if self.player.coins >= COINS_PER_ROUND:
            for door in self.door_list:
                if self.player.collides_with_sprite(door):
                    # Переход к следующему раунду
                    self.next_round()
                    break

        # Проверка прыжка
        if self.space_pressed:
            if self.player.jump():
                pass
            self.space_pressed = False

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

    def on_mouse_motion(self, x, y, dx, dy):
        """Обработка движения мыши"""
        if self.game_victory or self.game_over:
            self.restart_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши"""
        if self.game_victory or self.game_over:
            if self.restart_button.check_click(x, y):
                self.restart_game()

    def restart_game(self):
        """Перезапуск игры"""
        print("Перезапуск игры...")

        # Сброс игрока
        self.player.center_x = 100
        self.player.center_y = 300
        self.player.change_x = 0
        self.player.change_y = 0
        self.player.coins = 0
        self.player.total_coins = 0
        self.player.lives = 3

        # Сброс монет
        self.coin_list = arcade.SpriteList()
        self.spawn_coins(COINS_PER_ROUND)

        # Сброс состояния
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
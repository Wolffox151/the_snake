"""Игра «Змейка» с управлением стрелками и переходом через границы."""
from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

DIRECTION_MAP = {
    (pg.K_UP, LEFT): UP,
    (pg.K_UP, RIGHT): UP,
    (pg.K_DOWN, LEFT): DOWN,
    (pg.K_DOWN, RIGHT): DOWN,
    (pg.K_LEFT, UP): LEFT,
    (pg.K_LEFT, DOWN): LEFT,
    (pg.K_RIGHT, UP): RIGHT,
    (pg.K_RIGHT, DOWN): RIGHT,
}
TURN_KEYS = {key for key, direction in DIRECTION_MAP}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый игровой объект с позицией и цветом."""

    def __init__(self, body_color=None) -> None:
        """Задать начальную позицию и цвет объекта."""
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = body_color

    def draw(self):
        """Потребовать реализацию отрисовки в дочернем классе."""
        raise NotImplementedError(
            f'В классе {type(self).__name__} не реализоват метод draw().'
        )

    def draw_cell(self, position):
        """НАрисовать клетку объекта с рамкой."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Объект яблоко."""

    def __init__(self, body_color=APPLE_COLOR, occupied_cells = None) -> None:
        """Задать цвет яблока и выбрать свободную клетку."""
        super().__init__(body_color = body_color)
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells=None):
        """Выбрать случайную свободную клетку для яблока."""
        occupied_cells = set(occupied_cells or ())
        free_cells = [
            (x, y)
            for x in range(0, SCREEN_WIDTH, GRID_SIZE)
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE)
            if (x, y) not in occupied_cells
        ]
        if not free_cells:
            raise ValueError('На поле нет свободных клеток.')

        self.position = choice(free_cells)

    def draw(self):
        """Нарисовать яблоко"""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Объект змейка."""

    def __init__(self, body_color=SNAKE_COLOR) -> None:
        """Создать змейку направленную вправо из одного сегмента."""
        super().__init__(body_color = body_color)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.last = None

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self):
        """Передвинуть змейку на одну клетку с переходом через границы."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_head_position = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head_position)
        self.last = None
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def update_direction(self, next_direction=None):
        """Применить выбранное направление и очистить ожидающий поворот."""
        if next_direction is not None:
            self.direction = next_direction

    def draw(self):
        """Стереть старый хвост и нарисовать все сегменты змейки."""
        if self.last is not None:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

        for position in self.positions:
            self.draw_cell(position)

    def reset(self):
        """Сбросить змейку и выбрать случайное направление."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None


def handle_keys(game_object):
    """Обработать закрытие окна и вернуть выбранное направление."""
    next_direction = None

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        if event.type != pg.KEYDOWN:
            continue

        if event.key == pg.K_ESCAPE:
            pg.quit()
            raise SystemExit

        if event.key in TURN_KEYS:
            next_direction = DIRECTION_MAP.get(
                (event.key, game_object.direction), game_object.direction
            )

    return next_direction


def main():
    """Запустить игровой цикл змейки."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_cells = snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        next_direction = handle_keys(snake)
        snake.update_direction(next_direction)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()


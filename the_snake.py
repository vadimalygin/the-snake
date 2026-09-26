from random import randint

import pygame as pg

# Пользовательские типы данных для координат, направления и цвета
type Cell = tuple[int, int]
type Direction = tuple[int, int]
type Color = tuple[int, int, int, int]

# Константы для размеров поля и сетки:
SCREEN_WIDTH: int = 640
SCREEN_HEIGHT: int = 480
GRID_SIZE: int = 20
GRID_WIDTH: int = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT: int = SCREEN_HEIGHT // GRID_SIZE

# Константы координат ячеек центра и начального положения объектов
CENTER_CELL: Cell = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
INITIAL_GENERAL_CELL: Cell = (0, 0)
INITIAL_SNAKE_CELL: Cell = CENTER_CELL

# Настройки отображения линий сетки
GRID_LINE_WIDTH = 1
SHOW_GRID: bool = True

# Цвета использованные при отрисовке
BOARD_BACKGROUND_COLOR: Color = pg.color.THECOLORS['black']
GRID_LINE_COLOR: Color = pg.color.THECOLORS['gray']
BORDER_COLOR: Color = pg.color.THECOLORS['aquamarine4']
APPLE_COLOR: Color = pg.color.THECOLORS['red']
SNAKE_COLOR: Color = pg.color.THECOLORS['green']

# Направления движения:
UP: Direction = (0, -1)
DOWN: Direction = (0, 1)
LEFT: Direction = (-1, 0)
RIGHT: Direction = (1, 0)

# Скорость движения змейки(игры):
SPEED = 20

# Настройки игрового окна и времени:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Родительский класс всех игровых объектов."""

    def __init__(
        self,
        position: Cell = INITIAL_GENERAL_CELL,
        body_color: Color = BOARD_BACKGROUND_COLOR
    ) -> None:
        self.position = position
        self.body_color = body_color

    def draw(self) -> None:
        """Абстрактный метод отрисовки игрового объекта."""
        raise NotImplementedError(
            f"Метод 'draw' не реализован в классе: {type(self).__name__}"
        )


class Apple(GameObject):
    """Класс яблока."""

    def __init__(
        self,
        occupied_cells: list[Cell],
        position: Cell = INITIAL_GENERAL_CELL,
        body_color: Color = APPLE_COLOR
    ) -> None:
        super().__init__(position, body_color)
        self.randomize_position(occupied_cells)

    def draw(self):
        """Отрисовка яблока на поле."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self, occupied_cells: list[Cell]) -> None:
        """Перемещение яблока на незанятую ячейку."""
        while True:
            x = GRID_SIZE * randint(0, GRID_WIDTH - 1)
            y = GRID_SIZE * randint(0, GRID_HEIGHT - 1)
            if (x, y) not in occupied_cells:
                self.position = (x, y)
                break


class Snake(GameObject):
    """Класс змейки."""

    def __init__(
            self,
            position: Cell = INITIAL_SNAKE_CELL,
            body_color: Color = SNAKE_COLOR
    ) -> None:
        super().__init__(position, body_color)
        self.reset()

    def reset(self) -> None:
        """Сброс змейки в начальное состояние."""
        self.length: int = 1
        self.positions: list[Cell] = [self.position]
        self.direction: Direction = RIGHT
        self.next_direction: Direction | None = None
        self.last: Cell | None = None

    def get_head_position(self) -> Cell:
        """Возвращение текущих координат головы змейки."""
        return self.positions[0]

    def has_collision(self) -> bool:
        """Проверка самопересечения змейки."""
        return self.get_head_position() in self.positions[1:]

    def move(self) -> None:
        """Организация движения змейки."""
        # Вычисление нового положения головы змейки
        self.update_direction()
        dx, dy = self.direction
        old_x, old_y = self.get_head_position()
        new_x = (old_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (old_y + dy * GRID_SIZE) % SCREEN_HEIGHT

        # Добавление новой головы в начало списка и удаление "хвоста"
        self.positions.insert(0, (new_x, new_y))
        if self.has_collision():
            self.reset()
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    # Метод draw класса Snake
    def draw(self):
        """Отрисовка змейки на поле."""
        # Отрисовка тела змейки
        for position in self.positions:
            rect = (pg.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pg.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, head_rect)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    # Метод обновления направления после нажатия на кнопку
    def update_direction(self):
        """Обновление направления движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def check_eaten(snake: Snake, apple: Apple, occupied_cells: list[Cell]):
    """Обновление длины змейки в связи с съеденым яблоком."""
    if apple.position == snake.get_head_position():
        snake.length += 1
        apple.randomize_position(occupied_cells)


# Функция, которая отвечает за отрисовку линий сетки
def draw_lines():
    """Отрисовка линий сетки."""
    # Горизонтальные линии
    for i in range(1, GRID_HEIGHT):
        pg.draw.line(
            screen,
            GRID_LINE_COLOR,
            (0, i * GRID_SIZE),
            (SCREEN_WIDTH, i * GRID_SIZE),
            GRID_LINE_WIDTH
        )

    # Вертикальные линии
    for i in range(1, GRID_WIDTH):
        pg.draw.line(
            screen,
            GRID_LINE_COLOR,
            (i * GRID_SIZE, 0),
            (i * GRID_SIZE, SCREEN_HEIGHT),
            GRID_LINE_WIDTH
        )


# Функция обработки действий пользователя
def handle_keys(game_object: Snake):
    """Обработка нажатия кнопок."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Точка входа."""
    # Инициализация PyGame:
    pg.init()
    # Тут нужно создать экземпляры классов.
    snake: Snake = Snake()
    occupied_cells: list[Cell] = snake.positions
    apple: Apple = Apple(occupied_cells)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)

        # Отрисовка элементов игры
        screen.fill(BOARD_BACKGROUND_COLOR)
        if SHOW_GRID:
            draw_lines()
        snake.draw()
        apple.draw()

        check_eaten(snake, apple, occupied_cells)
        snake.move()
        pg.display.update()


if __name__ == '__main__':
    main()

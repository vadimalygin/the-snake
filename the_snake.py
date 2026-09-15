from random import randint

import pygame

# Пользовательские типы данных для координат, направления и цвета
type Cell = tuple[int, int]
type Direction = tuple[int, int]
type Color = tuple[int, int, int]

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

SHOW_GRID = True

# Толщина линий сетки
LINE_WIDTH = 1

# Направления движения:
UP: Direction = (0, -1)
DOWN: Direction = (0, 1)
LEFT: Direction = (-1, 0)
RIGHT: Direction = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR: Color = (0, 0, 0)

# Цвет линий сетки
LINE_COLOR = (128, 128, 128)

# Цвет границы ячейки
BORDER_COLOR: Color = (93, 216, 228)

# Цвет яблока
APPLE_COLOR: Color = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR: Color = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Родительский класс всех игровых объектов"""

    def __init__(
        self,
        position: Cell = (0, 0),
        body_color: Color = BOARD_BACKGROUND_COLOR
    ) -> None:
        self.position = position
        self.body_color = body_color

    def draw(self) -> None:
        """Абстрактный метод отрисовки игрового объекта"""
        raise NotImplementedError


class Apple(GameObject):
    """Класс яблока"""

    def randomize_position(self, occupied_cells: list[Cell]) -> None:
        """Создание случайных координат в пределах игрового поля"""
        while True:
            x = GRID_SIZE * randint(0, GRID_WIDTH - 1)
            y = GRID_SIZE * randint(0, GRID_HEIGHT - 1)
            if (x, y) not in occupied_cells:
                self.position = (x, y)
                break

    def __init__(
        self,
        position: Cell = (0, 0),
        body_color: Color = APPLE_COLOR
    ) -> None:
        super().__init__(position, body_color)
        self.randomize_position([(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)])

    def draw(self):
        """Отрисовка яблока на поле"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки"""

    def __init__(
            self,
            position: Cell = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            body_color: Color = SNAKE_COLOR
    ) -> None:
        super().__init__(position, body_color)
        self.length: int = 1
        self.positions: list[Cell] = []
        self.positions.append(self.position)
        self.direction: Direction = RIGHT
        self.next_direction: Direction | None = None
        self.last: Cell | None = None

    def reset(self) -> None:
        """Сброс змейки в начальное состояние"""
        self.__init__()

    def get_head_position(self) -> Cell:
        """Текущие координаты головы змейки"""
        return self.positions[0]

    def has_collision(self) -> bool:
        """Проверка самопересечения змейки"""
        return self.get_head_position() in self.positions[1:]

    def move(self) -> None:
        """Организация движения змейки"""
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
        """Отрисовка змейки на поле"""
        # Отрисовка тела змейки
        for position in self.positions:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    # Метод обновления направления после нажатия на кнопку
    def update_direction(self):
        """Обновление направления движения змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None


def check_eaten(snake: Snake, apple: Apple):
    """Обновление длины змейки в связи с съеденым яблоком"""
    if apple.position == snake.get_head_position():
        snake.length += 1
        apple.randomize_position(snake.positions)


# Функция, которая отвечает за отрисовку горизонтальных и вертикальных линий
def draw_lines():
    """Отрисовка линий сетки"""
    # Горизонтальные линии
    for i in range(1, GRID_HEIGHT):
        pygame.draw.line(
            screen,
            LINE_COLOR,
            (0, i * GRID_SIZE),
            (SCREEN_WIDTH, i * GRID_SIZE),
            LINE_WIDTH
        )

    # Вертикальные линии
    for i in range(1, GRID_WIDTH):
        pygame.draw.line(
            screen,
            LINE_COLOR,
            (i * GRID_SIZE, 0),
            (i * GRID_SIZE, SCREEN_HEIGHT),
            LINE_WIDTH
        )


# Функция обработки действий пользователя
def handle_keys(game_object: Snake):
    """Обработка нажатия кнопок"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Точка входа"""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    snake: Snake = Snake()
    apple: Apple = Apple()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)

        # Отрисовка элементов игры
        screen.fill(BOARD_BACKGROUND_COLOR)
        if SHOW_GRID:
            draw_lines()
        snake.draw()
        apple.draw()

        check_eaten(snake, apple)
        snake.move()
        pygame.display.update()


if __name__ == '__main__':
    main()

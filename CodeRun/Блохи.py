from collections import deque


def min_sum_paths(n, m, feed_row, feed_col, fleas):
    # Возможные ходы коня
    knight_moves = [
        (-2, -1),
        (-2, 1),
        (-1, -2),
        (-1, 2),
        (1, -2),
        (1, 2),
        (2, -1),
        (2, 1),
    ]

    # Функция для проверки валидности координат
    def is_valid(row, col):
        return 1 <= row <= n and 1 <= col <= m

    # Функция для поиска кратчайшего пути от кормушки до всех клеток
    def bfs_from_feeder():
        # Расстояния от кормушки до всех клеток (инициализируем -1)
        distances = [[-1 for _ in range(m + 1)] for _ in range(n + 1)]
        distances[feed_row][feed_col] = 0

        queue = deque([(feed_row, feed_col)])

        while queue:
            row, col = queue.popleft()

            for dr, dc in knight_moves:
                new_row, new_col = row + dr, col + dc

                if is_valid(new_row, new_col) and distances[new_row][new_col] == -1:
                    distances[new_row][new_col] = distances[row][col] + 1
                    queue.append((new_row, new_col))

        return distances

    # Получаем расстояния от кормушки до всех клеток
    distances = bfs_from_feeder()

    # Считаем сумму расстояний от блох до кормушки
    total_sum = 0
    for flea_row, flea_col in fleas:
        # Если блоха не может достичь кормушки
        if distances[flea_row][flea_col] == -1:
            return -1

        total_sum += distances[flea_row][flea_col]

    return total_sum


# Считываем входные данные
n, m, feed_row, feed_col, q = map(int, input().split())
fleas = []

for _ in range(q):
    flea_row, flea_col = map(int, input().split())
    fleas.append((flea_row, flea_col))

# Находим и выводим результат
print(min_sum_paths(n, m, feed_row, feed_col, fleas))

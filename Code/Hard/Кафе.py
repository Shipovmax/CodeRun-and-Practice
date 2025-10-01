import sys


def main():
    # Чтение входных данных
    n = int(input())
    costs = [int(input()) for _ in range(n)]

    if n == 0:
        print(0)
        print("0 0")
        return

    # dp[i][j] - минимальная стоимость для i дней с j купонами
    dp = [[float("inf")] * (n + 1) for _ in range(n + 1)]
    # prev[i][j] - хранит предыдущее состояние для восстановления ответа
    prev = [[None] * (n + 1) for _ in range(n + 1)]

    # Начальное состояние: 0 дней, 0 купонов
    dp[0][0] = 0

    # Заполнение таблицы динамического программирования
    for i in range(n):
        for j in range(n + 1):
            if dp[i][j] == float("inf"):
                continue

            # Вариант 1: Платим за обед
            cost = costs[i]
            new_coupons = j + (1 if cost > 100 else 0)
            if new_coupons <= n:
                if dp[i + 1][new_coupons] > dp[i][j] + cost:
                    dp[i + 1][new_coupons] = dp[i][j] + cost
                    prev[i + 1][new_coupons] = (j, False)

            # Вариант 2: Используем купон, если он есть
            if j > 0:
                if dp[i + 1][j - 1] > dp[i][j]:
                    dp[i + 1][j - 1] = dp[i][j]
                    prev[i + 1][j - 1] = (j, True)

    # Находим минимальную стоимость и максимальное количество оставшихся купонов
    min_cost = float("inf")
    max_coupons = 0
    for j in range(n + 1):
        if dp[n][j] < min_cost:
            min_cost = dp[n][j]
            max_coupons = j
        elif dp[n][j] == min_cost and j > max_coupons:
            max_coupons = j

    # Восстановление ответа
    used_days = []
    coupons_left = max_coupons
    i = n
    used_coupons = 0

    while i > 0:
        prev_coupons, used = prev[i][coupons_left]
        if used:
            used_days.append(i)
            used_coupons += 1
            coupons_left += 1
        else:
            coupons_left -= 1 if costs[i - 1] > 100 else 0
        i -= 1

    # Вывод результатов
    print(min_cost)
    print(f"{max_coupons} {used_coupons}")
    for day in sorted(used_days):
        print(day)
    pass


if __name__ == "__main__":
    main()

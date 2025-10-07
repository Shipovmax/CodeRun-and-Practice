def levenshtein_distance(s1, s2):
    # Создаем таблицу для динамического программирования
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Инициализация первой строки и столбца
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    # Заполняем таблицу
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1

            # Находим минимум из трех операций
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # удаление
                dp[i][j - 1] + 1,  # вставка
                dp[i - 1][j - 1] + cost,  # замена или совпадение
            )

    return dp[m][n]


s1 = input().strip()
s2 = input().strip()

print(levenshtein_distance(s1, s2))

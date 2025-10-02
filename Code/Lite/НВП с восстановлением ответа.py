def main():

    # Функция по нахождению НВП с восстановлением ответа
    def longest_increasing_subsequence(arr):
        n = len(arr)
        matrix = [1] * n
        prev = [-1] * n
        for i in range(1, n):
            for j in range(i):
                if arr[j] < arr[i] and matrix[j] + 1 > matrix[i]:
                    matrix[i] = matrix[j] + 1
                    prev[i] = j

        # Находим индекс последнего элемента НВП
        last_index = matrix.index(max(matrix))

        # Восстанавливаем НВП
        lis = []
        while last_index != -1:
            lis.append(arr[last_index])
            last_index = prev[last_index]

        # Разворачиваем, так как построили с конца
        return lis[::-1]

    # Чтение входных данных
    n = int(input())
    sequence = list(map(int, input().split()))

    # Находим НВП и вывод результата
    print(" ".join(map(str, longest_increasing_subsequence(sequence))))


if __name__ == "__main__":
    main()

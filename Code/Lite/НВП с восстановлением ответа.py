def main():

    def longest_increasing_subsequence(arr):
        n = len(arr)
        matrix = [1] * n
        prev = [-1] * n
        for i in range(1, n):
            for j in range(i):
                if arr[j] < arr[i] and matrix[j] + 1 > matrix[i]:
                    matrix[i] = matrix[j] + 1
                    prev[i] = j

        last_index = matrix.index(max(matrix))

        lis = []
        while last_index != -1:
            lis.append(arr[last_index])
            last_index = prev[last_index]

        return lis[::-1]

    n = int(input())
    sequence = list(map(int, input().split()))

    print(" ".join(map(str, longest_increasing_subsequence(sequence))))


if __name__ == "__main__":
    main()

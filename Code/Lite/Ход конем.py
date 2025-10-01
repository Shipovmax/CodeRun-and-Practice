import sys
import math


def main():

    N, M = map(int, input().split())

    routes = [0] * N * M
    routes[0] = 1
    if N * M == 1:
        print(1)
    elif (N == 1) or (M == 1):
        print(0)
    else:
        if M >= 3:
            routes[M + 2] = 1
        if N >= 3:
            routes[2 * M + 1] = 1

        for i in range(2, M):
            for j in range(2, N):
                q = M * j + i
                routes[q] = routes[q - (2 * M + 1)] + routes[q - M - 2]

        print(int(routes[-1]))


if __name__ == "__main__":
    main()

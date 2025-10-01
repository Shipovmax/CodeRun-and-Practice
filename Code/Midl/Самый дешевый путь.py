import sys

N, M = map(int, input().split())
L = [list(map(int, input().split())) for i in range(N)]
for n in range(1, N):
    L[n][0] += L[n - 1][0]
for m in range(1, M):
    L[0][m] += L[0][m - 1]
for n in range(1, N):
    for m in range(1, M):
        L[n][m] = min(L[n - 1][m], L[n][m - 1]) + L[n][m]
print(L[-1][-1])

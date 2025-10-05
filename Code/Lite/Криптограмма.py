from collections import Counter
from itertools import combinations


primes = []
N = 2 * 10**5 + 1
sieve = [1] * N
sieve[0] = 0
sieve[1] = 0

i = 2
while i < N:
    if sieve[i]:
        primes.append(i)
        j = i + i
        while j < N:
            sieve[j] = 0
            j += i
    i += 1


def get_primes(x):
    if sieve[x]:
        return [x]

    r = []

    for prime in primes:
        if x % prime == 0:
            r.append(prime)
            while x % prime == 0:
                x //= prime

        if prime * prime > x or sieve[x]:
            break

    if x != 1:
        r.append(x)

    return r


def solution():
    for _ in range(int(input())):
        n, k = map(int, input().split())
        a = list(map(int, input().split()))

        b = []
        for i in a:
            if i % k == 0:
                b.append(i // k)

        counter = Counter(b)
        c = [0] * (n + 1)
        answer = 0
        for i in counter:
            if i == 1:
                answer += (len(b) - 1) * counter[i]
                continue
            answer += len(b) * counter[i]

            t = get_primes(i)
            for count in range(1, len(t) + 1):
                for var in combinations(t, count):
                    div = 1
                    for prime in var:
                        div *= prime

                    if count % 2 == 0:
                        c[div] += 1 * counter[i]

                    else:
                        c[div] -= 1 * counter[i]

        for i in c:
            if i < 0:
                answer -= i * i

            else:
                answer += i * i

        print(answer // 2)

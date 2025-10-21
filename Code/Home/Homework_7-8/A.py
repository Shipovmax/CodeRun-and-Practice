import sys


def main():
    data = sys.stdin.read().splitlines()
    if not data:
        print(0)
        return

    n = int(data[0])
    A = []
    index = 1
    for i in range(n):
        s = data[index]
        index += 1
        parts = s.split('-')
        start_str = parts[0].strip()
        end_str = parts[1].strip()
        start_minutes = int(start_str[:2]) * 60 + int(start_str[3:])
        end_minutes = int(end_str[:2]) * 60 + int(end_str[3:])
        A.append((start_minutes, end_minutes))

    m = int(data[index])
    index += 1
    B = []
    for i in range(m):
        s = data[index]
        index += 1
        parts = s.split('-')
        start_str = parts[0].strip()
        end_str = parts[1].strip()
        start_minutes = int(start_str[:2]) * 60 + int(start_str[3:])
        end_minutes = int(end_str[:2]) * 60 + int(end_str[3:])
        B.append((start_minutes, end_minutes))

    A_sorted_by_arrival = sorted(A, key=lambda x: x[1])
    B_sorted_by_departure = sorted(B, key=lambda x: x[0])

    matching1 = 0
    i1, j1 = 0, 0
    while i1 < len(A_sorted_by_arrival) and j1 < len(B_sorted_by_departure):
        if A_sorted_by_arrival[i1][1] <= B_sorted_by_departure[j1][0]:
            matching1 += 1
            i1 += 1
            j1 += 1
        else:
            j1 += 1

    B_sorted_by_arrival = sorted(B, key=lambda x: x[1])
    A_sorted_by_departure = sorted(A, key=lambda x: x[0])

    matching2 = 0
    i2, j2 = 0, 0
    while i2 < len(B_sorted_by_arrival) and j2 < len(A_sorted_by_departure):
        if B_sorted_by_arrival[i2][1] <= A_sorted_by_departure[j2][0]:
            matching2 += 1
            i2 += 1
            j2 += 1
        else:
            j2 += 1

    total_buses = (n + m) - (matching1 + matching2)
    print(total_buses)


if __name__ == "__main__":
    main()

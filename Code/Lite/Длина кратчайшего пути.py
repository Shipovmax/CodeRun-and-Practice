def matr_to_dict(n: int) -> dict:
    data = {}
    for row in range(1, n + 1):
        data[row] = [
            index + 1
            for index, element in enumerate(input().split(" "))
            if element == "1"
        ]
    return data


def generate_all_ways(matrix, start_list, b):
    ways_list, is_added = [], False
    for variant in start_list:
        if variant[-1] == b:
            return len(variant) - 1
        for road in matrix[variant[-1]]:
            copy_var = variant.copy()
            if road not in variant:
                copy_var.append(road)
                ways_list.append(copy_var)
                is_added = True
    if is_added:
        return generate_all_ways(matrix, ways_list, b)
    return -1


def main():
    n = int(input())
    matrix = matr_to_dict(n)
    A, B = map(int, input().split())
    res = generate_all_ways(matrix, [[A]], B)
    print(res)


if __name__ == "__main__":
    main()

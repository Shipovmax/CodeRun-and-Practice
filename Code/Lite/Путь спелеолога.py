import sys


def main():
    n = int(input())
    height_d = []
    wave_front = None
    for height in range(n):
        input()
        width_d = []
        for width in range(n):
            length_d = []
            for length, symbol in enumerate(input()):
                if symbol == "#":
                    length_d.append(False)
                elif symbol == ".":
                    length_d.append(True)
                else:
                    if height == 0:
                        print(0)
                        sys.exit()
                    length_d.append(False)
                    wave_front = [(height, width, length)]
            width_d.append(length_d)
        height_d.append(width_d)
    steps = 0
    while True:
        new_wave_front = []
        steps += 1
        for h, w, l in wave_front:
            if h > 0 and height_d[h - 1][w][l]:
                if h == 1:
                    print(steps)
                    sys.exit()
                height_d[h - 1][w][l] = False
                new_wave_front.append((h - 1, w, l))
            if h < n - 1 and height_d[h + 1][w][l]:
                height_d[h + 1][w][l] = False
                new_wave_front.append((h + 1, w, l))

            if w > 0 and height_d[h][w - 1][l]:
                height_d[h][w - 1][l] = False
                new_wave_front.append((h, w - 1, l))
            if w < n - 1 and height_d[h][w + 1][l]:
                height_d[h][w + 1][l] = False
                new_wave_front.append((h, w + 1, l))

            if l > 0 and height_d[h][w][l - 1]:
                height_d[h][w][l - 1] = False
                new_wave_front.append((h, w, l - 1))
            if l < n - 1 and height_d[h][w][l + 1]:
                height_d[h][w][l + 1] = False
                new_wave_front.append((h, w, l + 1))

        wave_front = new_wave_front


if __name__ == "__main__":
    main()

import sys


def main():
    n = input()
    p = [int(i) for i in n.split(" ")]
    print(sorted(p)[1])


if __name__ == "__main__":
    main()

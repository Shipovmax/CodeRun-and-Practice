import sys


def main():
    i_to_direction = {0: "N", 1: "S", 2: "W", 3: "E", 4: "U", 5: "D"}
    direction_to_i = {"N": 0, "S": 1, "W": 2, "E": 3, "U": 4, "D": 5}
    processor = {
        "N": input(),
        "S": input(),
        "W": input(),
        "E": input(),
        "U": input(),
        "D": input(),
    }
    dp = [[0 for i in range(101)] for j in range(6)]
    for i in range(6):
        dp[i][1] = 1
    for j in range(2, 101):
        for i in range(6):
            cur_direction = i_to_direction[i]
            cur_cmd = processor[cur_direction]
            summ = 1
            for direction in cur_cmd:
                summ += dp[direction_to_i[direction]][j - 1]
            dp[i][j] = summ

    cmd_to_execute = input().split(" ")
    print(dp[direction_to_i[cmd_to_execute[0]]][int(cmd_to_execute[1])])


if __name__ == "__main__":
    main()

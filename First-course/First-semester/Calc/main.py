"""
Библиотеки
"""

import math
from fractions import Fraction
from decimal import Decimal, getcontext, ROUND_HALF_UP
import re
import os

getcontext().prec = 15  # Устанавливаю 15 знаков после запитой во всем файле


"""
    Цвета для терминала
"""


class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


"""
    Инициализирую все числа от 0 до 99
"""

number_words = {
    "ноль": 0,
    "один": 1,
    "два": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "девять": 9,
    "десять": 10,
    "одиннадцать": 11,
    "двенадцать": 12,
    "тринадцать": 13,
    "четырнадцать": 14,
    "пятнадцать": 15,
    "шестнадцать": 16,
    "семнадцать": 17,
    "восемнадцать": 18,
    "девятнадцать": 19,
    "двадцать": 20,
    "тридцать": 30,
    "сорок": 40,
    "пятьдесят": 50,
    "шестьдесят": 60,
    "семьдесят": 70,
    "восемьдесят": 80,
    "девяносто": 90,
}


"""
    Инициализирую степени от 2 до 20
"""

fraction_words = {
    "вторая": 2,
    "третья": 3,
    "четвертая": 4,
    "пятая": 5,
    "шестая": 6,
    "седьмая": 7,
    "восьмая": 8,
    "девятая": 9,
    "десятая": 10,
    "одиннадцатая": 11,
    "двенадцатая": 12,
    "тринадцатая": 13,
    "четырнадцатая": 14,
    "пятнадцатая": 15,
    "шестнадцатая": 16,
    "семнадцатая": 17,
    "восемнадцатая": 18,
    "девятнадцатая": 19,
    "двадцатая": 20,
}


"""
    Инициализирую математические функции
"""

operators = {
    "плюс": "+",
    "минус": "-",
    "умножить": "*",
    "разделить": "/",
    "остаток": "%",
    "в степени": "**",
    "синус": "sin",
    "косинус": "cos",
    "тангенс": "tan",
    "размещений": "perm",
    "сочетаний": "comb",
    "перестановок": "fact",
}


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def text_to_number(text):
    text = text.lower().replace("-", " ").replace(" и ", " ").split()
    number = 0
    negative = False
    frac = None
    for word in text:
        if word == "минус":
            negative = True
        elif word in number_words:
            number += number_words[word]
        elif word in fraction_words:
            frac = Fraction(1, fraction_words[word])
    if frac:
        number = Fraction(number) + frac
    if negative:
        number = -number
    return number


def number_to_text(number):
    if isinstance(number, Fraction):
        number = number.limit_denominator()
        whole = number.numerator // number.denominator
        frac = Fraction(number.numerator % number.denominator, number.denominator)
        result = ""
        if whole:
            result += number_to_text_simple(whole) + " и "
        if frac:
            result += (
                number_to_text_simple(frac.numerator)
                + " "
                + ordinal_from_denominator(frac.denominator)
            )
        return result or "ноль"
    if isinstance(number, float):
        s = str(Decimal(number).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP))
        if "." in s:
            int_part, dec_part = s.split(".")
            period = detect_period(dec_part)
            result = number_to_text_simple(int(int_part))
            if dec_part and int(dec_part) > 0:
                dec_text = " ".join([number_to_text_simple(int(d)) for d in dec_part])
                result += " и " + dec_text
                if period:
                    result += f" в периоде {period}"
            return result
        else:
            return number_to_text_simple(int(number))
    return number_to_text_simple(int(number))


def detect_period(decimal_str):
    for l in range(1, 5):
        seq = decimal_str[:l]
        repeated = seq * (len(decimal_str) // l + 1)
        if repeated.startswith(decimal_str):
            return " ".join([number_to_text_simple(int(c)) for c in seq])
    return ""


def number_to_text_simple(n):
    if n == 0:
        return "ноль"
    for k, v in sorted(number_words.items(), key=lambda x: x[1], reverse=True):
        if n >= v:
            rem = n - v
            if rem == 0:
                return k
            else:
                return k + " " + number_to_text_simple(rem)
    return ""


def ordinal_from_denominator(d):
    for k, v in fraction_words.items():
        if v == d:
            return k
    return ""


def calc(expression):
    expression = (
        expression.lower()
        .replace("скобка открывается", "(")
        .replace("скобка закрывается", ")")
    )
    for word, op in operators.items():
        expression = expression.replace(word, op)
    tokens = expression.split()
    for i, tok in enumerate(tokens):
        if tok.isalpha():
            val = text_to_number(tok)
            tokens[i] = (
                f"Fraction({val})" if isinstance(val, Fraction) else str(float(val))
            )
    expr = " ".join(tokens)
    try:
        result = eval(
            expr,
            {
                "__builtins__": None,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "pi": math.pi,
                "Fraction": Fraction,
                "perm": math.perm,
                "comb": math.comb,
                "fact": math.factorial,
            },
        )
    except Exception as e:
        return f"{Colors.RED}Ошибка: {e}{Colors.END}"
    if isinstance(result, Fraction) and result.denominator > 1000000:
        result = float(result)
    return number_to_text(result)


def print_header():
    print(f"{Colors.BOLD}{Colors.PURPLE}")
    print("=" * 50)
    print("🔥 ТЕКСТОВЫЙ КАЛЬКУЛЯТОР 🔥")
    print("=" * 50)
    print(f"{Colors.END}")


def main():
    clear_screen()
    print_header()
    print(
        f"{Colors.CYAN}Введите выражение (например: 'двадцать пять плюс тринадцать'):{Colors.END}"
    )
    expr = input("> ").strip()
    result = calc(expr)
    print(f"{Colors.GREEN}Результат: {result}{Colors.END}")


if __name__ == "__main__":
    main()

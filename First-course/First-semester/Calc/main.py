# -*- coding: utf-8 -*-
"""
calc.py — единый текстовый калькулятор (всё в одном файле)
Поддерживает:
 - числа, записанные словами (целые, смешанные дроби, десятичные "и ... сотых/тысячных")
 - операции: плюс, минус, умножить, разделить, остаток от деления, в степени
 - приоритет операций и скобки (словами "скобка открывается", "скобка закрывается")
 - унарный минус (например: "пять минус минус один")
 - дроби (правильные и смешанные), сокращение дробей
 - формат вывода: целые, "и X сотых/тысячных", смешанные дроби, периодическая десятичная дробь
 - тригонометрические функции: синус, косинус, тангенс, константа пи
 - комбинаторика: перестановки, размещения, сочетания (фразы: "перестановок из N",
   "размещений из N по K", "сочетаний из N по K")
 - диагностика ошибок: неизвестные слова, синтаксические ошибки, деление на ноль, скобки

Главная функция:
    calc(expr: str) -> str

Пример использования (внешний):
    from calc import calc
    print(calc("скобка открывается пять плюс два скобка закрывается умножить на три минус один"))
"""

from __future__ import annotations
import re
from fractions import Fraction
from math import sin, cos, tan, pi, factorial
from typing import List, Tuple, Union, Optional

# ---------- Словари для преобразования слов <-> числа (русский) ----------
# Базовые числа
SIMPLE_NUM = {
    "ноль": 0,
    "один": 1,
    "одна": 1,
    "два": 2,
    "две": 2,
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
}
TENS = {
    "двадцать": 20,
    "тридцать": 30,
    "сорок": 40,
    "пятьдесят": 50,
    "шестьдесят": 60,
    "семьдесят": 70,
    "восемьдесят": 80,
    "девяносто": 90,
}
HUNDREDS = {
    "сто": 100,
    "двести": 200,
    "триста": 300,
    "четыреста": 400,
    "пятьсот": 500,
    "шестьсот": 600,
    "семьсот": 700,
    "восемьсот": 800,
    "девятьсот": 900,
}
# Разряды (тысячи, миллионы) — частичная поддержка (до миллионов)
SCALES = {
    "тысяча": 10 ** 3,
    "тысячи": 10 ** 3,
    "тысяч": 10 ** 3,
    "миллион": 10 ** 6,
    "миллиона": 10 ** 6,
    "миллионов": 10 ** 6,
}

# Сопоставления для именования разрядов десятичной дроби
DECIMAL_DENOMINATORS = {
    "сотая": 100,
    "сотых": 100,
    "сотые": 100,
    "тысячная": 1000,
    "тысячных": 1000,
    "тысячные": 1000,
}

# Операторы (фразы) — все в нижнем регистре
OPERATORS = {
    "плюс": {"symbol": "+", "precedence": 1, "assoc": "left"},
    "минус": {"symbol": "-", "precedence": 1, "assoc": "left"},
    "умножить": {"symbol": "*", "precedence": 2, "assoc": "left"},
    "разделить": {"symbol": "/", "precedence": 2, "assoc": "left"},
    "остаток от деления": {"symbol": "%", "precedence": 2, "assoc": "left"},
    "в степени": {"symbol": "^", "precedence": 3, "assoc": "right"},
}

# Функции (в виде ключевых слов)
FUNCTIONS = {"синус", "косинус", "тангенс"}
# Комбинаторные операции — будем распознавать по фразам
COMBINATORICS = {"перестановок", "размещений", "сочетаний"}

# Скобки — словесные формы
OPEN_PAREN = ("скобка открывается",)
CLOSE_PAREN = ("скобка закрывается",)

# Регулярные шаблоны для токенизации фраз
# Важно: порядок фраз имеет значение — более длинные фразы сначала
PHRASE_TOKENS = [
    "остаток от деления",
    "скобка открывается",
    "скобка закрывается",
    "в степени",
    "синус от",
    "косинус от",
    "тангенс от",
    "перестановок из",
    "размещений из",
    "сочетаний из",
    "плюс",
    "минус",
    "умножить",
    "разделить",
]


# ---------- Исключения / классы ошибок ----------
class CalcError(Exception):
    """Базовая ошибка калькулятора — для диагностики пользователю"""

    pass


class ParseError(CalcError):
    pass


class MathError(CalcError):
    pass


# ---------- Утилиты по работе с дробями и форматом вывода ----------
def fraction_to_decimal_with_period(
        fr: Fraction, max_nonrepeat: int = 10, max_period: int = 6
) -> Tuple[str, Optional[str]]:
    """
    Переводим дробь в десятичную запись с выделением периодической части.
    Возвращаем (non_repeating_part, repeating_part_or_None).
    non_repeating_part включает целую и неповторяющуюся дробную часть, например "0.125"
    repeating_part — строка повторяющейся последовательности без точки, или None.
    Реализовано через симуляцию деления (long division), фиксируем позиции остатков.
    """
    # Анализируем знак
    sign = "-" if fr < 0 else ""
    fr = abs(fr)

    integer_part = fr.numerator // fr.denominator
    remainder = fr.numerator % fr.denominator

    if remainder == 0:
        return f"{sign}{integer_part}", None

    # Выполняем деление в школе и отслеживаем остатков
    remainder_positions = {}
    decimals = []
    pos = 0
    repeating_start = None

    while remainder != 0 and pos < (max_nonrepeat + max_period + 5):
        if remainder in remainder_positions:
            repeating_start = remainder_positions[remainder]
            break
        remainder_positions[remainder] = pos
        remainder *= 10
        digit = remainder // fr.denominator
        decimals.append(str(digit))
        remainder %= fr.denominator
        pos += 1

    # Формируем части
    if repeating_start is None:
        # нет периода в исследуемой длине — просто вернём неповторяющуюся дробь
        dec_str = "".join(decimals)
        return f"{sign}{integer_part}.{dec_str}", None
    else:
        nonrep = "".join(decimals[:repeating_start])
        rep = "".join(decimals[repeating_start:])
        return (
            f"{sign}{integer_part}.{nonrep}" if nonrep else f"{sign}{integer_part}",
            rep,
        )


def fraction_to_mixed_and_words(fr: Fraction) -> str:
    """
    Преобразует Fraction в человеко-читаемый текст:
     - если целое, возвращает слово-целое
     - если дробь со знаменателем 100 или 1000, возвращает 'и X сотых/тысячных'
     - если дробь может быть выражена как смешанная дробь — формат 'целая и числитель знаменатель'
     - если дробь не имеет удобной дробной формы, пытается найти период и вывести 'целая и <непериод> и <период> в периоде'
    Возвращает строку на русском.
    """
    # Сохраняем знак
    sign_prefix = ""
    if fr < 0:
        sign_prefix = "минус "
        fr = abs(fr)

    # Целая часть
    целая = fr.numerator // fr.denominator
    дробь = Fraction(fr.numerator % fr.denominator, fr.denominator)

    parts = []
    if целая != 0:
        parts.append(int_to_words(целая))

    if дробь == 0:
        return (sign_prefix + parts[0]) if parts else sign_prefix + "ноль"

    # Сначала пробуем специальные разряды: сотые/тысячные/миллионные (100,1000,1000000)
    for denom_word, denom_value in [
        (100, "сотых"),
        (1000, "тысячных"),
        (10 ** 6, "миллионных"),
    ]:
        if дробь.denominator == denom_value if False else False:
            pass  # (не используется) -- оставлено для логики ниже

    # Если знаменатель делится на 2^a * 5^b => конечная десятичная дробь
    # попробуем представить в виде сотых/тысячных/миллионных (до 1e6)
    dec = None
    if is_terminating_decimal(fr):
        # представим десятичную дробь с достаточной точностью (до 6 знаков)
        dec_str, period = fraction_to_decimal_with_period(
            fr, max_nonrepeat=10, max_period=6
        )
        # dec_str выглядит как 'целая.дробь' или 'целая'
        if period is None:
            # разберём дробную часть
            if "." in dec_str:
                int_part_str, frac_part_str = dec_str.split(".", 1)
                # пробуем представить как сотые/тысячные/миллионные
                length = len(frac_part_str)
                numerator = int(frac_part_str)
                if length in (2, 3, 6):
                    denom_map = {2: "сотых", 3: "тысячных", 6: "миллионных"}
                    denom_word = denom_map[length]
                    # убираем ведущие нули при чтении числа (например "05" -> "пять")
                    num_words = int_to_words(numerator)
                    if int(int_part_str) == 0:
                        return f"{sign_prefix}ноль и {num_words} {denom_word}"
                    else:
                        return f"{sign_prefix}{int_to_words(int(int_part_str))} и {num_words} {denom_word}"
                else:
                    # не специальный разряд — выводим как 'целая.дробь' словами цифр
                    # попытаемся округлить до тысячных по заданию основной: округление до 3 знаков
                    rounded_frac = round(float(fr - int(fr)), 3)
                    # если rounding makes fraction 0 or whole, re-evaluate
                    rounded_frac_frac = Fraction(
                        str(round(fr - int(fr), 3))
                    ).limit_denominator()
                    if rounded_frac_frac == 0:
                        return f"{sign_prefix}{int_to_words(int(fr))}"
                    # иначе — вывести как "и X сотых/тысячных" если попадает
                    # попытаемся представить в сотых/тысячных
                    denom_try = {2: "сотых", 3: "тысячных"}
                    for l, word in denom_try.items():
                        numerator_try = int(round(fr - int(fr), l) * (10 ** l))
                        if abs(
                                (Fraction(numerator_try, 10 ** l) - (fr - int(fr)))
                        ) < Fraction(1, 10 ** l):
                            if int(fr) == 0:
                                return f"{sign_prefix}ноль и {int_to_words(numerator_try)} {word}"
                            else:
                                return f"{sign_prefix}{int_to_words(int(fr))} и {int_to_words(numerator_try)} {word}"
                    # fallback to decimal with words for digits
                    return sign_prefix + decimal_numeric_to_words(fr)
            else:
                return sign_prefix + int_to_words(int(dec_str))
        else:
            # есть период — хотим вывести как "целая и непериод и период в периоде"
            nonrep = dec_str.split(".", 1)[1] if "." in dec_str else ""
            if nonrep == "":
                nonrep_words = "ноль"
            else:
                nonrep_words = int_to_words(int(nonrep)) if nonrep != "" else "ноль"
            period_words = digits_to_words(period)
            if int(целая) == 0:
                return f"{sign_prefix}ноль и {nonrep_words} и {period_words} в периоде"
            else:
                return f"{sign_prefix}{int_to_words(целая)} и {nonrep_words} и {period_words} в периоде"
    else:
        # непериодическая бесконечная десятичная — будем пытаться обнаружить период (общий случай)
        dec_str, period = fraction_to_decimal_with_period(
            fr, max_nonrepeat=10, max_period=6
        )
        if period:
            # конвертируем в требуемую форму (ограничиваем период до 4 знаков в выводе)
            period_trimmed = period[:4]
            nonrep = dec_str.split(".", 1)[1] if "." in dec_str else ""
            nonrep_words = int_to_words(int(nonrep)) if nonrep else "ноль"
            period_words = digits_to_words(period_trimmed)
            if целая == 0:
                return f"{sign_prefix}ноль и {nonrep_words} и {period_words} в периоде"
            else:
                return f"{sign_prefix}{int_to_words(целая)} и {nonrep_words} и {period_words} в периоде"

    # Если дошли сюда — представим как смешанную дробь (целая и числитель/знаменатель)
    числитель = дробь.numerator
    знаменатель = дробь.denominator
    сокращенная = Fraction(числитель, знаменатель)  # уже сокращено
    if целая == 0:
        return f"{sign_prefix}{fraction_to_words(сокращенная)}"
    else:
        return f"{sign_prefix}{int_to_words(целая)} и {fraction_to_words(сокращенная)}"


def decimal_numeric_to_words(fr: Fraction) -> str:
    """
    Преобразует дробь в вид 'целая и X сотых/тысячных' если возможно, иначе в 'целая дробь' словами.
    Это fallback при сложных ситуациях.
    """
    # попробуем округлить до тысячных и вывести
    val = float(fr)
    integer_part = int(val)
    frac_part = round(val - integer_part, 3)
    if frac_part == 0:
        return int_to_words(integer_part)
    digits3 = int(round(frac_part * 1000))
    if integer_part == 0:
        return f"ноль и {int_to_words(digits3)} тысячных"
    else:
        return f"{int_to_words(integer_part)} и {int_to_words(digits3)} тысячных"


def is_terminating_decimal(fr: Fraction) -> bool:
    """Проверяет, является ли дробь конечной десятичной (знаменатель содержит только 2 и 5)"""
    d = fr.denominator
    while d % 2 == 0:
        d //= 2
    while d % 5 == 0:
        d //= 5
    return d == 1


def digits_to_words(digits: str) -> str:
    """
    Преобразует строку цифр '023' в словесное представление чисел как целое число:
    'ноль два три' -> но для читаемости вернём как число словами: 23 -> 'двадцать три'
    Здесь мы интерпретируем строку как число без ведущих нулей.
    """
    if digits == "":
        return "ноль"
    num = int(digits)
    return int_to_words(num)


def fraction_to_words(fr: Fraction) -> str:
    """
    Преобразует простую дробь (числитель/знаменатель, правильную) в текст:
    'три четвертых' и т.п. (знаменатели читаются как порядковые: 2->вторых/вторая, 3->третьих...)
    — упрощённая реализация: вернёт 'числитель знаменатель-словом' (напр. 'одна третья' или 'одна третьих')
    Для корректного морфологического согласования нужно больше логики — здесь упрощённо вернём 'числитель знаменатель-ых'
    """
    num = fr.numerator
    den = fr.denominator
    den_word = f"{ordinal_name_for_denominator(den)}"
    return f"{int_to_words(num)} {den_word}"


def ordinal_name_for_denominator(den: int) -> str:
    """
    Возвращает слово-форму для знаменателя в родительном/мн.ч. ('третьих', 'пятых').
    Это упрощение: для 2,3,4 используем особые формы, иначе общая 'х-ых'.
    """
    if den == 2:
        return "вторых"
    if den == 3:
        return "третьих"
    if den == 4:
        return "четвертых"
    if den == 5:
        return "пятых"
    if den == 7:
        return "седьмых"
    if den == 9:
        return "девятых"
    # общая форма
    return f"{int_to_words(den)}-ых"


# ---------- Преобразование целого числа в слова (русский) ----------
# Поддержка до миллионов (потребуется для вывода больших результатов)
ONES = {
    0: "ноль",
    1: "один",
    2: "два",
    3: "три",
    4: "четыре",
    5: "пять",
    6: "шесть",
    7: "семь",
    8: "восемь",
    9: "девять",
    10: "десять",
    11: "одиннадцать",
    12: "двенадцать",
    13: "тринадцать",
    14: "четырнадцать",
    15: "пятнадцать",
    16: "шестнадцать",
    17: "семнадцать",
    18: "восемнадцать",
    19: "девятнадцать",
}
TENS_WORDS = {
    20: "двадцать",
    30: "тридцать",
    40: "сорок",
    50: "пятьдесят",
    60: "шестьдесят",
    70: "семьдесят",
    80: "восемьдесят",
    90: "девяносто",
}
HUND_WORDS = {
    100: "сто",
    200: "двести",
    300: "триста",
    400: "четыреста",
    500: "пятьсот",
    600: "шестьсот",
    700: "семьсот",
    800: "восемьсот",
    900: "девятьсот",
}


def int_to_words(n: int) -> str:
    """Преобразует неотрицательное целое число (до 999999) в русские слова."""
    if n == 0:
        return "ноль"
    if n < 0:
        return "минус " + int_to_words(-n)
    parts = []
    if n >= 10 ** 6:
        millions = n // 10 ** 6
        parts.append(
            int_to_words(millions)
            + " миллион"
            + ("ов" if millions % 10 != 1 or millions % 100 == 11 else "")
        )
        n %= 10 ** 6
    if n >= 1000:
        thousands = n // 1000
        parts.append(_hundreds_to_words(thousands) + " " + _plural_thousand(thousands))
        n %= 1000
    if n > 0:
        parts.append(_hundreds_to_words(n))
    return " ".join([p for p in parts if p]).strip()


def _plural_thousand(n: int) -> str:
    """Правильное окончание для тысячи (упрощённо)"""
    if 11 <= (n % 100) <= 14:
        return "тысяч"
    last = n % 10
    if last == 1:
        return "тысяча"
    if 2 <= last <= 4:
        return "тысячи"
    return "тысяч"


def _hundreds_to_words(n: int) -> str:
    """Число до 999 в слова"""
    parts = []
    if n >= 100:
        h = (n // 100) * 100
        parts.append(HUND_WORDS.get(h, ""))
        n %= 100
    if n >= 20:
        t = (n // 10) * 10
        parts.append(TENS_WORDS.get(t, ""))
        n %= 10
    if n > 0:
        parts.append(ONES.get(n, ""))
    return " ".join([p for p in parts if p]).strip()


# ---------- Парсер слов в число ----------
def parse_simple_number_words(
        tokens: List[str], start_index: int = 0
) -> Tuple[int, int]:
    """
    Парсит последовательность слов, представляющих целое число (включая сотни, тысячи, миллионы).
    Возвращает (значение, индекс_последнего_слова_в_последовательности).
    Бросает ParseError при неизвестных словах.
    """
    i = start_index
    total = 0
    current = 0
    consumed = 0
    length = len(tokens)
    while i < length:
        w = tokens[i]
        if w in SIMPLE_NUM:
            current += SIMPLE_NUM[w]
            i += 1
            consumed += 1
        elif w in TENS:
            current += TENS[w]
            i += 1
            consumed += 1
        elif w in HUNDREDS:
            current += HUNDREDS[w]
            i += 1
            consumed += 1
        elif w in SCALES:
            scale = SCALES[w]
            if current == 0:
                current = 1
            total += current * scale
            current = 0
            i += 1
            consumed += 1
        else:
            break
    total += current
    if consumed == 0:
        raise ParseError(f"Ожидалось число, но найдено: '{tokens[start_index]}'")
    return total, start_index + consumed - 1


def parse_fractional_descriptor(
        tokens: List[str], start_index: int
) -> Tuple[Fraction, int]:
    """
    Парсит дробную часть, начиная с индекс start_index.
    Возможные формы:
      - "тридцать одна сотая" -> numerator words + denom-word (сотая/тысячная)
      - "четыре пятых" -> числитель + порядковое слово (производит Fraction)
    Также поддерживает форму "одна вторая" и т.п.
    Возвращает (Fraction, last_index).
    Бросает ParseError при некорректности.
    """
    # Попытаемся найти число (числитель)
    num, idx_num_end = parse_simple_number_words(tokens, start_index)
    # следующий токен — ожидаемо слово-разряд (сотая/тысячная) или форма 'третий/третьих' (упрощённо — мы ищем слово "сотая" или "тысячная" или любое слово, не число)
    next_idx = idx_num_end + 1
    if next_idx >= len(tokens):
        raise ParseError(
            "Ожидается слово-разряд (сотая/тысячная) после числителя дроби"
        )
    denom_word = tokens[next_idx]
    # Если это стандартная десятичная разрядность
    if denom_word in DECIMAL_DENOMINATORS:
        denom = DECIMAL_DENOMINATORS[denom_word]
        return Fraction(num, denom), next_idx
    else:
        # Если формируют 'четыре пятых' — попробуем распознать знаменатель из слова (упрощённо)
        # Попробуем извлечь число из слов, если denom_word — слово, обозначающее число (напр. "пятых" — будем резать окончание)
        # Найдём в словаре простых чисел основу
        # Алгоритм упрощён: попытаемся взять denom_word — если это слово есть в SIMPLE_NUM (без окончаний) — используем его
        # Иначе попытаемся удалить типичные окончания ('ых','ая','ых','ых' и т.д.) и повторно проверить
        base = denom_word
        if base in SIMPLE_NUM:
            denom = SIMPLE_NUM[base]
            return Fraction(num, denom), next_idx
        # Попытаемся убрать окончания
        for ending in ("ых", "ая", "ых", "ое", "ых", "их", "ых", "ых"):
            if base.endswith(ending):
                candidate = base[: -len(ending)]
                if candidate in SIMPLE_NUM:
                    denom = SIMPLE_NUM[candidate]
                    return Fraction(num, denom), next_idx
        # В противном случае — не поддерживаем такую форму
        raise ParseError(f"Неизвестный тип дробной части: '{denom_word}'")


def parse_mixed_or_decimal_number(
        tokens: List[str], start_index: int
) -> Tuple[Fraction, int]:
    """
    Парсит число, которое может быть:
     - целым (например 'пять')
     - смешанным: 'один и четыре пятых' или 'один и тридцать одна сотая'
     - десятичной дробью, записанной как 'и ... сотых' (мы поддерживаем только через 'и' как разделитель)
    Возвращает Fraction и индекс последнего использованного слова.
    """
    # Сначала пробуем целое
    val_int, idx_int_end = parse_simple_number_words(tokens, start_index)
    next_idx = idx_int_end + 1
    if next_idx < len(tokens) and tokens[next_idx] == "и":
        # есть дробная часть
        frac, idx_frac_end = parse_fractional_descriptor(tokens, next_idx + 1)
        return Fraction(val_int) + frac, idx_frac_end
    else:
        return Fraction(val_int), idx_int_end


# ---------- Токенизация входной строки ----------
def tokenize_expression(expr: str) -> List[Tuple[str, str]]:
    """
    Токенизирует входную строку в последовательность токенов (type, value):
      - ('NUMBER', Fraction) для чисел, но пока на этапе токенизации вернём слова и обработаем числа в парсере
      - ('OP', symbol) для операторов (+ - * / % ^)
      - ('FUNC', name) для функций (sin/cos/tan) — позиционно ожидается слово 'от' после имени
      - ('LPAREN'/'RPAREN') для скобок (словесных)
      - ('COMB', name) для комбинаторики (будем парсить далее)
      - ('WORD', word) для прочих слов (используется при парсинге чисел)
    Преобразует многословные операторы (например, "остаток от деления") в один токен.
    """
    s = expr.lower()
    # Нормализация: удалим лишние многопробелы
    s = re.sub(r"\s+", " ", s).strip()
    tokens_raw = []
    i = 0
    words = s.split(" ")
    n = len(words)
    # Обходим список слов, пытаясь на каждом шаге найти многословную фразу из PHRASE_TOKENS
    while i < n:
        matched = False
        # Проверяем фразы в порядке убывания длины
        for phrase in PHRASE_TOKENS:
            phrase_parts = phrase.split(" ")
            lp = len(phrase_parts)
            if i + lp - 1 < n and words[i: i + lp] == phrase_parts:
                # распознали фразу
                tokens_raw.append(("PHRASE", phrase))
                i += lp
                matched = True
                break
        if matched:
            continue
        # Проверки для функций, у которых форма "синус от"
        if (
                i + 1 < n
                and words[i] in {"синус", "косинус", "тангенс"}
                and words[i + 1] == "от"
        ):
            tokens_raw.append(("PHRASE", words[i] + " от"))
            i += 2
            continue
        # Скобки словесные
        if i + 2 < n and words[i] == "скобка" and words[i + 1] == "открывается":
            tokens_raw.append(("PHRASE", "скобка открывается"))
            i += 2
            continue
        if i + 2 < n and words[i] == "скобка" and words[i + 1] == "закрывается":
            tokens_raw.append(("PHRASE", "скобка закрывается"))
            i += 2
            continue
        # Комбинаторика может быть двух/трёхсловной (например "размещений из")
        if i + 1 < n and words[i] in COMBINATORICS and words[i + 1] == "из":
            tokens_raw.append(("PHRASE", words[i] + " из"))
            i += 2
            continue
        # иначе — просто слово
        tokens_raw.append(("WORD", words[i]))
        i += 1

    # Дополнительная постобработка: свёртка фраз в операторы, функции и скобки
    tokens: List[Tuple[str, str]] = []
    for typ, val in tokens_raw:
        if typ == "PHRASE":
            if val in OPERATORS:
                tokens.append(("OP", OPERATORS[val]["symbol"]))
            elif val in OPEN_PAREN:
                tokens.append(("LPAREN", "("))
            elif val in CLOSE_PAREN:
                tokens.append(("RPAREN", ")"))
            elif val in ("синус от", "косинус от", "тангенс от"):
                func_name = val.split()[0]
                tokens.append(("FUNC", func_name))
            elif val.endswith(" из"):  # комбинаторика
                comb_kind = val.split()[0]  # 'перестановок'/'размещений'/'сочетаний'
                tokens.append(("COMB", comb_kind))
            elif val == "в степени":
                tokens.append(("OP", "^"))
            elif val == "остаток от деления":
                tokens.append(("OP", "%"))
            else:
                # другой оператор, например 'плюс', 'минус', 'умножить', 'разделить'
                if val in OPERATORS:
                    tokens.append(("OP", OPERATORS[val]["symbol"]))
                else:
                    tokens.append(("WORD", val))
        else:
            tokens.append((typ, val))
    return tokens


# ---------- Построение выражения в ОПЗ (shunting-yard) и парсинг чисел ----------
def shunting_yard_with_numbers(
        tokens: List[Tuple[str, str]],
) -> List[Tuple[str, Union[str, Fraction]]]:
    """
    Преобразует токены в обратную польскую запись (RPN), одновременно собирая числа.
    Возвращает список RPN-элементов: ('NUM', Fraction) или ('OP', symbol) или ('FUNC', name) или ('COMB', name)
    """
    output_queue: List[Tuple[str, Union[str, Fraction]]] = []
    operator_stack: List[Tuple[str, str]] = []

    # Преобразуем поток токенов (WORD/FUNC/OP/LPAREN/RPAREN/COMB) в поток, где числа собираются
    i = 0
    length = len(tokens)

    while i < length:
        tok_type, tok_val = tokens[i]
        if tok_type == "WORD":
            # Слова могут быть началом числа (например 'двадцать', 'пять', 'один')
            # Пытаемся распознать смешанное/десятичное число, если не получится — это ошибка
            # Соберём последовательность слов, относящуюся к числу
            j = i
            word_seq = []
            while j < length and tokens[j][0] == "WORD":
                word_seq.append(tokens[j][1])
                # заранее останавливаем, если следующими идут операторы/функции/скобки/COMB
                # но на этапе while мы просто соберём широкую последовательность и попытаемся распознать
                j += 1
            # Попробуем распознать число начиная от i:
            try:
                num, last_idx = parse_mixed_or_decimal_number([w for w in word_seq], 0)
                # last_idx — индекс внутри word_seq; реальный индекс в tokens = i + last_idx
                consumed = last_idx + 1
                output_queue.append(("NUM", num))
                i += consumed
                continue
            except ParseError as e:
                # Если не удалось распознать число — возможно это слово-пломба (напр. "минус" как оператор)
                # поэтому попробуем поставить это слово обратно как отдельный токен
                # Но если слово не оператор — выдаём ошибку
                if tok_val in {"плюс", "минус", "умножить", "разделить"}:
                    # не должно случаться — эти слова обычно распарсены ранее как PHRASE->OP
                    output_queue.append(("OP", OPERATORS[tok_val]["symbol"]))
                    i += 1
                    continue
                else:
                    raise ParseError(
                        f"Не удалось распознать число из слов: {' '.join(word_seq[:5])}... ({e})"
                    )
        elif tok_type == "NUM":
            # в нашем tokenize этого не бывает; но оставлено для полноты
            output_queue.append(("NUM", tok_val))
            i += 1
        elif tok_type == "OP":
            op = tok_val
            # определяем precedence и assoc по символу
            prec, assoc = _operator_props(op)
            while operator_stack:
                top_type, top_val = operator_stack[-1]
                if top_type == "OP":
                    top_prec, _ = _operator_props(top_val)
                    if (assoc == "left" and prec <= top_prec) or (
                            assoc == "right" and prec < top_prec
                    ):
                        output_queue.append(("OP", top_val))
                        operator_stack.pop()
                        continue
                if top_type == "FUNC":
                    output_queue.append(("FUNC", top_val))
                    operator_stack.pop()
                    continue
                break
            operator_stack.append(("OP", op))
            i += 1
        elif tok_type == "FUNC":
            operator_stack.append(("FUNC", tok_val))
            i += 1
        elif tok_type == "COMB":
            # Комбинаторика — ожидаем далее числа: форма "перестановок из N" или "размещений из N по K"
            comb_kind = tok_val  # 'перестановок'/'размещений'/'сочетаний'
            # Разбор далее:
            # ожидается: номер N (числа словами), затем возможно 'по' и число K
            # Пропустим слово 'из' если оно отдельно
            # Найдём следующие WORD-последовательности и распознаем числа
            # Build small slice from tokens
            j = i + 1
            # Сбор слов после COMB: пропускаем 'из' если есть
            if j < length and tokens[j][0] == "WORD" and tokens[j][1] == "из":
                j += 1
            # Соберём слова до оператора/скобки/COMB/FUNC
            word_seq = []
            k = j
            while k < length and tokens[k][0] == "WORD":
                # остановимся если получим 'по' — тогда следующая последовательность это K
                if tokens[k][1] == "по":
                    break
                word_seq.append(tokens[k][1])
                k += 1
            if not word_seq:
                raise ParseError(
                    "Ожидалось число после '... из' в комбинаторной операции"
                )
            n_val, _ = parse_mixed_or_decimal_number(word_seq, 0)
            # Теперь проверим есть ли 'по' и второе число
            if k < length and tokens[k][0] == "WORD" and tokens[k][1] == "по":
                # соберём слова после 'по'
                l = k + 1
                word_seq2 = []
                while l < length and tokens[l][0] == "WORD":
                    word_seq2.append(tokens[l][1])
                    l += 1
                if not word_seq2:
                    raise ParseError(
                        "Ожидалось число после 'по' в комбинаторной операции"
                    )
                k_val, _ = parse_mixed_or_decimal_number(word_seq2, 0)
                # запишем как встроенную функцию: ('COMB', (kind, n_val, k_val))
                output_queue.append(("COMB", (comb_kind, n_val, k_val)))
                # передвинем i до l
                i = l
            else:
                # только N (для перестановок)
                output_queue.append(("COMB", (comb_kind, n_val, None)))
                i = k
        elif tok_type == "LPAREN":
            operator_stack.append(("LPAREN", tok_val))
            i += 1
        elif tok_type == "RPAREN":
            # выталкиваем до LPAREN
            found = False
            while operator_stack:
                top_type, top_val = operator_stack.pop()
                if top_type == "LPAREN":
                    found = True
                    break
                else:
                    output_queue.append((top_type, top_val))
            if not found:
                raise ParseError(
                    "Несбалансированные скобки (найдена закрывающая без открывающей)"
                )
            i += 1
        else:
            raise ParseError(f"Неизвестный тип токена: {tok_type}")
    # выталкиваем оставшиеся операторы
    while operator_stack:
        top_type, top_val = operator_stack.pop()
        if top_type in ("LPAREN", "RPAREN"):
            raise ParseError("Несбалансированные скобки (незакрытая скобка)")
        output_queue.append((top_type, top_val))
    return output_queue


def _operator_props(symbol: str) -> Tuple[int, str]:
    """Возвращает (precedence, assoc) для символа оператора"""
    for k, v in OPERATORS.items():
        if v["symbol"] == symbol:
            return v["precedence"], v["assoc"]
    # кастомные: '^' уже добавлен, '%' тоже
    if symbol == "^":
        return (3, "right")
    if symbol == "*":
        return (2, "left")
    if symbol == "/":
        return (2, "left")
    if symbol == "+":
        return (1, "left")
    if symbol == "-":
        return (1, "left")
    if symbol == "%":
        return (2, "left")
    # fallback
    return (1, "left")


# ---------- Оценщик выражения (вычисление RPN) ----------
def evaluate_rpn(rpn: List[Tuple[str, Union[str, Fraction]]]) -> Fraction:
    """
    Вычисляет выражение в обратной польской нотации.
    Возвращает Fraction (для тригонометрии/степеней — приближённое представление в Fraction через limit_denominator).
    """
    stack: List[Fraction] = []
    for elem_type, elem_val in rpn:
        if elem_type == "NUM":
            stack.append(elem_val)
        elif elem_type == "OP":
            # оператор бинарный; поддерживаем унарный минус как отдельную логику не здесь (мы превращали минус в унарный заранее)
            if len(stack) < 2:
                raise ParseError("Недостаточно операндов для бинарной операции")
            b = stack.pop()
            a = stack.pop()
            if elem_val == "+":
                stack.append(a + b)
            elif elem_val == "-":
                stack.append(a - b)
            elif elem_val == "*":
                stack.append(a * b)
            elif elem_val == "/":
                if b == 0:
                    raise MathError("Деление на ноль")
                stack.append(a / b)
            elif elem_val == "%":
                if b == 0:
                    raise MathError("Деление на ноль для операции остатка")
                # для остатка работаем с целыми: приведём к целому через floor, но если дробные — применим Fraction numerator%denom
                # Нормализуем: реализуем a % b как Fraction(a.numerator/a.denominator % b.numerator/b.denominator)
                # Преобразуем в вещественные дроби с ограничением — но проще: a % b = a - b * floor(a/b)
                quotient_floor = a // b
                stack.append(a - b * quotient_floor)
            elif elem_val == "^":
                # возведение в степень — поддерживаем целочисленные степени и дробные основания
                # если степень большая и нецелая — используем float и затем приближаем обратно в Fraction
                # Если степень — fraction с denominator==1 (целая)
                if b.denominator != 1:
                    # нецелая степень — используем float
                    val = float(a) ** float(b)
                    stack.append(Fraction(val).limit_denominator(10 ** 6))
                else:
                    exp = b.numerator
                    # поддержка отрицательных степеней
                    if exp >= 0:
                        stack.append(a ** exp)
                    else:
                        # отрицательная целая степень
                        stack.append(Fraction(1, 1) / (a ** abs(exp)))
            else:
                raise ParseError(f"Неизвестный оператор '{elem_val}'")
        elif elem_type == "FUNC":
            # применяем функцию к верхнему элементу стека
            if len(stack) < 1:
                raise ParseError("Недостаточно операндов для функции")
            arg = stack.pop()
            # вычисляем тригонометрию в радианах: arg задаётся в радианах (если пользователь хочет градусы — нужно дополнительно)
            if elem_val == "синус":
                val = sin(float(arg))
                stack.append(Fraction(val).limit_denominator(10 ** 6))
            elif elem_val == "косинус":
                val = cos(float(arg))
                stack.append(Fraction(val).limit_denominator(10 ** 6))
            elif elem_val == "тангенс":
                val = tan(float(arg))
                stack.append(Fraction(val).limit_denominator(10 ** 6))
            else:
                raise ParseError(f"Неизвестная функция '{elem_val}'")
        elif elem_type == "COMB":
            kind, n_val, k_val = elem_val
            # оба n_val и k_val — Fraction; ожидаем целые
            n = int(n_val)
            if k_val is None:
                # перестановки: n!
                if n < 0:
                    raise MathError("n для перестановок должен быть неотрицательным")
                result = factorial(n)
                stack.append(Fraction(result))
            else:
                k = int(k_val)
                if kind == "перестановок":
                    # перестановки из n по k — обычно nPk = n! / (n-k)!
                    if k > n or n < 0 or k < 0:
                        stack.append(Fraction(0))
                    else:
                        result = factorial(n) // factorial(n - k)
                        stack.append(Fraction(result))
                elif kind == "размещений":
                    # размещений — аналогично размещениям (размещений из n по k == nPk)
                    if k > n or n < 0 or k < 0:
                        stack.append(Fraction(0))
                    else:
                        result = factorial(n) // factorial(n - k)
                        stack.append(Fraction(result))
                elif kind == "сочетаний":
                    # nCk = n! / (k!(n-k)!)
                    if k > n or n < 0 or k < 0:
                        stack.append(Fraction(0))
                    else:
                        result = factorial(n) // (factorial(k) * factorial(n - k))
                        stack.append(Fraction(result))
                else:
                    raise ParseError(f"Неизвестный вид комбинаторики: {kind}")
        else:
            raise ParseError(f"Неподдерживаемый элемент RPN: {elem_type}")
    if len(stack) != 1:
        raise ParseError(
            "Некорректное выражение (после вычисления остаётся более одного значения на стеке)"
        )
    return stack[0]


# ---------- Высокоуровневая функция calc ----------
def calc(expression: str) -> str:
    """
    Вход: строка-выражение на русском языке.
    Выход: строка с текстовым представлением результата.
    Основные шаги:
      1) Токенизировать фразы
      2) Построить ОПЗ (RPN), распознав числа как Fraction
      3) Вычислить RPN -> Fraction
      4) Преобразовать Fraction в удобочитаемый русский текст (с дробями/десятичными/периодом)
    """
    if not isinstance(expression, str) or not expression.strip():
        raise ParseError("Пустая строка. Ожидается выражение.")

    # Нормализация и замены для удобства: 'пи' -> numeric token
    expr = expression.lower()
    expr = expr.replace("π", "пи")
    # Заменим слово 'пи' на эквивалент вещественной константы — представим как 'число' токен
    # Но можно оставить как слово и при парсинге интерпретировать 'пи' как число
    # Выполним токенизацию
    tokens = tokenize_expression(expr)

    # На стадии токенов обработаем простые случаи 'пи' как WORD -> заменим на NUM
    # Но наша shunting_yard ожидает WORD и попытается распознать числа из последовательности слов.
    # Поэтому преобразуем в tokens: если WORD == 'пи' — заменяем на ('NUM', Fraction(pi).limit_denominator())
    # Чтобы сохранить точность, представим пи как Fraction(round(pi,6)).limit_denominator(10**6)
    # Хотя тригонометрические функции обычно принимают аргументы в радианах, и нам удобно иметь pi.
    tokens_transformed: List[Tuple[str, str]] = []
    i = 0
    while i < len(tokens):
        ttype, tval = tokens[i]
        if ttype == "WORD" and tval == "пи":
            # заменяем на NUM
            # представим пи как Fraction(pi) approximated
            frac_pi = Fraction(str(pi)).limit_denominator(10 ** 6)
            # вставляем специальный токен NUM (для последующей обработки)
            tokens_transformed.append(("NUM", frac_pi))
            i += 1
        else:
            tokens_transformed.append((ttype, tval))
            i += 1

    # Далее нам нужно, чтобы shunting_yard_with_numbers мог работать со 'NUM' токенами и конструкциями WORD.
    # Однако его реализация ожидает WORD и внутренне вызывает parse_mixed_or_decimal_number.
    # Мы упрощаем: заменим токен 'NUM' на ('WORD', string-repr) так как shunting_yard_with_numbers при видении WORD
    # пытается распознать числа из последовательности слов. Но у нас NUM уже содержит Fraction.
    # Чтобы обработать NUM, будем вставлять ('NUM', Fraction) и чуть-чуть изменим shunting_yard_with_numbers — он умеет с NUM.
    # Поэтому используем уже существующие tokens_transformed.

    # Приводим все 'WORD' токены, заменяя None и т.п.
    # В shunting_yard_with_numbers ожидается список токенов с типами WORD/OP/FUNC/COMB/LPAREN/RPAREN/NUM
    rpn_input = []
    for ttype, tval in tokens_transformed:
        if ttype == "NUM":
            rpn_input.append(("NUM", tval))
        else:
            rpn_input.append((ttype, tval))

    # Теперь построение RPN: сначала простейший подход — преобразуем WORD-последовательности в NUM внутри shunting_yard_with_numbers
    rpn = shunting_yard_with_numbers(rpn_input)

    # Но shunting_yard_with_numbers формирует список с ('NUM', Fraction) или ('OP','+') etc.
    # Преобразуем его к форме, ожидаемой evaluate_rpn: ('NUM',Fraction) -> ('NUM',Fraction), ('OP', '+')->('OP','+'), ('FUNC',name)
    # Вычисляем значение
    result_fraction = evaluate_rpn(rpn)

    # Форматируем результат в текст
    result_text = fraction_to_mixed_and_words(result_fraction)
    return result_text

# ---------- Небольшие средства самотестирования (пустые) ----------
# В соответствии с пожеланием — не добавляем демонстрационных примеров/print в модуль.
# Модуль предоставляет функцию calc(expr: str) -> str, которую можно импортировать и использовать.
# Конец файла.

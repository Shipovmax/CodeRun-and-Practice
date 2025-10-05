def normalize_phone(phone):
    # Удаляем все нецифровые символы
    digits = "".join(filter(str.isdigit, phone))

    if len(digits) == 11:  # Если кол-во цифр 11, то указан и код и номер
        code = digits[1:4]
        number = digits[4:11]
    else:  # Если кол-во цифр 7, то нам не указали код - берём стандартный
        code = "495"
        number = digits

    return code, number


new_phone = input()
existing_phones = [input() for _ in range(3)]
new_code, new_number = normalize_phone(new_phone)
for phone in existing_phones:
    code, number = normalize_phone(phone)
    if code == new_code and number == new_number:
        print("YES")
    else:
        print("NO")

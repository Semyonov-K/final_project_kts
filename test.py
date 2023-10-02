# # Оригинальная строка
# SHOWBAR_ALREADY_ADD = '{"type": "show_snackbar", "text": "Вы уже добавлены в игру."}'

# # Замена значения в строке
# test = "ИГРАНОМЕР1"
# SHOWBAR_ALREADY_ADD = SHOWBAR_ALREADY_ADD.replace("Вы уже добавлены в игру.", f"Вы уже добавлены в игру {test}.")

# # Вывод результата
# print(SHOWBAR_ALREADY_ADD)
# # print(SHOWBAR_ALREADY_ODD)

# number_of_moves = 2
# name = 'aboba'
# price = 10000

# text_msg = f"""Сессия {number_of_moves} из 10.
# Акция 1: {name}, цена: {price}.
# Акция 2: {name}, цена: {price}.
# Акция 3: {name}, цена: {price}."""
# print(text_msg)

dic = {}
print(dic)
id = 151
if id not in dic:
    dic[id] = []
print(dic)
dic[id].append(1255)
print(dic)
print(len(dic[id]))
if 1255 in dic[id]:
    print("kekus")
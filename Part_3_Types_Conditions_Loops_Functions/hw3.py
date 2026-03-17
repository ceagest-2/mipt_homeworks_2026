#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"

MONTH_WITH_30_DAYS = (4, 6, 9, 11)

def is_leap_year(year: int) -> bool:
    if ((year % 4 == 0) and (year % 100 != 0)) or ((year % 100 == 0) and (year % 400 == 0)):
        return True
    return False


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    if not valid_date(maybe_dt):
        return None
    blocks = maybe_dt.split('-')
    day = int(blocks[0].lstrip("0"))
    month = int(blocks[1].lstrip("0"))
    year = int(blocks[2].lstrip("0"))
    return day, month, year

def valid_date(maybe_dt:str) -> bool:
    blocks = maybe_dt.split('-')
    if len(blocks) != 3:
        return False
    if valid_month(blocks[1]) and valid_year(blocks[2]):
        mount = int(blocks[1].lstrip("0"))
        year = int(blocks[2].lstrip("0"))
        if valid_day(blocks[0], mount, year):
            return True
    return False

def valid_day(maybe_day:str, month:int, year:int) -> bool:
    blocks = maybe_day.split(" ")
    if len(blocks) != 1 or len(maybe_day) != 2:
        return False
    if not maybe_day.lstrip("0").isdecimal():
        return False
    maybe_day_number = int(maybe_day.lstrip("0"))
    if (month not in MONTH_WITH_30_DAYS) and (month != 2) and (1 <= maybe_day_number <= 31):
        return True
    elif month == 2:
        if is_leap_year(year) and (1 <= maybe_day_number <= 29):
            return True
        if (not is_leap_year(year)) and (1 <= maybe_day_number <= 28):
            return True
        return False
    elif (month in MONTH_WITH_30_DAYS) and (1 <= maybe_day_number <= 30):
        return True
    return False

def valid_month(maybe_month:str) -> bool:
    blocks = maybe_month.split(" ")
    if len(blocks) != 1 or len(maybe_month) != 2:
        return False
    if not maybe_month.lstrip("0").isdecimal():
        return False
    maybe_month_number = int(maybe_month.lstrip("0"))
    if 1 <= maybe_month_number <= 12:
        return True
    return False

def valid_year(maybe_year:str) -> bool:
    blocks = maybe_year.split(" ")
    if len(blocks) != 1 or len(maybe_year) != 4:
        return False
    if not maybe_year.lstrip("0").isdecimal():
        return False
    maybe_year_number = int(maybe_year.lstrip("0"))
    if maybe_year_number >= 1:
        return True
    return False

def valid_float(maybe_float:str) -> bool:
    blocks = maybe_float.split(" ")
    if len(blocks) > 1:
        return False
    maybe_float = maybe_float.replace(",", ".")
    if "." not in maybe_float:
        maybe_float = maybe_float + "." + "0"
    parts = maybe_float.split(".")
    if len(parts) != 2:
        return False
    if (parts[0].isdecimal() or (parts[0][0] == '-' and parts[0][1:].isdecimal())) and parts[1].isdecimal():
        return True
    return False

def valid_category(maybe_category: str) -> bool:
    if (" " not in maybe_category) and (maybe_category != "") and ("." not in maybe_category) and ("," not in maybe_category):
        return True
    return False

def adding_income(receipt_line: str, receipts: list) -> None:
    blocks = receipt_line.split(" ")
    amount = float(blocks[1])
    date = blocks[2]
    receipts.append((amount, date))

def adding_an_expense(expense_line: str, expenses: list) -> None:
    blocks = expense_line.split(" ")
    category = blocks[1]
    amount = float(blocks[2])
    date = blocks[3]
    expenses.append((category, amount, date))

def compare_dates_by_month(date1_str: str, date2_str: str) -> int:
    date1 = extract_date(date1_str)
    date2 = extract_date(date2_str)
    if (date1[2] != date2[2]) or (date1[1] != date2[1]):
        return 2
    if date1[0] < date2[0]:
        return 1
    elif date1[0] > date2[0]:
        return -1
    else:
        return 0

def compare_dates(date1_str: str, date2_str: str) -> int:
    date1 = extract_date(date1_str)
    date2 = extract_date(date2_str)
    if date1[2] < date2[2]:
        return 1
    elif date1[2] > date2[2]:
        return -1
    else:
        if date1[1] < date2[1]:
            return 1
        elif date1[1] > date2[1]:
            return -1
        else:
            if date1[0] < date2[0]:
                return 1
            elif date1[0] > date2[0]:
                return -1
            else:
                return 0

def get_statistics(line: str, receipts_list: list, expenses_list: list) -> None:
    blocks = line.split(" ")
    date = blocks[1]
    print(f"Ваша статистика по состоянию на {date}:")
    total_capital = 0
    receipts = 0
    expenses = 0
    categories_and_amounts = dict()
    for income in receipts_list:
        amount = income[0]
        current_date = income[1]
        if compare_dates(current_date, date) == 1:
            total_capital += amount
        if compare_dates_by_month(current_date, date) == 1:
            receipts += amount
    for expenditure in expenses_list:
        category = expenditure[0]
        amount = expenditure[1]
        current_date = expenditure[2]
        if compare_dates(current_date, date) == 1:
            total_capital -= amount
        if compare_dates_by_month(current_date, date) == 1:
            expenses += amount
            if categories_and_amounts.get(category) is None:
                categories_and_amounts.update({category: amount})
            else:
                categories_and_amounts.update({category: categories_and_amounts.get(category) + amount})
    print(f"Суммарный капитал: {total_capital} рублей")
    difference = receipts - expenses
    if difference >= 0:
        print(f"В этом месяце прибыль составила {difference} рублей")
    else:
        print(f"В этом месяце убыток составил {-difference} рублей")
    print(f"Доходы: {receipts} рублей")
    print(f"Расходы: {expenses} рублей")
    print("Детализация (категория: сумма):")
    sorted_keys = sorted(categories_and_amounts)
    categories_and_amounts = {key: categories_and_amounts[key] for key in sorted_keys}
    counter = 0
    for pair in categories_and_amounts.items():
        counter += 1
        category = pair[0]
        amount = pair[1]
        print(f"{counter}. {category}: {amount}")

def operation_validation(operation: str) -> str:
    blocks = operation.split(" ")
    if len(blocks) > 4 or len(blocks) == 1:
        return UNKNOWN_COMMAND_MSG
    if blocks[0] == "income" and len(blocks) == 3:
        if valid_float(blocks[1]) and float(blocks[1]) > 0 and valid_date(blocks[2]):
            return "income"
        elif valid_float(blocks[1]) and float(blocks[1]) <= 0:
            return NONPOSITIVE_VALUE_MSG
        elif not valid_date(blocks[2]):
            return INCORRECT_DATE_MSG
    if blocks[0] == "cost" and len(blocks) == 4:
        if valid_category(blocks[1]) and valid_float(blocks[2]) and float(blocks[2]) > 0 and valid_date(blocks[3]):
            return "cost"
        elif not valid_category(blocks[1]):
            return UNKNOWN_COMMAND_MSG
        elif valid_float(blocks[2]) and float(blocks[2]) <= 0:
            return NONPOSITIVE_VALUE_MSG
        elif not valid_date(blocks[2]):
            return INCORRECT_DATE_MSG
    if blocks[0] == "stats" and len(blocks) == 2:
        if valid_date(blocks[1]):
            return "stats"
        else:
            return INCORRECT_DATE_MSG
    return UNKNOWN_COMMAND_MSG

def main() -> None:
    receipts_list = []
    expenses_list = []
    while True:
        line = input()
        if not line:
            break
        validate = operation_validation(line)
        if validate in [UNKNOWN_COMMAND_MSG, NONPOSITIVE_VALUE_MSG, INCORRECT_DATE_MSG]:
            print(validate)
            continue
        else:
            if validate == "income":
                adding_income(line, receipts_list)
                print(OP_SUCCESS_MSG)
            elif validate == "cost":
                adding_an_expense(line, expenses_list)
                print(OP_SUCCESS_MSG)
            else:
                get_statistics(line, receipts_list, expenses_list)

if __name__ == "__main__":
    main()

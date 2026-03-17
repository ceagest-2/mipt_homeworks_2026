#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"

LEN_BLOCKS = 3
LEN_BIG_BLOOKS = 4
LEN_SMALL_BLOOKS = 2
INCOME_COMMAND_PARTS = 3
COST_COMMAND_PARTS = 4
LEN_DAYS = 2
LEN_MONTH = 2
LEN_YEARS = 4
FIRST_MONTH = 1
LAST_MONTH = 12
LONG_MONTH_DAYS = 31
SHORT_MONTH_DAYS = 30
LEAP_FEBRUARY_DAYS = 29
COMMON_FEBRUARY_DAYS = 28
FEBRUARY_MONTH = 2
THE_EDGE_CASE = 2

MONTH_WITH_30_DAYS = (4, 6, 9, 11)


def is_leap_year(year: int) -> bool:
    return bool((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0))


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    if not valid_date(maybe_dt):
        return None
    blocks = maybe_dt.split("-")
    day = int(blocks[0].lstrip("0") or "0")
    month = int(blocks[1].lstrip("0") or "0")
    year = int(blocks[2].lstrip("0") or "0")
    return day, month, year


def valid_date(maybe_dt: str) -> bool:
    blocks = maybe_dt.split("-")
    if len(blocks) != LEN_BLOCKS:
        return False
    if valid_month(blocks[1]) and valid_year(blocks[2]):
        month = int(blocks[1].lstrip("0") or "0")
        year = int(blocks[2].lstrip("0") or "0")
        return valid_day(blocks[0], month, year)
    return False


def valid_day(maybe_day: str, month: int, year: int) -> bool:
    blocks = maybe_day.split(" ")
    if len(blocks) != 1 or len(maybe_day) != LEN_DAYS:
        return False
    if not maybe_day.lstrip("0").isdecimal() and maybe_day != "00":
        return False
    maybe_day_number = int(maybe_day.lstrip("0") or "0")

    if month == FEBRUARY_MONTH:
        max_days = LEAP_FEBRUARY_DAYS if is_leap_year(year) else COMMON_FEBRUARY_DAYS
        return 1 <= maybe_day_number <= max_days

    max_days = SHORT_MONTH_DAYS if month in MONTH_WITH_30_DAYS else LONG_MONTH_DAYS
    return 1 <= maybe_day_number <= max_days


def valid_month(maybe_month: str) -> bool:
    blocks = maybe_month.split(" ")
    if len(blocks) != 1 or len(maybe_month) != LEN_MONTH:
        return False
    if not maybe_month.lstrip("0").isdecimal() and maybe_month != "00":
        return False
    maybe_month_number = int(maybe_month.lstrip("0") or "0")
    return FIRST_MONTH <= maybe_month_number <= LAST_MONTH


def valid_year(maybe_year: str) -> bool:
    blocks = maybe_year.split(" ")
    if len(blocks) != 1 or len(maybe_year) != LEN_YEARS:
        return False
    if not maybe_year.lstrip("0").isdecimal() and maybe_year != "0000":
        return False
    maybe_year_number = int(maybe_year.lstrip("0") or "0")
    return maybe_year_number >= 1


def valid_float(maybe_float: str) -> bool:
    blocks = maybe_float.split(" ")
    if len(blocks) > 1:
        return False
    maybe_float_normalized = maybe_float.replace(",", ".")
    if "." not in maybe_float_normalized:
        maybe_float_normalized = maybe_float_normalized + ".0"
    parts = maybe_float_normalized.split(".")
    if len(parts) != LEN_SMALL_BLOOKS:
        return False
    first_part_valid = parts[0].isdecimal() or (len(parts[0]) > 1 and parts[0][0] == "-" and parts[0][1:].isdecimal())
    return bool(first_part_valid and parts[1].isdecimal())


def valid_category(maybe_category: str) -> bool:
    return bool(
        " " not in maybe_category and maybe_category != "" and "." not in maybe_category and "," not in maybe_category
    )


def adding_income(receipt_line: str, receipts: list[tuple[float, str]]) -> None:
    blocks = receipt_line.split(" ")
    amount = float(blocks[1].replace(",", "."))
    date = blocks[2]
    receipts.append((amount, date))


def adding_an_expense(expense_line: str, expenses: list[tuple[str, float, str]]) -> None:
    blocks = expense_line.split(" ")
    category = blocks[1]
    amount = float(blocks[2].replace(",", "."))
    date = blocks[3]
    expenses.append((category, amount, date))


def compare_dates_by_month(date1_str: str, date2_str: str) -> int:
    date1 = extract_date(date1_str)
    date2 = extract_date(date2_str)
    if date1 is None or date2 is None:
        return 0
    if (date1[2] != date2[2]) or (date1[1] != date2[1]):
        return 2
    if date1[0] < date2[0]:
        return 1
    return -1 if date1[0] > date2[0] else 0


def compare_dates(date1_str: str, date2_str: str) -> int:
    date1 = extract_date(date1_str)
    date2 = extract_date(date2_str)
    if date1 is None or date2 is None:
        return 0

    if date1[2] != date2[2]:
        return 1 if date1[2] < date2[2] else -1
    if date1[1] != date2[1]:
        return 1 if date1[1] < date2[1] else -1

    return 1 if date1[0] < date2[0] else (-1 if date1[0] > date2[0] else 0)


def _process_income(receipts_list: list[tuple[float, str]], date: str) -> tuple[float, float]:
    """Processing income for statistics."""
    total_capital = 0.0
    receipts = 0.0
    for income in receipts_list:
        amount = income[0]
        current_date = income[1]
        if compare_dates(current_date, date) >= 0:
            total_capital += amount
        if (
            compare_dates_by_month(current_date, date) >= 0
            and compare_dates_by_month(current_date, date) != THE_EDGE_CASE
        ):
            receipts += amount
    return total_capital, receipts


def _process_expenses(expenses_list: list[tuple[str, float, str]], date: str) -> tuple[float, float, dict[str, float]]:
    """Processing expenses for statistics."""
    total_capital = 0.0
    expenses = 0.0
    categories_and_amounts: dict[str, float] = {}
    for expenditure in expenses_list:
        category = expenditure[0]
        amount = expenditure[1]
        current_date = expenditure[2]
        if compare_dates(current_date, date) >= 0:
            total_capital -= amount
        if (
            compare_dates_by_month(current_date, date) >= 0
            and compare_dates_by_month(current_date, date) != THE_EDGE_CASE
        ):
            expenses += amount
            if category in categories_and_amounts:
                categories_and_amounts[category] += amount
            else:
                categories_and_amounts[category] = amount
    return total_capital, expenses, categories_and_amounts


def statistics(
    line: str,
    receipts_list: list[tuple[float, str]],
    expenses_list: list[tuple[str, float, str]],
) -> None:
    blocks = line.split(" ")
    date = blocks[1]
    print(f"Ваша статистика по состоянию на {date}:")

    income_capital, receipts = _process_income(receipts_list, date)
    expense_capital, expenses, categories = _process_expenses(expenses_list, date)

    total_capital = income_capital + expense_capital
    difference = receipts - expenses

    print(f"Суммарный капитал: {total_capital:.2f} рублей")
    if difference >= 0:
        print(f"В этом месяце прибыль составила {difference:.2f} рублей")  # noqa: RUF001
    else:
        print(f"В этом месяце убыток составил {-difference:.2f} рублей")  # noqa: RUF001
    print(f"Доходы: {receipts:.2f} рублей")
    print(f"Расходы: {expenses:.2f} рублей")
    print("Детализация (категория: сумма):")

    sorted_keys = sorted(categories)
    for index, key in enumerate(sorted_keys, start=1):
        amount = categories[key]
        print(f"{index}. {key}: {amount:.2f}")


def _validate_income(blocks: list[str]) -> str:
    """Validation for income command."""
    if not valid_float(blocks[1]):
        return NONPOSITIVE_VALUE_MSG
    amount = float(blocks[1].replace(",", "."))
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    if not valid_date(blocks[2]):
        return INCORRECT_DATE_MSG
    return "income"


def _validate_cost(blocks: list[str]) -> str:
    """Validation for cost command."""
    if not valid_category(blocks[1]):
        return UNKNOWN_COMMAND_MSG
    if not valid_float(blocks[2]):
        return NONPOSITIVE_VALUE_MSG
    amount = float(blocks[2].replace(",", "."))
    if amount <= 0:
        return NONPOSITIVE_VALUE_MSG
    if not valid_date(blocks[3]):
        return INCORRECT_DATE_MSG
    return "cost"


def _validate_stats(blocks: list[str]) -> str:
    """Validation for stats command."""
    return "stats" if valid_date(blocks[1]) else INCORRECT_DATE_MSG


def operation_validation(operation: str) -> str:
    blocks = operation.split(" ")
    if len(blocks) > LEN_BIG_BLOOKS or len(blocks) == 1:
        return UNKNOWN_COMMAND_MSG

    if blocks[0] == "income" and len(blocks) == LEN_BLOCKS:
        return _validate_income(blocks)
    if blocks[0] == "cost" and len(blocks) == LEN_BIG_BLOOKS:
        return _validate_cost(blocks)
    if blocks[0] == "stats" and len(blocks) == LEN_SMALL_BLOOKS:
        return _validate_stats(blocks)

    return UNKNOWN_COMMAND_MSG


def main() -> None:
    receipts_list: list[tuple[float, str]] = []
    expenses_list: list[tuple[str, float, str]] = []
    while True:
        line = input()
        if not line:
            break
        validate = operation_validation(line)
        if validate in [UNKNOWN_COMMAND_MSG, NONPOSITIVE_VALUE_MSG, INCORRECT_DATE_MSG]:
            print(validate)
            continue
        if validate == "income":
            adding_income(line, receipts_list)
            print(OP_SUCCESS_MSG)
        elif validate == "cost":
            adding_an_expense(line, expenses_list)
            print(OP_SUCCESS_MSG)
        else:
            statistics(line, receipts_list, expenses_list)


if __name__ == "__main__":
    main()

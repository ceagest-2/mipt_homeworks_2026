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
MONTHS_WITH_THIRTY_DAYS = (4, 6, 9, 11)
STRING_ZERO = "0"
POINT_ZERO = ".0"


def is_leap_year(year: int) -> bool:
    is_div_by_four = year % 4 == 0
    is_div_by_hundred = year % 100 == 0
    is_div_by_four_hundred = year % 400 == 0
    return bool(
        (is_div_by_four and not is_div_by_hundred) or is_div_by_four_hundred,
    )


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    if not valid_date(maybe_dt):
        return None
    blocks = maybe_dt.split("-")
    day = int(blocks[0].lstrip(STRING_ZERO) or STRING_ZERO)
    month = int(blocks[1].lstrip(STRING_ZERO) or STRING_ZERO)
    year = int(blocks[2].lstrip(STRING_ZERO) or STRING_ZERO)
    return day, month, year


def valid_date(maybe_dt: str) -> bool:
    blocks = maybe_dt.split("-")
    if len(blocks) != LEN_BLOCKS:
        return False
    month_valid = valid_month(blocks[1])
    year_valid = valid_year(blocks[2])
    if month_valid and year_valid:
        month = int(blocks[1].lstrip(STRING_ZERO) or STRING_ZERO)
        year = int(blocks[2].lstrip(STRING_ZERO) or STRING_ZERO)
        return valid_day(blocks[0], month, year)
    return False


def valid_day(maybe_day: str, month: int, year: int) -> bool:
    blocks = maybe_day.split(" ")
    if len(blocks) != 1 or len(maybe_day) != LEN_DAYS:
        return False
    is_decimal = maybe_day.lstrip(STRING_ZERO).isdecimal()
    is_zero = maybe_day == "00"
    if not is_decimal and not is_zero:
        return False
    maybe_day_number = int(maybe_day.lstrip(STRING_ZERO) or STRING_ZERO)

    if month == FEBRUARY_MONTH:
        max_days = (
            LEAP_FEBRUARY_DAYS
            if is_leap_year(year)
            else COMMON_FEBRUARY_DAYS
        )
        return 1 <= maybe_day_number <= max_days

    max_days = (
        SHORT_MONTH_DAYS
        if month in MONTHS_WITH_THIRTY_DAYS
        else LONG_MONTH_DAYS
    )
    return 1 <= maybe_day_number <= max_days


def valid_month(maybe_month: str) -> bool:
    blocks = maybe_month.split(" ")
    if len(blocks) != 1 or len(maybe_month) != LEN_MONTH:
        return False
    is_decimal = maybe_month.lstrip(STRING_ZERO).isdecimal()
    is_zero = maybe_month == "00"
    if not is_decimal and not is_zero:
        return False
    maybe_month_number = int(maybe_month.lstrip(STRING_ZERO) or STRING_ZERO)
    return FIRST_MONTH <= maybe_month_number <= LAST_MONTH


def valid_year(maybe_year: str) -> bool:
    blocks = maybe_year.split(" ")
    if len(blocks) != 1 or len(maybe_year) != LEN_YEARS:
        return False
    is_decimal = maybe_year.lstrip(STRING_ZERO).isdecimal()
    is_zero = maybe_year == "0000"
    if not is_decimal and not is_zero:
        return False
    maybe_year_number = int(maybe_year.lstrip(STRING_ZERO) or STRING_ZERO)
    return maybe_year_number >= 1


def _check_float_parts(normalized: str) -> bool:
    """Check if float has valid parts."""
    parts = normalized.split(".")
    if len(parts) != LEN_SMALL_BLOOKS:
        return False
    first_is_decimal = parts[0].isdecimal()
    is_negative_number = (
        len(parts[0]) > 1
        and parts[0][0] == "-"
        and parts[0][1:].isdecimal()
    )
    first_valid = first_is_decimal or is_negative_number
    return bool(first_valid and parts[1].isdecimal())


def valid_float(maybe_float: str) -> bool:
    blocks = maybe_float.split(" ")
    if len(blocks) > 1:
        return False
    normalized = maybe_float.replace(",", ".")
    if "." not in normalized:
        normalized = normalized.join((normalized, POINT_ZERO))
    return _check_float_parts(normalized)


def valid_category(maybe_category: str) -> bool:
    has_no_space = " " not in maybe_category
    not_empty = maybe_category != ""
    has_no_point = "." not in maybe_category
    has_no_comma = "," not in maybe_category
    return bool(has_no_space and not_empty and has_no_point and has_no_comma)


def adding_income(receipt_line: str, receipts: list[tuple[float, str]]) -> None:
    blocks = receipt_line.split(" ")
    amount = float(blocks[1].replace(",", "."))
    date = blocks[2]
    receipts.append((amount, date))


def adding_an_expense(
    expense_line: str,
    expenses: list[tuple[str, float, str]],
) -> None:
    blocks = expense_line.split(" ")
    category = blocks[1]
    amount = float(blocks[2].replace(",", "."))
    date = blocks[3]
    expenses.append((category, amount, date))


def _compare_years(
    date_one: tuple[int, int, int],
    date_two: tuple[int, int, int],
) -> int:
    """Compare years of two dates."""
    if date_one[2] < date_two[2]:
        return 1
    return -1 if date_one[2] > date_two[2] else 0


def _compare_months(
    date_one: tuple[int, int, int],
    date_two: tuple[int, int, int],
) -> int:
    """Compare months of two dates."""
    if date_one[1] < date_two[1]:
        return 1
    return -1 if date_one[1] > date_two[1] else 0


def _compare_days(
    date_one: tuple[int, int, int],
    date_two: tuple[int, int, int],
) -> int:
    """Compare days of two dates."""
    if date_one[0] < date_two[0]:
        return 1
    return -1 if date_one[0] > date_two[0] else 0


def compare_dates_by_month(date_one_str: str, date_two_str: str) -> int:
    """Compare dates by month and year."""
    date_one = extract_date(date_one_str)
    date_two = extract_date(date_two_str)
    if date_one is None or date_two is None:
        return 0
    years_equal = date_one[2] == date_two[2]
    months_equal = date_one[1] == date_two[1]
    if not years_equal or not months_equal:
        return 2
    return (
        -1
        if date_one[0] > date_two[0]
        else (1 if date_one[0] < date_two[0] else 0)
    )


def _get_day_comparison(
    date_one: tuple[int, int, int],
    date_two: tuple[int, int, int],
) -> int:
    """Get comparison result for days."""
    if date_one[0] > date_two[0]:
        return -1
    return 1 if date_one[0] < date_two[0] else 0


def compare_dates(date_one_str: str, date_two_str: str) -> int:
    """Compare two dates."""
    date_one = extract_date(date_one_str)
    date_two = extract_date(date_two_str)
    if date_one is None or date_two is None:
        return 0

    year_cmp = _compare_years(date_one, date_two)
    if year_cmp != 0:
        return year_cmp

    month_cmp = _compare_months(date_one, date_two)
    if month_cmp != 0:
        return month_cmp

    return _get_day_comparison(date_one, date_two)


def _accumulate_income(
    receipts_list: list[tuple[float, str]],
    date: str,
) -> tuple[float, float]:
    """Accumulate income data."""
    capital = 0
    total = 0
    for amount, current_date in receipts_list:
        if compare_dates(current_date, date) >= 0:
            capital += amount
        month_cmp = compare_dates_by_month(current_date, date)
        if month_cmp >= 0 and month_cmp != THE_EDGE_CASE:
            total += amount
    return float(capital), float(total)


def _accumulate_expenses(
    expenses_list: list[tuple[str, float, str]],
    date: str,
) -> tuple[float, float, dict[str, float]]:
    """Accumulate expense data."""
    capital = 0
    total = 0
    categories: dict[str, float] = {}
    for category, amount, current_date in expenses_list:
        if compare_dates(current_date, date) >= 0:
            capital -= amount
        month_cmp = compare_dates_by_month(current_date, date)
        if month_cmp >= 0 and month_cmp != THE_EDGE_CASE:
            total += amount
            current = categories.get(category, 0)
            categories[category] = current + amount
    return float(capital), float(total), categories


def _print_statistics_header(date: str) -> None:
    """Print statistics header."""
    print(f"Ваша статистика по состоянию на {date}:")


def _print_capital_and_profit(
    total_capital: float,
    receipts: float,
    expenses: float,
) -> None:
    """Print capital and profit information."""
    print(f"Суммарный капитал: {total_capital:.2f} рублей")
    difference = receipts - expenses
    if difference >= 0:
        msg = f"В этом месяце прибыль составила {difference:.2f} рублей"  # noqa: RUF001
        print(msg)
    else:
        loss = -difference
        msg = f"В этом месяце убыток составил {loss:.2f} рублей"  # noqa: RUF001
        print(msg)


def _print_income_expense(receipts: float, expenses: float) -> None:
    """Print income and expense information."""
    print(f"Доходы: {receipts:.2f} рублей")
    print(f"Расходы: {expenses:.2f} рублей")


def _print_categories(categories: dict[str, float]) -> None:
    """Print category breakdown."""
    print("Детализация (категория: сумма):")
    sorted_keys = sorted(categories)
    for index, key in enumerate(sorted_keys, start=1):
        amount = categories[key]
        print(f"{index}. {key}: {amount:.2f}")


def _get_statistics_data(
    receipts_list: list[tuple[float, str]],
    expenses_list: list[tuple[str, float, str]],
    date: str,
) -> tuple[float, float, float, dict[str, float]]:
    """Get statistics data for a specific date."""
    income_capital, receipts = _accumulate_income(receipts_list, date)
    expense_capital, expenses, categories = _accumulate_expenses(
        expenses_list,
        date,
    )
    total_capital = income_capital + expense_capital
    return total_capital, receipts, expenses, categories


def get_statistics(
    line: str,
    receipts_list: list[tuple[float, str]],
    expenses_list: list[tuple[str, float, str]],
) -> None:
    """Get and display statistics for a given date."""
    blocks = line.split(" ")
    date = blocks[1]
    _print_statistics_header(date)

    total_capital, receipts, expenses, categories = _get_statistics_data(
        receipts_list,
        expenses_list,
        date,
    )

    _print_capital_and_profit(total_capital, receipts, expenses)
    _print_income_expense(receipts, expenses)
    _print_categories(categories)


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


def _handle_command(
    validate: str,
    line: str,
    receipts_list: list[tuple[float, str]],
    expenses_list: list[tuple[str, float, str]],
) -> None:
    """Handle validated command."""
    if validate == "income":
        adding_income(line, receipts_list)
        print(OP_SUCCESS_MSG)
    elif validate == "cost":
        adding_an_expense(line, expenses_list)
        print(OP_SUCCESS_MSG)
    else:
        get_statistics(line, receipts_list, expenses_list)


def operation_validation(operation: str) -> str:
    """Validate the operation string."""
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
    """Main function to run the program."""
    receipts_list: list[tuple[float, str]] = []
    expenses_list: list[tuple[str, float, str]] = []
    while True:
        line = input()
        if not line:
            break
        validate = operation_validation(line)
        error_messages = {UNKNOWN_COMMAND_MSG, NONPOSITIVE_VALUE_MSG, INCORRECT_DATE_MSG}
        if validate in error_messages:
            print(validate)
            continue
        _handle_command(validate, line, receipts_list, expenses_list)


if __name__ == "__main__":
    main()

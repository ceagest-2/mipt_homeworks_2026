#!/usr/bin/env python

UNKNOWN_COMMAND_MSG = "Неизвестная команда!"
NONPOSITIVE_VALUE_MSG = "Значение должно быть больше нуля!"
INCORRECT_DATE_MSG = "Неправильная дата!"
OP_SUCCESS_MSG = "Добавлено"

LEN_BLOCKS = 3
LEN_BIG_BLOCKS = 4
LEN_SMALL_BLOCKS = 2
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
MONTHS = (4, 6, 9, 11)
STRING_ZERO = "0"
POINT_ZERO = ".0"
DEFAULT_ZERO = 0.0


def is_leap_year(year: int) -> bool:
    div4 = year % 4 == 0
    div100 = year % 100 == 0
    div400 = year % 400 == 0
    return bool((div4 and not div100) or div400)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    if not valid_date(maybe_dt):
        return None
    blocks = maybe_dt.split("-")
    day = int(blocks[0].lstrip(STRING_ZERO) or STRING_ZERO)
    month = int(blocks[1].lstrip(STRING_ZERO) or STRING_ZERO)
    year = int(blocks[2].lstrip(STRING_ZERO) or STRING_ZERO)
    return day, month, year


def _is_decimal_or_zero(text: str, zero_value: str) -> bool:
    """Check if text is decimal or zero."""
    return text.lstrip(STRING_ZERO).isdecimal() or text == zero_value


def valid_day(maybe_day: str, month: int, year: int) -> bool:
    blocks = maybe_day.split(" ")
    if len(blocks) != 1 or len(maybe_day) != LEN_DAYS:
        return False
    if not _is_decimal_or_zero(maybe_day, "00"):
        return False
    maybe_day_number = int(maybe_day.lstrip(STRING_ZERO) or STRING_ZERO)

    if month == FEBRUARY_MONTH:
        max_days = (
            LEAP_FEBRUARY_DAYS if is_leap_year(year)
            else COMMON_FEBRUARY_DAYS
        )
        return 1 <= maybe_day_number <= max_days

    max_days = (
        SHORT_MONTH_DAYS if month in MONTHS
        else LONG_MONTH_DAYS
    )
    return 1 <= maybe_day_number <= max_days


def valid_month(maybe_month: str) -> bool:
    blocks = maybe_month.split(" ")
    if len(blocks) != 1 or len(maybe_month) != LEN_MONTH:
        return False
    if not _is_decimal_or_zero(maybe_month, "00"):
        return False
    maybe_month_number = int(maybe_month.lstrip(STRING_ZERO) or STRING_ZERO)
    return FIRST_MONTH <= maybe_month_number <= LAST_MONTH


def valid_year(maybe_year: str) -> bool:
    blocks = maybe_year.split(" ")
    if len(blocks) != 1 or len(maybe_year) != LEN_YEARS:
        return False
    if not _is_decimal_or_zero(maybe_year, "0000"):
        return False
    maybe_year_number = int(maybe_year.lstrip(STRING_ZERO) or STRING_ZERO)
    return maybe_year_number >= 1


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


def _check_first_part(first: str) -> bool:
    """Check if first part is valid decimal or negative."""
    if first.isdecimal():
        return True
    if len(first) <= 1:
        return False
    is_negative = first[0] == "-"
    has_decimal = first[1:].isdecimal()
    return is_negative and has_decimal


def _check_float_parts(normalized: str) -> bool:
    """Check if float has valid parts."""
    parts = normalized.split(".")
    if len(parts) != LEN_SMALL_BLOCKS:
        return False
    first_valid = _check_first_part(parts[0])
    second_valid = parts[1].isdecimal()
    return bool(first_valid and second_valid)


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
    expense_line: str, expenses: list[tuple[str, float, str]]
) -> None:
    blocks = expense_line.split(" ")
    category = blocks[1]
    amount = float(blocks[2].replace(",", "."))
    date = blocks[3]
    expenses.append((category, amount, date))


def _compare_value(val1: int, val2: int) -> int:
    """Compare two values: 1 if val1 < val2, -1 if val1 > val2, 0 if equal."""
    if val1 < val2:
        return 1
    return -1 if val1 > val2 else 0


def compare_dates_by_month(date1_str: str, date2_str: str) -> int:
    date1 = extract_date(date1_str)
    date2 = extract_date(date2_str)
    if date1 is None or date2 is None:
        return 0
    years_equal = date1[2] == date2[2]
    months_equal = date1[1] == date2[1]
    if not years_equal or not months_equal:
        return 2
    return _compare_value(date1[0], date2[0])


def compare_dates(date1_str: str, date2_str: str) -> int:
    date1 = extract_date(date1_str)
    date2 = extract_date(date2_str)
    if date1 is None or date2 is None:
        return 0

    year_cmp = _compare_value(date1[2], date2[2])
    if year_cmp != 0:
        return year_cmp

    month_cmp = _compare_value(date1[1], date2[1])
    if month_cmp != 0:
        return month_cmp

    return _compare_value(date1[0], date2[0])


def _check_income_date(current_date: str, date: str) -> int:
    """Check if income date is within range and return multiplier."""
    return 1 if compare_dates(current_date, date) >= 0 else 0


def _check_month_date(current_date: str, date: str) -> int:
    """Check if date is in same month and return multiplier."""
    month_cmp = compare_dates_by_month(current_date, date)
    return 1 if month_cmp >= 0 and month_cmp != THE_EDGE_CASE else 0


def _process_income_item(
    amount: float, current_date: str, date: str
) -> tuple[float, float]:
    """Process single income item."""
    cap_factor = _check_income_date(current_date, date)
    month_factor = _check_month_date(current_date, date)
    return amount * cap_factor, amount * month_factor


def _sum_income_data(
    capitals: list[tuple[float, float]],
) -> tuple[float, float]:
    """Sum income capital and receipts."""
    total_capital = sum(cap for cap, _ in capitals)
    total_receipts = sum(rec for _, rec in capitals)
    return total_capital, total_receipts


def _accumulate_income(
    receipts_list: list[tuple[float, str]], date: str
) -> tuple[float, float]:
    """Accumulate income data."""
    capitals = [
        _process_income_item(amount, current_date, date)
        for amount, current_date in receipts_list
    ]
    return _sum_income_data(capitals)


def _check_expense_date(current_date: str, date: str) -> int:
    """Check if expense date is within range and return multiplier."""
    return 1 if compare_dates(current_date, date) >= 0 else 0


def _update_categories(
    month_factor: int, category: str, amount: float, categories: dict[str, float]
) -> None:
    """Update category amounts if in month range."""
    if month_factor:
        current = categories.get(category, DEFAULT_ZERO)
        categories[category] = current + amount


def _process_expense_item(
    category: str,
    amount: float,
    current_date: str,
    date: str,
    categories: dict[str, float],
) -> tuple[float, float]:
    """Process single expense item."""
    cap_factor = _check_expense_date(current_date, date)
    month_factor = _check_month_date(current_date, date)
    _update_categories(month_factor, category, amount, categories)
    return amount * cap_factor, amount * month_factor


def _sum_expense_data(
    expenses_data: list[tuple[float, float]],
) -> tuple[float, float]:
    """Sum expense capital and expenses."""
    total_capital = sum(cap for cap, _ in expenses_data)
    total_expenses = sum(exp for _, exp in expenses_data)
    return total_capital, total_expenses


def _create_expenses_data(
    expenses_list: list[tuple[str, float, str]], date: str,
    categories: dict[str, float],
) -> list[tuple[float, float]]:
    """Create expenses data list."""
    return [
        _process_expense_item(category, amount, current_date, date, categories)
        for category, amount, current_date in expenses_list
    ]


def _accumulate_expenses(
    expenses_list: list[tuple[str, float, str]], date: str
) -> tuple[float, float, dict[str, float]]:
    """Accumulate expense data."""
    categories: dict[str, float] = {}
    expenses_data = _create_expenses_data(expenses_list, date, categories)
    total_capital, total_expenses = _sum_expense_data(expenses_data)
    return total_capital, total_expenses, categories


def _print_statistics_header(date: str) -> None:
    """Print statistics header."""
    print(f"Ваша статистика по состоянию на {date}:")


def _print_capital(total_capital: float) -> None:
    """Print capital information."""
    print(f"Суммарный капитал: {total_capital:.2f} рублей")


def _print_profit_loss(receipts: float, expenses: float) -> None:
    """Print profit or loss information."""
    difference = receipts - expenses
    if difference >= 0:
        print(f"В этом месяце прибыль составила {difference:.2f} рублей")  # noqa: RUF001
    else:
        loss = -difference
        print(f"В этом месяце убыток составил {loss:.2f} рублей")  # noqa: RUF001


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


def _display_stats(
    date: str,
    total_capital: float,
    receipts: float,
    expenses: float,
    categories: dict[str, float],
) -> None:
    """Display all statistics."""
    _print_statistics_header(date)
    _print_capital(total_capital)
    _print_profit_loss(receipts, expenses)
    _print_income_expense(receipts, expenses)
    _print_categories(categories)


def _get_stats_values(
    income_capital: float, expense_capital: float,
) -> tuple[float, float, float, float]:
    """Get statistics values."""
    total_capital = income_capital + expense_capital
    return total_capital, income_capital, expense_capital, total_capital


def print_statistics(
    date: str,
    receipts_list: list[tuple[float, str]],
    expenses_list: list[tuple[str, float, str]],
) -> None:
    """Print statistics for the given date."""
    income_capital, receipts = _accumulate_income(receipts_list, date)
    expense_capital, expenses, categories = _accumulate_expenses(
        expenses_list, date
    )
    total_capital, _, _, _ = _get_stats_values(income_capital, expense_capital)
    _display_stats(date, total_capital, receipts, expenses, categories)


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


def _handle_income(line: str, receipts_list: list[tuple[float, str]]) -> None:
    """Handle income command."""
    adding_income(line, receipts_list)
    print(OP_SUCCESS_MSG)


def _handle_cost(line: str, expenses_list: list[tuple[str, float, str]]) -> None:
    """Handle cost command."""
    adding_an_expense(line, expenses_list)
    print(OP_SUCCESS_MSG)


def _handle_stats(
    line: str,
    receipts_list: list[tuple[float, str]],
    expenses_list: list[tuple[str, float, str]],
) -> None:
    """Handle stats command."""
    blocks = line.split(" ")
    date = blocks[1]
    print_statistics(date, receipts_list, expenses_list)


def _process_command(
    validate: str,
    line: str,
    receipts_list: list[tuple[float, str]],
    expenses_list: list[tuple[str, float, str]],
) -> None:
    """Process validated command."""
    if validate == "income":
        _handle_income(line, receipts_list)
    elif validate == "cost":
        _handle_cost(line, expenses_list)
    elif validate == "stats":
        _handle_stats(line, receipts_list, expenses_list)


def operation_validation(operation: str) -> str:
    blocks = operation.split(" ")
    if len(blocks) > LEN_BIG_BLOCKS or len(blocks) == 1:
        return UNKNOWN_COMMAND_MSG

    if blocks[0] == "income" and len(blocks) == LEN_BLOCKS:
        return _validate_income(blocks)
    if blocks[0] == "cost" and len(blocks) == LEN_BIG_BLOCKS:
        return _validate_cost(blocks)
    if blocks[0] == "stats" and len(blocks) == LEN_SMALL_BLOCKS:
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
        error_messages = {
            UNKNOWN_COMMAND_MSG,
            NONPOSITIVE_VALUE_MSG,
            INCORRECT_DATE_MSG,
        }
        if validate in error_messages:
            print(validate)
            continue
        _process_command(validate, line, receipts_list, expenses_list)


if __name__ == "__main__":
    main()

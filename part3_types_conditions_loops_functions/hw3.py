#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"

DATE_LENGTH = 10
MAX_MONTH = 12
INCOME_ARGS_COUNT = 3
COST_CATEGORIES_ARGS_COUNT = 2
COST_ARGS_COUNT = 4
STATS_ARGS_COUNT = 2
FEBRUARY_MONTH = 2
LEAP_FEBRUARY_DAYS = 29

TX_AMOUNT_KEY = "amount"
TX_DATE_KEY = "date"
TX_CATEGORY_KEY = "category"
TOTAL_INCOME_KEY = "income"
TOTAL_EXPENSES_KEY = "expenses"
TOTAL_CAPITAL_KEY = "capital"

type DateTuple = tuple[int, int, int]
type TotalsMap = dict[str, float]
type CategoryExpensesMap = dict[str, float]
type StatsData = tuple[TotalsMap, CategoryExpensesMap]

DAYS_IN_MONTH = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}


EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("Misc",),
}


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    if year % 4 != 0:
        return False
    if year % 100 != 0:
        return True
    return year % 400 == 0


def _extract_date_digits(maybe_dt: str) -> DateTuple | None:
    day_part = maybe_dt[:2]
    month_part = maybe_dt[3:5]
    year_part = maybe_dt[6:]
    if not (day_part.isdigit() and month_part.isdigit() and year_part.isdigit()):
        return None
    return int(day_part), int(month_part), int(year_part)


def _is_valid_day(day: int, month: int, year: int) -> bool:
    max_day = DAYS_IN_MONTH[month]
    if month == FEBRUARY_MONTH and is_leap_year(year):
        max_day = LEAP_FEBRUARY_DAYS
    return 1 <= day <= max_day


def extract_date(maybe_dt: str) -> DateTuple | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    parsed_date: DateTuple | None = None
    if (
        len(maybe_dt) == DATE_LENGTH
        and maybe_dt[2] == "-"
        and maybe_dt[5] == "-"
    ):
        parsed_date = _extract_date_digits(maybe_dt)

    if parsed_date is None:
        return None
    day, month, year = parsed_date

    if year < 1 or month < 1 or month > MAX_MONTH:
        return None

    return (day, month, year) if _is_valid_day(day, month, year) else None


def _split_sign(raw_amount: str) -> tuple[int, str] | None:
    if not raw_amount:
        return None

    sign = 1
    start_index = 0
    if raw_amount[0] == "-":
        sign = -1
        start_index = 1
    elif raw_amount[0] == "+":
        start_index = 1

    numeric_part = raw_amount[start_index:]
    if not numeric_part:
        return None
    return sign, numeric_part


def _parse_decimal_parts(value: str) -> tuple[str, str] | None:
    integer_part, fractional_part = value.split(".", maxsplit=1)
    if not integer_part or not fractional_part:
        return None
    if not (integer_part.isdigit() and fractional_part.isdigit()):
        return None
    return integer_part, fractional_part


def _parse_unsigned_decimal(value: str) -> float | None:
    normalized = value.replace(",", ".")
    if normalized.count(".") > 1:
        return None
    if "." not in normalized:
        return float(int(normalized)) if normalized.isdigit() else None

    parsed_parts = _parse_decimal_parts(normalized)
    if parsed_parts is None:
        return None

    integer_part: str
    fractional_part: str
    integer_part, fractional_part = parsed_parts
    fractional_divisor = float(10 ** len(fractional_part))
    return float(int(integer_part)) + (int(fractional_part) / fractional_divisor)


def _extract_amount(raw_amount: str) -> float | None:
    signed_amount = _split_sign(raw_amount)
    if signed_amount is None:
        return None

    sign, numeric_part = signed_amount
    parsed_amount = _parse_unsigned_decimal(numeric_part)
    if parsed_amount is None:
        return None
    return sign * parsed_amount


def _is_valid_cost_category(category_name: str) -> bool:
    if category_name.count("::") != 1:
        return False
    common_category, target_category = category_name.split("::", maxsplit=1)
    if not common_category or not target_category:
        return False
    if common_category not in EXPENSE_CATEGORIES:
        return False
    return target_category in EXPENSE_CATEGORIES[common_category]


def _date_key(date_value: DateTuple) -> DateTuple:
    day, month, year = date_value
    return year, month, day


def _is_same_month(date1: DateTuple, date2: DateTuple) -> bool:
    if date1[2] != date2[2]:
        return False
    return date1[1] == date2[1]


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({TX_AMOUNT_KEY: amount, TX_DATE_KEY: parsed_date})
    return OP_SUCCESS_MSG


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    if not _is_valid_cost_category(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY

    financial_transactions_storage.append(
        {TX_CATEGORY_KEY: category_name, TX_AMOUNT_KEY: amount, TX_DATE_KEY: parsed_date}
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    return "\n".join(
        f"{common}::{target}"
        for common, targets in EXPENSE_CATEGORIES.items()
        for target in targets
    )


def _format_amount(amount: float) -> str:
    if amount.is_integer():
        return str(int(amount))
    return f"{amount:.2f}".rstrip("0").rstrip(".")


def _is_relevant_transaction(transaction: dict[str, Any], report_key: DateTuple) -> bool:
    if not transaction:
        return False
    transaction_date = transaction.get(TX_DATE_KEY)
    if not isinstance(transaction_date, tuple):
        return False
    return _date_key(transaction_date) <= report_key


def _apply_income(
    amount: float,
    transaction_date: DateTuple,
    parsed_report_date: DateTuple,
    totals: TotalsMap,
) -> None:
    totals[TOTAL_CAPITAL_KEY] += amount
    if _is_same_month(transaction_date, parsed_report_date):
        totals[TOTAL_INCOME_KEY] += amount


def _update_stats_by_transaction(
    transaction: dict[str, Any],
    parsed_report_date: DateTuple,
    report_key: DateTuple,
    totals: TotalsMap,
    month_category_expenses: CategoryExpensesMap,
) -> None:
    if not _is_relevant_transaction(transaction, report_key):
        return

    amount = float(transaction[TX_AMOUNT_KEY])
    transaction_date = transaction[TX_DATE_KEY]
    category_name = transaction.get(TX_CATEGORY_KEY)
    if category_name is None:
        _apply_income(amount, transaction_date, parsed_report_date, totals)
        return

    totals[TOTAL_CAPITAL_KEY] -= amount
    if _is_same_month(transaction_date, parsed_report_date):
        totals[TOTAL_EXPENSES_KEY] += amount
        category_title = category_name.split("::", maxsplit=1)[1]
        month_category_expenses[category_title] = (
            month_category_expenses.get(category_title, 0) + amount
        )


def _collect_stats(parsed_report_date: DateTuple) -> StatsData:
    totals: TotalsMap = {
        TOTAL_INCOME_KEY: 0,
        TOTAL_EXPENSES_KEY: 0,
        TOTAL_CAPITAL_KEY: 0,
    }
    month_category_expenses: CategoryExpensesMap = {}
    report_key = _date_key(parsed_report_date)

    for transaction in financial_transactions_storage:
        _update_stats_by_transaction(
            transaction,
            parsed_report_date,
            report_key,
            totals,
            month_category_expenses,
        )

    return totals, month_category_expenses


def _build_stats_summary_lines(report_date: str, totals: TotalsMap) -> list[str]:
    month_balance = totals[TOTAL_INCOME_KEY] - totals[TOTAL_EXPENSES_KEY]
    month_result = "profit" if month_balance >= 0 else "loss"
    return [
        f"Your statistics as of {report_date}:",
        f"Total capital: {totals[TOTAL_CAPITAL_KEY]:.2f} rubles",
        f"This month, the {month_result} amounted to {abs(month_balance):.2f} rubles.",
        f"Income: {totals[TOTAL_INCOME_KEY]:.2f} rubles",
        f"Expenses: {totals[TOTAL_EXPENSES_KEY]:.2f} rubles",
        "",
        "Details (category: amount):",
    ]


def _append_sorted_category_lines(lines: list[str], month_category_expenses: CategoryExpensesMap) -> None:
    sorted_categories = sorted(month_category_expenses.items(), key=lambda item: item[0])
    for index, (category_title, amount) in enumerate(sorted_categories, start=1):
        lines.append(f"{index}. {category_title}: {_format_amount(amount)}")


def _build_stats_lines(
    report_date: str,
    totals: TotalsMap,
    month_category_expenses: CategoryExpensesMap,
) -> list[str]:
    lines = _build_stats_summary_lines(report_date, totals)
    _append_sorted_category_lines(lines, month_category_expenses)
    return lines


def stats_handler(report_date: str) -> str:
    parsed_report_date = extract_date(report_date)
    if parsed_report_date is None:
        return INCORRECT_DATE_MSG

    totals, month_category_expenses = _collect_stats(parsed_report_date)
    return "\n".join(_build_stats_lines(report_date, totals, month_category_expenses))


def _handle_income_command(command_parts: list[str]) -> list[str]:
    if len(command_parts) != INCOME_ARGS_COUNT:
        return [UNKNOWN_COMMAND_MSG]

    raw_amount = command_parts[1]
    date_value = command_parts[2]

    parsed_amount = _extract_amount(raw_amount)
    if parsed_amount is None:
        return [UNKNOWN_COMMAND_MSG]
    return [income_handler(parsed_amount, date_value)]


def _handle_cost_command(command_parts: list[str]) -> list[str]:
    if (
        len(command_parts) == COST_CATEGORIES_ARGS_COUNT
        and command_parts[1] == "categories"
    ):
        return [cost_categories_handler()]

    if len(command_parts) != COST_ARGS_COUNT:
        return [UNKNOWN_COMMAND_MSG]

    parsed_amount = _extract_amount(command_parts[2])
    if parsed_amount is None:
        return [UNKNOWN_COMMAND_MSG]

    result = cost_handler(command_parts[1], parsed_amount, command_parts[3])
    responses = [result]
    if result == NOT_EXISTS_CATEGORY:
        responses.append(cost_categories_handler())
    return responses


def _handle_stats_command(command_parts: list[str]) -> list[str]:
    if len(command_parts) != STATS_ARGS_COUNT:
        return [UNKNOWN_COMMAND_MSG]
    date_value = command_parts[1]
    return [stats_handler(date_value)]


def _handle_command(command_parts: list[str]) -> list[str]:
    if not command_parts:
        return [UNKNOWN_COMMAND_MSG]

    root_command = command_parts[0]
    if root_command == "income":
        return _handle_income_command(command_parts)
    if root_command == "cost":
        return _handle_cost_command(command_parts)
    if root_command == "stats":
        return _handle_stats_command(command_parts)
    return [UNKNOWN_COMMAND_MSG]


def main() -> None:
    command_parts = input().strip().split()
    for response in _handle_command(command_parts):
        print(response)


if __name__ == "__main__":
    main()

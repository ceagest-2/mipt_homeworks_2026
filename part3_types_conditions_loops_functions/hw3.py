#!/usr/bin/env python

from typing import Any

UNKNOWN_COMMAND_MSG = "Unknown command!"
NONPOSITIVE_VALUE_MSG = "Value must be grater than zero!"
INCORRECT_DATE_MSG = "Invalid date!"
NOT_EXISTS_CATEGORY = "Category not exists!"
OP_SUCCESS_MSG = "Added"


EXPENSE_CATEGORIES = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": (),
}


financial_transactions_storage: list[dict[str, Any]] = []


def is_leap_year(year: int) -> bool:
    """
    Для заданного года определяет: високосный (True) или невисокосный (False).

    :param int year: Проверяемый год
    :return: Значение високосности.
    :rtype: bool
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
    Парсит дату формата DD-MM-YYYY из строки.

    :param str maybe_dt: Проверяемая строка
    :return: typle формата (день, месяц, год) или None, если дата неправильная.
    :rtype: tuple[int, int, int] | None
    """
    if len(maybe_dt) != 10:
        return None

    if maybe_dt[2] != "-" or maybe_dt[5] != "-":
        return None

    day_part = maybe_dt[:2]
    month_part = maybe_dt[3:5]
    year_part = maybe_dt[6:]

    if not (day_part.isdigit() and month_part.isdigit() and year_part.isdigit()):
        return None

    day = int(day_part)
    month = int(month_part)
    year = int(year_part)

    if year < 1 or month < 1 or month > 12:
        return None

    days_in_month = {
        1: 31,
        2: 29 if is_leap_year(year) else 28,
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
    max_day = days_in_month[month]
    if day < 1 or day > max_day:
        return None

    return day, month, year


def _extract_amount(raw_amount: str) -> float | None:
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

    separator_count = 0
    for char in numeric_part:
        if char in ".,":
            separator_count += 1
        elif not char.isdigit():
            return None

    if separator_count > 1:
        return None

    normalized = numeric_part.replace(",", ".")
    if "." in normalized:
        integer_part, fractional_part = normalized.split(".", maxsplit=1)
        if not integer_part or not fractional_part:
            return None
        if not (integer_part.isdigit() and fractional_part.isdigit()):
            return None
        integer_value = int(integer_part)
        fractional_value = int(fractional_part)
        divisor = 10 ** len(fractional_part)
        return sign * (integer_value + (fractional_value / divisor))

    if not normalized.isdigit():
        return None
    return sign * float(int(normalized))


def _is_valid_cost_category(category_name: str) -> bool:
    if category_name.count("::") != 1:
        return False
    common_category, target_category = category_name.split("::", maxsplit=1)
    if not common_category or not target_category:
        return False
    if common_category not in EXPENSE_CATEGORIES:
        return False
    return target_category in EXPENSE_CATEGORIES[common_category]


def _date_key(date_value: tuple[int, int, int]) -> tuple[int, int, int]:
    day, month, year = date_value
    return year, month, day


def _is_same_month(date1: tuple[int, int, int], date2: tuple[int, int, int]) -> bool:
    return date1[1] == date2[1] and date1[2] == date2[2]


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG

    parsed_date = extract_date(income_date)
    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append({"amount": amount, "date": parsed_date})
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
        {"category": category_name, "amount": amount, "date": parsed_date}
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


def stats_handler(report_date: str) -> str:
    parsed_report_date = extract_date(report_date)
    if parsed_report_date is None:
        return INCORRECT_DATE_MSG

    month_income = 0.0
    month_expenses = 0.0
    total_capital = 0.0
    month_category_expenses: dict[str, float] = {}

    report_key = _date_key(parsed_report_date)
    for transaction in financial_transactions_storage:
        if not transaction:
            continue

        transaction_date = transaction.get("date")
        if not isinstance(transaction_date, tuple):
            continue

        if _date_key(transaction_date) > report_key:
            continue

        amount = float(transaction["amount"])
        category_name = transaction.get("category")

        if category_name is None:
            total_capital += amount
            if _is_same_month(transaction_date, parsed_report_date):
                month_income += amount
            continue

        total_capital -= amount
        if _is_same_month(transaction_date, parsed_report_date):
            month_expenses += amount
            category_title = category_name.split("::", maxsplit=1)[1]
            month_category_expenses[category_title] = (
                month_category_expenses.get(category_title, 0.0) + amount
            )

    month_balance = month_income - month_expenses
    month_result = "profit" if month_balance >= 0 else "loss"
    month_result_amount = abs(month_balance)

    lines = [
        f"Your statistics as of {report_date}:",
        f"Total capital: {total_capital:.2f} rubles",
        (
            f"This month, the {month_result} amounted to "
            f"{month_result_amount:.2f} rubles."
        ),
        f"Income: {month_income:.2f} rubles",
        f"Expenses: {month_expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    sorted_categories = sorted(
        month_category_expenses.items(),
        key=lambda item: item[0],
    )
    for index, (category_title, amount) in enumerate(sorted_categories, start=1):
        lines.append(f"{index}. {category_title}: {_format_amount(amount)}")

    return "\n".join(lines)


def main() -> None:
    command = input().strip()
    if not command:
        print(UNKNOWN_COMMAND_MSG)
        return

    command_parts = command.split()
    root_command = command_parts[0]

    if root_command == "income":
        if len(command_parts) != 3:
            print(UNKNOWN_COMMAND_MSG)
            return

        raw_amount = command_parts[1]
        date_value = command_parts[2]

        parsed_amount = _extract_amount(raw_amount)
        if parsed_amount is None:
            print(UNKNOWN_COMMAND_MSG)
            return

        print(income_handler(parsed_amount, date_value))
        return

    if root_command == "cost":
        if len(command_parts) == 2 and command_parts[1] == "categories":
            print(cost_categories_handler())
            return

        if len(command_parts) != 4:
            print(UNKNOWN_COMMAND_MSG)
            return

        category_name = command_parts[1]
        raw_amount = command_parts[2]
        date_value = command_parts[3]

        parsed_amount = _extract_amount(raw_amount)
        if parsed_amount is None:
            print(UNKNOWN_COMMAND_MSG)
            return

        result = cost_handler(category_name, parsed_amount, date_value)
        print(result)
        if result == NOT_EXISTS_CATEGORY:
            print(cost_categories_handler())
        return

    if root_command == "stats":
        if len(command_parts) != 2:
            print(UNKNOWN_COMMAND_MSG)
            return

        date_value = command_parts[1]
        print(stats_handler(date_value))
        return

    print(UNKNOWN_COMMAND_MSG)


if __name__ == "__main__":
    main()

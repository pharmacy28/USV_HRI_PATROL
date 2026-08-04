from __future__ import annotations

import re


CN_NUMBERS = {
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}
GRID_COLUMNS = "ABCDEFGH"
GRID_ROWS = "12345678"
GRID_ROW_ALIASES = {
    key: str(value)
    for key, value in CN_NUMBERS.items()
    if value <= 8
}
NAVIGATION_WORDS = ["到", "去", "前往", "进入", "抵达", "航向", "开到", "移动到"]
SELECTION_WORDS = ["选择", "切换", "控制", "操作"]
NUMBER_TOKEN = r"(?:\d{1,2}|[一二两三四五六七八九十])"
NUMBER_START = r"(?<![0-9一二两三四五六七八九十])"
NUMBER_BOUNDARY = r"(?![0-9一二两三四五六七八九十])"


def parse_number(token: str) -> int | None:
    try:
        value = int(token)
    except ValueError:
        value = CN_NUMBERS.get(token)
    return value if value is not None and 1 <= value <= 99 else None


def _vehicle_numbers(text: str) -> set[int]:
    tokens: list[str] = []
    patterns = [
        rf"(?<![A-Za-z0-9])wam[\s_-]*v[\s_-]*"
        rf"({NUMBER_TOKEN}){NUMBER_BOUNDARY}\s*号?",
        rf"{NUMBER_START}(?:第\s*)?({NUMBER_TOKEN}){NUMBER_BOUNDARY}"
        rf"\s*号?\s*(?:艘\s*)?(?:船|艇)",
        rf"(?:船|艇)\s*(?:第\s*)?({NUMBER_TOKEN})"
        rf"{NUMBER_BOUNDARY}\s*号?",
    ]
    for pattern in patterns:
        tokens.extend(re.findall(pattern, text, flags=re.IGNORECASE))
    return {
        value
        for token in tokens
        if (value := parse_number(token)) is not None
    }


def parse_vehicle(
    text: str,
    target_names: list[str],
) -> tuple[str | None, str | None]:
    numbers = _vehicle_numbers(text)
    if len(numbers) > 1:
        return None, "ambiguous_vehicle"
    if not numbers:
        return None, "missing_vehicle"
    candidate = f"wamv_{next(iter(numbers)):02d}"
    if candidate not in target_names:
        return None, "unknown_vehicle"
    return candidate, None


def parse_cell(text: str) -> tuple[str | None, str | None]:
    matches = re.findall(
        rf"(?<![A-Za-z])([A-Ia-i])\s*(?:区|区域)?\s*"
        rf"({NUMBER_TOKEN}){NUMBER_BOUNDARY}",
        text,
    )
    cells = set()
    invalid = False
    for column, row_token in matches:
        column = column.upper()
        row = GRID_ROW_ALIASES.get(row_token, row_token)
        if column in GRID_COLUMNS and row in GRID_ROWS:
            cells.add(f"{column}{row}")
        else:
            invalid = True
    if len(cells) > 1:
        return None, "ambiguous_cell"
    if invalid:
        return None, "invalid_cell"
    if cells:
        return next(iter(cells)), None
    return None, "invalid_cell" if invalid else "missing_cell"


def parse_grid_assignment(text: str, target_names: list[str]) -> dict | None:
    if not any(word in text for word in NAVIGATION_WORDS):
        return None
    vehicle, vehicle_error = parse_vehicle(text, target_names)
    cell, cell_error = parse_cell(text)
    selection = any(word in text for word in SELECTION_WORDS)
    if cell_error == "missing_cell" and selection:
        return None
    return {
        "type": "grid_goal",
        "target": vehicle,
        "cell": cell,
        "errors": [error for error in [vehicle_error, cell_error] if error],
    }


def is_manual_selection(text: str) -> bool:
    if not any(word in text for word in SELECTION_WORDS):
        return False
    _cell, cell_error = parse_cell(text)
    return cell_error == "missing_cell"

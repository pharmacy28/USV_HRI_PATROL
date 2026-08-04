from usv_overview.voice_intent import (
    is_manual_selection,
    parse_cell,
    parse_grid_assignment,
    parse_vehicle,
)


TARGETS = [f"wamv_{index:02d}" for index in range(1, 11)]


def test_chinese_assignment():
    action = parse_grid_assignment("二号船去E5", TARGETS)
    assert action == {
        "type": "grid_goal",
        "target": "wamv_02",
        "cell": "E5",
        "errors": [],
    }


def test_wamv_assignment_variants():
    action = parse_grid_assignment("WAM-V 2 去 e 五", TARGETS)
    assert action["target"] == "wamv_02"
    assert action["cell"] == "E5"
    assert action["errors"] == []

    action = parse_grid_assignment("WAMV十号到A1", TARGETS)
    assert action["target"] == "wamv_10"
    assert action["cell"] == "A1"
    assert action["errors"] == []


def test_cell_digit_is_not_vehicle_number():
    action = parse_grid_assignment("船去E5", TARGETS)
    assert action["target"] is None
    assert "missing_vehicle" in action["errors"]

    vehicle, error = parse_vehicle("选择E5", TARGETS)
    assert vehicle is None
    assert error == "missing_vehicle"


def test_reject_ambiguous_or_invalid_assignment():
    action = parse_grid_assignment("二号船和三号船去E5", TARGETS)
    assert "ambiguous_vehicle" in action["errors"]
    assert parse_cell("去I1") == (None, "invalid_cell")
    assert parse_cell("去A9") == (None, "invalid_cell")
    assert parse_cell("去A10") == (None, "invalid_cell")
    assert parse_cell("去A1再到B2") == (None, "ambiguous_cell")


def test_vehicle_number_is_not_truncated():
    assert parse_vehicle("WAMV11去E5", TARGETS) == (None, "unknown_vehicle")
    assert parse_vehicle("十一号船去E5", TARGETS) == (None, "missing_vehicle")


def test_region_separator_is_normalized():
    action = parse_grid_assignment("二号船去E区5", TARGETS)
    assert action["target"] == "wamv_02"
    assert action["cell"] == "E5"
    assert action["errors"] == []


def test_switch_to_vehicle_is_manual_selection_not_mission():
    assert parse_grid_assignment("切换到二号船", TARGETS) is None
    assert is_manual_selection("切换到二号船") is True

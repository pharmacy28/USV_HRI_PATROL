from usv_overview.mission_contract import build_request, extract_grid_action


TARGETS = [f"wamv_{index:02d}" for index in range(1, 11)]


def test_build_valid_request_and_status():
    request, status = build_request(
        {"type": "grid_goal", "target": "wamv_02", "cell": "E5", "errors": []},
        TARGETS,
        "request-1",
        123,
    )
    assert request == {
        "schema": "usv_mission_request/v1",
        "request_id": "request-1",
        "stamp_ns": 123,
        "source": "voice",
        "task": "navigate_to_cell",
        "vehicle": "wamv_02",
        "goal": {"grid_id": "overview_sector_8x8", "cell": "E5"},
    }
    assert status["state"] == "accepted"
    assert status["request_id"] == request["request_id"]


def test_reject_incomplete_request():
    request, status = build_request(
        {
            "type": "grid_goal",
            "target": None,
            "cell": "E5",
            "errors": ["missing_vehicle"],
        },
        TARGETS,
        "request-2",
        456,
    )
    assert request is None
    assert status["state"] == "rejected"
    assert status["reason_code"] == "missing_vehicle"
    assert status["detail"] == "missing_vehicle"


def test_reject_unknown_vehicle_and_cell():
    request, status = build_request(
        {"type": "grid_goal", "target": "wamv_11", "cell": "I9", "errors": []},
        TARGETS,
        "request-3",
        789,
    )
    assert request is None
    assert status["state"] == "rejected"
    assert status["detail"] == "unknown_vehicle,invalid_cell"


def test_extract_exactly_one_grid_action():
    grid_action = {
        "type": "grid_goal",
        "target": "wamv_02",
        "cell": "E5",
        "errors": [],
    }
    intent = {
        "actions": [
            {"type": "set_page", "page": "overview"},
            grid_action,
            {"type": "toggle_grid"},
        ]
    }
    assert extract_grid_action(intent) == (grid_action, None)
    assert extract_grid_action(
        {"actions": [{"type": "unhandled"}]}
    ) == (None, None)


def test_reject_multiple_grid_actions_or_malformed_intent():
    action = {
        "type": "grid_goal",
        "target": "wamv_02",
        "cell": "E5",
        "errors": [],
    }
    assert extract_grid_action({"actions": [action, dict(action)]}) == (
        None,
        "ambiguous_assignment",
    )
    assert extract_grid_action([]) == (None, "invalid_intent")
    assert extract_grid_action(
        {"actions": "not-a-list"}
    ) == (None, "invalid_intent")

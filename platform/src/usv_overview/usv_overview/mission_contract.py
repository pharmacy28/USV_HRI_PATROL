from __future__ import annotations

import re


CELL_PATTERN = re.compile(r"^[A-H][1-8]$")
VEHICLE_ERRORS = {"missing_vehicle", "unknown_vehicle", "ambiguous_vehicle"}
CELL_ERRORS = {"missing_cell", "invalid_cell", "ambiguous_cell"}


def extract_grid_action(intent: object) -> tuple[dict | None, str | None]:
    """Return the sole grid assignment and ignore unrelated voice actions."""
    if not isinstance(intent, dict):
        return None, "invalid_intent"

    actions = intent.get("actions", [])
    if not isinstance(actions, list):
        return None, "invalid_intent"

    grid_actions = [
        action
        for action in actions
        if isinstance(action, dict) and action.get("type") == "grid_goal"
    ]
    if len(grid_actions) > 1:
        return None, "ambiguous_assignment"
    if not grid_actions:
        return None, None
    return grid_actions[0], None


def build_request(
    action: dict,
    target_names: list[str],
    request_id: str,
    stamp_ns: int,
) -> tuple[dict | None, dict]:
    vehicle = action.get("target")
    cell = str(action.get("cell") or "").upper()
    errors = list(action.get("errors") or [])

    if not VEHICLE_ERRORS.intersection(errors):
        if not vehicle:
            errors.append("missing_vehicle")
        elif vehicle not in target_names:
            errors.append("unknown_vehicle")
    if not CELL_ERRORS.intersection(errors):
        if not cell:
            errors.append("missing_cell")
        elif not CELL_PATTERN.fullmatch(cell):
            errors.append("invalid_cell")

    errors = list(dict.fromkeys(errors))
    status = {
        "schema": "usv_mission_status/v1",
        "request_id": request_id,
        "stamp_ns": int(stamp_ns),
        "vehicle": vehicle,
        "state": "rejected" if errors else "accepted",
        "reason_code": errors[0] if errors else "",
        "detail": ",".join(errors),
    }
    if errors:
        return None, status

    request = {
        "schema": "usv_mission_request/v1",
        "request_id": request_id,
        "stamp_ns": int(stamp_ns),
        "source": "voice",
        "task": "navigate_to_cell",
        "vehicle": vehicle,
        "goal": {
            "grid_id": "overview_sector_8x8",
            "cell": cell,
        },
    }
    return request, status

from usv_overview.world_scan import sector_grid


def test_sector_grid_has_stable_world_definition():
    bounds = {"min_x": -400.0, "max_x": 400.0, "min_y": -400.0, "max_y": 400.0}
    grid = sector_grid(bounds)
    assert grid == {
        "id": "overview_sector_8x8",
        "frame_id": "world",
        "bounds": bounds,
        "columns": "ABCDEFGH",
        "rows": "12345678",
        "column_origin": "min_x",
        "row_origin": "max_y",
    }

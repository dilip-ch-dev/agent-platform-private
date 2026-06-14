from unittest.mock import MagicMock, patch


def test_dev_starts_with_reload() -> None:
    with patch("uvicorn.run") as mock_run:
        from app.cli import dev

        dev()
        mock_run.assert_called_once_with(
            "app.main:app", host="127.0.0.1", port=8000, reload=True
        )


def test_start_binds_all_interfaces() -> None:
    with patch("uvicorn.run") as mock_run:
        from app.cli import start

        start()
        mock_run.assert_called_once_with("app.main:app", host="0.0.0.0", port=8000)


def test_ui_launches_gradio() -> None:
    mock_demo = MagicMock()
    import sys

    mock_module = MagicMock()
    mock_module.demo = mock_demo
    with patch.dict(sys.modules, {"ui.app": mock_module}):
        from app.cli import ui

        ui()
        mock_demo.launch.assert_called_once_with(
            server_name="127.0.0.1", server_port=7860
        )


def test_smoke_runs_script() -> None:
    with patch("runpy.run_path") as mock_run:
        from app.cli import smoke

        smoke()
        mock_run.assert_called_once_with("scripts/smoke.py", run_name="__main__")

"""Console entry points (see [project.scripts] in pyproject.toml).

Names are prefixed ``bt-`` so the installed wheel never shadows common
binaries like ``dev`` or ``start`` on a teammate's PATH.
"""

from pathlib import Path

import uvicorn

_REPO_ROOT = Path(__file__).resolve().parent.parent


def dev() -> None:
    """Start API in development mode with auto-reload (bt-dev)."""
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


def start() -> None:
    """Start API in production mode (bt-start)."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)


def ui() -> None:
    """Start the Gradio demo UI (bt-ui)."""
    from ui.app import demo

    demo.launch(server_name="127.0.0.1", server_port=7860)


def smoke() -> None:
    """Run the smoke test (bt-smoke). Path is anchored to the repo root, not cwd."""
    import runpy

    runpy.run_path(str(_REPO_ROOT / "scripts" / "smoke.py"), run_name="__main__")

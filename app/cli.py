import uvicorn


def dev() -> None:
    """Start API in development mode with auto-reload."""
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


def start() -> None:
    """Start API in production mode."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)


def ui() -> None:
    """Start the Gradio demo UI."""
    from ui.app import demo

    demo.launch(server_name="127.0.0.1", server_port=7860)


def smoke() -> None:
    """Run the smoke test."""
    import runpy

    runpy.run_path("scripts/smoke.py", run_name="__main__")

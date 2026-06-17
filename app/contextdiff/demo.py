from __future__ import annotations

from pathlib import Path

from app.contextdiff.service import load_request_from_json, run_contextdiff
from packages.contracts.contextdiff import ContextDiffReport, ContextDiffRequest

_SEED_PATH = Path("eval/contextdiff_seed.json")


def load_seed_demo(path: Path = _SEED_PATH) -> ContextDiffRequest:
    return load_request_from_json(path)


def run_seed_demo(path: Path = _SEED_PATH) -> ContextDiffReport:
    return run_contextdiff(load_seed_demo(path))

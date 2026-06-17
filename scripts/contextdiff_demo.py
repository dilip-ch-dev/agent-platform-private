"""Run the seeded ContextDiff demo and export JSON plus HTML reports."""

from pathlib import Path

from app.contextdiff.demo import run_seed_demo
from app.contextdiff.service import write_report


def main() -> None:
    report = run_seed_demo()
    json_path, html_path = write_report(report, Path("data/audit/contextdiff_demo"))
    print(f"Release status: {report.status}")
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")


if __name__ == "__main__":
    main()

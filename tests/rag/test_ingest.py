from __future__ import annotations

from pathlib import Path

from app.rag.chunker import chunk_text
from app.rag.ingest import build_chunks
from packages.contracts.schemas import Locator


class _FakePage:
    def __init__(self, text: str) -> None:
        self._text = text

    def extract_text(self) -> str:
        return self._text


class _FakeReader:
    def __init__(self, _path: str) -> None:
        self.pages = [_FakePage("PDF page one text"), _FakePage("")]


def test_pdf_extraction_has_locators(monkeypatch) -> None:
    monkeypatch.setattr("app.rag.ingest.PdfReader", _FakeReader)

    chunks = build_chunks("tests/fixtures/sample.pdf")

    assert chunks
    assert all(chunk.locator.page is not None for chunk in chunks)
    assert all(chunk.source_type == "pdf" for chunk in chunks)


def test_chunk_text_splits_long_text() -> None:
    chunks = chunk_text(
        text="word " * 4000,
        source_file="test.txt",
        source_type="txt",
        base_locator=Locator(char_start=0, char_end=100),
    )

    assert len(chunks) > 1
    assert all(chunk.token_count is not None and chunk.token_count > 0 for chunk in chunks)


def test_csv_row_locator(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text("name,role\nAda,Engineer\nTuring,Researcher\n", encoding="utf-8")

    chunks = build_chunks(str(csv_path))

    assert chunks
    assert all(chunk.locator.row is not None for chunk in chunks)
    assert all(chunk.source_type == "csv" for chunk in chunks)

from __future__ import annotations

from pathlib import Path

import pytest

from app.rag.chunker import chunk_text
from app.rag.ingest import (
    CsvExtractor,
    build_chunks,
    extract,
    extract_csv,
    extract_pdf,
    extract_txt,
)
from packages.contracts.schemas import Locator


class StubPdfPage:
    def __init__(self, text: str | None) -> None:
        self._text = text

    def extract_text(self) -> str | None:
        return self._text


class StubPdfReader:
    def __init__(self, path: str) -> None:
        assert path.endswith(".pdf"), f"Got {path!r}"
        self.pages = [StubPdfPage("PDF page one text"), StubPdfPage("")]


class StubPdfReaderAllBlank:
    def __init__(self, path: str) -> None:
        assert path.endswith(".pdf"), f"Got {path!r}"
        self.pages = [StubPdfPage(""), StubPdfPage("  \n "), StubPdfPage(None)]


class StubPdfReaderMixed:
    def __init__(self, path: str) -> None:
        assert path.endswith(".pdf"), f"Got {path!r}"
        self.pages = [
            StubPdfPage(""),
            StubPdfPage("Page two content"),
            StubPdfPage(None),
        ]


def test_pdf_extraction_has_locators(monkeypatch) -> None:
    monkeypatch.setattr("app.rag.ingest.PdfReader", StubPdfReader)

    chunks = build_chunks("tests/fixtures/sample.pdf")

    assert chunks
    assert len(chunks) == 1
    assert all(chunk.locator.page is not None for chunk in chunks)
    assert all(chunk.source_type == "pdf" for chunk in chunks)


def test_pdf_all_pages_blank_returns_empty(monkeypatch) -> None:
    monkeypatch.setattr("app.rag.ingest.PdfReader", StubPdfReaderAllBlank)
    assert extract_pdf("tests/fixtures/sample.pdf") == []


def test_pdf_mixed_blank_and_content_pages(monkeypatch) -> None:
    monkeypatch.setattr("app.rag.ingest.PdfReader", StubPdfReaderMixed)
    chunks = build_chunks("tests/fixtures/sample.pdf")
    assert len(chunks) == 1
    assert chunks[0].locator.page == 2


def test_chunk_text_splits_long_text() -> None:
    chunks = chunk_text(
        text="word " * 4000,
        source_file="test.txt",
        source_type="txt",
        base_locator=Locator(char_start=0, char_end=100),
    )

    assert len(chunks) > 1
    assert all(len(chunk.text) <= 1024 for chunk in chunks)
    assert all(
        chunk.token_count is not None and chunk.token_count > 0 for chunk in chunks
    )


def test_chunker_empty_returns_empty() -> None:
    assert chunk_text("", "a.txt", "txt", Locator(char_start=0, char_end=0)) == []


def test_chunker_whitespace_returns_empty() -> None:
    assert (
        chunk_text("  \n\t ", "a.txt", "txt", Locator(char_start=0, char_end=0)) == []
    )


def test_chunker_single_word_returns_single_chunk() -> None:
    chunks = chunk_text("hello", "a.txt", "txt", Locator(char_start=0, char_end=5))
    assert len(chunks) == 1
    assert chunks[0].text == "hello"


def test_chunker_chunk_ids_unique() -> None:
    chunks = chunk_text(
        "word " * 4000, "a.txt", "txt", Locator(char_start=0, char_end=100)
    )
    ids = [chunk.chunk_id for chunk in chunks]
    assert len(ids) == len(set(ids))


def test_chunker_preserves_source_fields_and_non_blank_text() -> None:
    chunks = chunk_text(
        "word " * 2000,
        source_file="my.txt",
        source_type="txt",
        base_locator=Locator(char_start=0, char_end=100),
    )
    assert chunks
    assert all(chunk.text.strip() != "" for chunk in chunks)
    assert all(chunk.source_file == "my.txt" for chunk in chunks)
    assert all(chunk.source_type == "txt" for chunk in chunks)


def test_chunker_source_unit_id_present_and_absent() -> None:
    with_unit = chunk_text(
        "hello world",
        source_file="a.txt",
        source_type="txt",
        base_locator=Locator(char_start=0, char_end=11),
        source_unit_id="unit-1",
    )
    without_unit = chunk_text(
        "hello world",
        source_file="a.txt",
        source_type="txt",
        base_locator=Locator(char_start=0, char_end=11),
    )

    assert with_unit[0].source_unit_ids == ["unit-1"]
    assert without_unit[0].source_unit_ids == []


def test_txt_normal_file_produces_chunks(tmp_path: Path) -> None:
    txt_path = tmp_path / "sample.txt"
    txt_path.write_text("Line one\nLine two\n", encoding="utf-8")
    chunks = build_chunks(str(txt_path))
    assert chunks


def test_txt_empty_file_returns_empty(tmp_path: Path) -> None:
    txt_path = tmp_path / "empty.txt"
    txt_path.write_text("", encoding="utf-8")
    assert extract_txt(str(txt_path)) == []


def test_txt_whitespace_only_file_returns_empty(tmp_path: Path) -> None:
    txt_path = tmp_path / "whitespace.txt"
    txt_path.write_text("   \n\t  \n", encoding="utf-8")
    assert extract_txt(str(txt_path)) == []


def test_txt_blank_lines_skipped_and_offsets_valid(tmp_path: Path) -> None:
    txt_path = tmp_path / "blank_lines.txt"
    txt_path.write_text("A\n\nB\n", encoding="utf-8")

    units = extract_txt(str(txt_path))

    assert len(units) == 2
    assert all(unit.text.strip() != "" for unit in units)
    assert all(
        unit.locator.char_start is not None and unit.locator.char_end is not None
        for unit in units
    )
    assert all(
        (unit.locator.char_end or 0) > (unit.locator.char_start or 0) for unit in units
    )


def test_txt_windows_crlf_offsets(tmp_path: Path) -> None:
    txt_path = tmp_path / "windows.txt"
    txt_path.write_bytes(b"12345678\r\nABCD\r\n")

    units = extract_txt(str(txt_path))

    assert len(units) == 2
    assert units[1].locator.char_start == 10


def test_txt_latin1_detected_no_crash(tmp_path: Path) -> None:
    txt_path = tmp_path / "latin1.txt"
    txt_path.write_bytes("caf\xe9\n".encode("latin-1"))

    units = extract_txt(str(txt_path))

    assert len(units) == 1
    assert "café" in units[0].text


def test_csv_row_locator(tmp_path: Path) -> None:
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(
        "name,role\nAda,Engineer\nTuring,Researcher\n", encoding="utf-8"
    )

    chunks = build_chunks(str(csv_path))

    assert chunks
    assert all(chunk.locator.row is not None for chunk in chunks)
    assert all(chunk.source_type == "csv" for chunk in chunks)


def test_csv_headers_only_returns_empty(tmp_path: Path) -> None:
    csv_path = tmp_path / "headers_only.csv"
    csv_path.write_text("name,role\n", encoding="utf-8")

    assert extract_csv(str(csv_path)) == []


def test_csv_blank_rows_skipped(tmp_path: Path) -> None:
    csv_path = tmp_path / "blank_rows.csv"
    csv_path.write_text("name,role\n,\nAda,Engineer\n,\n", encoding="utf-8")

    units = extract_csv(str(csv_path))

    assert len(units) == 1
    assert "Ada" in units[0].text
    assert "Engineer" in units[0].text


def test_csv_first_row_locator_is_zero(tmp_path: Path) -> None:
    csv_path = tmp_path / "row_locator.csv"
    csv_path.write_text("name,role\nAda,Engineer\n", encoding="utf-8")

    units = extract_csv(str(csv_path))

    assert len(units) == 1
    assert units[0].locator.row == 0


def test_csv_latin1_detected_no_crash(tmp_path: Path) -> None:
    csv_path = tmp_path / "latin1.csv"
    csv_path.write_bytes("name,role\ncaf\xe9,dev\n".encode("latin-1"))

    units = extract_csv(str(csv_path))

    assert len(units) == 1
    assert "café" in units[0].text


def test_csv_too_large_raises_value_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "big.csv"
    csv_path.write_text("name,role\nAda,Engineer\n", encoding="utf-8")

    extractor = CsvExtractor(max_bytes=1)
    with pytest.raises(ValueError, match="CSV too large"):
        extractor.extract(csv_path)


def test_extract_unsupported_extensions_raise() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract("notes.docx")
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract("data.json")
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract("README")


def test_extract_uppercase_extension_routes(tmp_path: Path) -> None:
    csv_path = tmp_path / "UPPER.CSV"
    csv_path.write_text("name,role\nAda,Engineer\n", encoding="utf-8")

    units = extract(str(csv_path))

    assert len(units) == 1
    assert units[0].source_type == "csv"


def test_file_not_found_raises() -> None:
    with pytest.raises(FileNotFoundError):
        extract_txt("missing_file.txt")

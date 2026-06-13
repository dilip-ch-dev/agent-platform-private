from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import chardet
import pandas as pd
from pypdf import PdfReader

from app.rag.chunker import chunk_text
from packages.contracts.rag import Chunk, ExtractedUnit, SupportedSourceType
from packages.contracts.schemas import Locator


def _source_type_for_path(file_path: str) -> SupportedSourceType:
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".txt":
        return "txt"
    if suffix == ".csv":
        return "csv"
    return "unknown"


def extract_pdf(file_path: str) -> list[ExtractedUnit]:
    source_file = str(file_path)
    reader = PdfReader(source_file)
    units: list[ExtractedUnit] = []
    for page_index, page in enumerate(reader.pages, start=1):
        page_text = (page.extract_text() or "").strip()
        if not page_text:
            continue
        units.append(
            ExtractedUnit(
                unit_id=str(uuid4()),
                source_file=source_file,
                source_type="pdf",
                text=page_text,
                locator=Locator(page=page_index),
            )
        )
    return units


def extract_txt(file_path: str) -> list[ExtractedUnit]:
    source_file = str(file_path)
    raw = Path(source_file).read_bytes()
    detected = chardet.detect(raw).get("encoding") or "utf-8"
    text = raw.decode(detected, errors="replace")

    units: list[ExtractedUnit] = []
    char_start = 0
    for line in text.splitlines():
        line_text = line.strip()
        line_length = len(line)
        if line_text:
            units.append(
                ExtractedUnit(
                    unit_id=str(uuid4()),
                    source_file=source_file,
                    source_type="txt",
                    text=line_text,
                    locator=Locator(
                        char_start=char_start,
                        char_end=char_start + line_length,
                    ),
                )
            )
        char_start += line_length + 1
    return units


def extract_csv(file_path: str) -> list[ExtractedUnit]:
    source_file = str(file_path)
    dataframe = pd.read_csv(source_file)

    units: list[ExtractedUnit] = []
    for row_index, row in dataframe.iterrows():
        row_text = " | ".join(f"{column}: {value}" for column, value in row.items()).strip()
        if not row_text:
            continue
        units.append(
            ExtractedUnit(
                unit_id=str(uuid4()),
                source_file=source_file,
                source_type="csv",
                text=row_text,
                locator=Locator(row=int(row_index)),
            )
        )
    return units


def extract(file_path: str) -> list[ExtractedUnit]:
    source_type = _source_type_for_path(file_path)
    if source_type == "pdf":
        return extract_pdf(file_path)
    if source_type == "txt":
        return extract_txt(file_path)
    if source_type == "csv":
        return extract_csv(file_path)
    raise ValueError(f"Unsupported file type for ingest: {file_path}")


def build_chunks(file_path: str) -> list[Chunk]:
    units = extract(file_path)
    chunks: list[Chunk] = []
    for unit in units:
        chunks.extend(
            chunk_text(
                text=unit.text,
                source_file=unit.source_file,
                source_type=unit.source_type,
                base_locator=unit.locator,
                source_unit_id=unit.unit_id,
            )
        )
    return chunks

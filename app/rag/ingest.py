from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import uuid4

import chardet
import pandas as pd
from pypdf import PdfReader

from app.rag.chunker import TextChunker, get_text_chunker
from packages.contracts.rag import Chunk, ExtractedUnit, SupportedSourceType
from packages.contracts.schemas import Locator

logger = logging.getLogger(__name__)


def _detect_encoding(raw: bytes) -> str:
    detected = chardet.detect(raw).get("encoding")
    return detected or "utf-8"


class BaseExtractor(ABC):
    source_type: SupportedSourceType

    @abstractmethod
    def extract(self, file_path: Path) -> list[ExtractedUnit]:
        raise NotImplementedError


class PdfExtractor(BaseExtractor):
    source_type: SupportedSourceType = "pdf"

    def extract(self, file_path: Path) -> list[ExtractedUnit]:
        reader = PdfReader(str(file_path))
        units: list[ExtractedUnit] = []
        for page_index, page in enumerate(reader.pages, start=1):
            page_text = (page.extract_text() or "").strip()
            if not page_text:
                continue
            units.append(
                ExtractedUnit(
                    unit_id=str(uuid4()),
                    source_file=str(file_path),
                    source_type=self.source_type,
                    text=page_text,
                    locator=Locator(page=page_index),
                )
            )
        logger.debug("Extracted %d PDF units from %s", len(units), file_path)
        return units


class TxtExtractor(BaseExtractor):
    source_type: SupportedSourceType = "txt"

    def extract(self, file_path: Path) -> list[ExtractedUnit]:
        raw = file_path.read_bytes()
        encoding = _detect_encoding(raw)
        text = raw.decode(encoding, errors="replace")

        units: list[ExtractedUnit] = []
        char_start = 0
        for line in text.splitlines(keepends=True):
            line_without_newline = line.rstrip("\r\n")
            line_length = len(line)
            line_text = line_without_newline.strip()
            if line_text:
                units.append(
                    ExtractedUnit(
                        unit_id=str(uuid4()),
                        source_file=str(file_path),
                        source_type=self.source_type,
                        text=line_text,
                        locator=Locator(
                            char_start=char_start,
                            char_end=char_start + len(line_without_newline),
                        ),
                    )
                )
            char_start += line_length

        logger.debug("Extracted %d TXT units from %s", len(units), file_path)
        return units


class CsvExtractor(BaseExtractor):
    source_type: SupportedSourceType = "csv"

    def __init__(self, max_bytes: int = 100 * 1024 * 1024) -> None:
        self._max_bytes = max_bytes

    def extract(self, file_path: Path) -> list[ExtractedUnit]:
        if file_path.stat().st_size > self._max_bytes:
            raise ValueError(f"CSV too large: {file_path}")

        raw = file_path.read_bytes()
        encoding = _detect_encoding(raw)
        dataframe = pd.read_csv(
            file_path, encoding=encoding, dtype=str, keep_default_na=False
        )

        units: list[ExtractedUnit] = []
        for row_index, row in dataframe.iterrows():
            normalized_items = [(column, str(value)) for column, value in row.items()]
            if not any(value.strip() for _, value in normalized_items):
                continue

            row_text = " | ".join(
                f"{column}: {value}" for column, value in normalized_items
            ).strip()
            if not row_text:
                continue

            units.append(
                ExtractedUnit(
                    unit_id=str(uuid4()),
                    source_file=str(file_path),
                    source_type=self.source_type,
                    text=row_text,
                    locator=Locator(row=int(row_index)),
                )
            )

        logger.debug("Extracted %d CSV units from %s", len(units), file_path)
        return units


class ExtractorRegistry:
    def __init__(self) -> None:
        self._extractors: dict[str, BaseExtractor] = {}

    def register(self, suffix: str, extractor: BaseExtractor) -> None:
        self._extractors[suffix.lower()] = extractor

    def get(self, suffix: str) -> BaseExtractor:
        normalized = suffix.lower()
        if normalized not in self._extractors:
            raise ValueError(
                f"Unsupported file type for ingest: {suffix or '<no-extension>'}"
            )
        return self._extractors[normalized]


def _build_default_registry() -> ExtractorRegistry:
    registry = ExtractorRegistry()
    registry.register(".pdf", PdfExtractor())
    registry.register(".txt", TxtExtractor())
    registry.register(".csv", CsvExtractor())
    return registry


class FileProcessor:
    def __init__(self, registry: ExtractorRegistry, chunker: TextChunker) -> None:
        self._registry = registry
        self._chunker = chunker

    def extract(self, file_path: str | Path) -> list[ExtractedUnit]:
        path = Path(file_path)
        extractor = self._registry.get(path.suffix)
        units = extractor.extract(path)
        logger.debug(
            "extract() routed %s to %s (%d units)",
            path,
            extractor.__class__.__name__,
            len(units),
        )
        return units

    def process(self, file_path: str | Path) -> list[Chunk]:
        units = self.extract(file_path)
        chunks: list[Chunk] = []
        for unit in units:
            chunks.extend(
                self._chunker.chunk(
                    text=unit.text,
                    source_file=unit.source_file,
                    source_type=unit.source_type,
                    base_locator=unit.locator,
                    source_unit_id=unit.unit_id,
                )
            )

        logger.debug("process() produced %d chunks from %s", len(chunks), file_path)
        return chunks


_DEFAULT_PROCESSOR = FileProcessor(
    registry=_build_default_registry(),
    chunker=get_text_chunker(),
)


def extract_pdf(file_path: str) -> list[ExtractedUnit]:
    return PdfExtractor().extract(Path(file_path))


def extract_txt(file_path: str) -> list[ExtractedUnit]:
    return TxtExtractor().extract(Path(file_path))


def extract_csv(file_path: str) -> list[ExtractedUnit]:
    return CsvExtractor().extract(Path(file_path))


def extract(file_path: str) -> list[ExtractedUnit]:
    return _DEFAULT_PROCESSOR.extract(file_path)


def build_chunks(file_path: str) -> list[Chunk]:
    return _DEFAULT_PROCESSOR.process(file_path)

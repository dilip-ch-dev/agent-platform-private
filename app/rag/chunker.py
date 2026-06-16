from __future__ import annotations

import logging
from functools import lru_cache
from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from packages.contracts.rag import Chunk, SupportedSourceType
from packages.contracts.schemas import Locator

logger = logging.getLogger(__name__)

_DEFAULT_CHUNK_SIZE = 512
_DEFAULT_CHUNK_OVERLAP = 64


def _count_tokens(text: str) -> int:
    try:
        import tiktoken  # type: ignore

        encoder = tiktoken.get_encoding("cl100k_base")
        return len(encoder.encode(text))
    except Exception:
        return len(text.split())


class TextChunker:
    def __init__(self, chunk_size: int = _DEFAULT_CHUNK_SIZE, chunk_overlap: int = _DEFAULT_CHUNK_OVERLAP) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk(
        self,
        text: str,
        source_file: str,
        source_type: SupportedSourceType,
        base_locator: Locator,
        source_unit_id: str | None = None,
    ) -> list[Chunk]:
        if not text.strip():
            logger.debug("chunk_text() skipped blank text. source_file=%s", source_file)
            return []

        pieces = self._splitter.split_text(text)

        chunks: list[Chunk] = []
        for piece in pieces:
            clean_piece = piece.strip()
            if not clean_piece:
                continue

            source_unit_ids = [source_unit_id] if source_unit_id else []
            chunks.append(
                Chunk(
                    chunk_id=str(uuid4()),
                    source_file=source_file,
                    source_type=source_type,
                    text=clean_piece,
                    locator=base_locator,
                    source_unit_ids=source_unit_ids,
                    token_count=_count_tokens(clean_piece),
                )
            )

        logger.debug("Produced %d chunks from source_file=%s", len(chunks), source_file)
        return chunks


@lru_cache(maxsize=1)
def get_text_chunker() -> TextChunker:
    return TextChunker()


def chunk_text(
    text: str,
    source_file: str,
    source_type: SupportedSourceType,
    base_locator: Locator,
    source_unit_id: str | None = None,
) -> list[Chunk]:
    return get_text_chunker().chunk(
        text=text,
        source_file=source_file,
        source_type=source_type,
        base_locator=base_locator,
        source_unit_id=source_unit_id,
    )

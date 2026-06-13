from __future__ import annotations

from uuid import uuid4

from langchain_text_splitters import RecursiveCharacterTextSplitter

from packages.contracts.rag import Chunk, SupportedSourceType
from packages.contracts.schemas import Locator

_CHUNK_SIZE = 512
_CHUNK_OVERLAP = 64


def chunk_text(
    text: str,
    source_file: str,
    source_type: SupportedSourceType,
    base_locator: Locator,
    source_unit_id: str | None = None,
) -> list[Chunk]:
    if not text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
    )
    pieces = splitter.split_text(text)

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
                token_count=len(clean_piece.split()),
            )
        )
    return chunks

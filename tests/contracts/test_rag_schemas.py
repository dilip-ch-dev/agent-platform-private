import pytest
from pydantic import ValidationError

from packages.contracts.rag import (
    Chunk,
    ExtractedUnit,
    IngestResult,
    RetrievalResult,
    StoredChunk,
)
from packages.contracts.schemas import Locator


def _valid_extracted_unit(**overrides) -> ExtractedUnit:
    data = {
        "unit_id": "unit-1",
        "source_file": "doc.pdf",
        "source_type": "pdf",
        "text": "sample text",
        "locator": Locator(page=1),
    }
    data.update(overrides)
    return ExtractedUnit(**data)


def _valid_chunk(**overrides) -> Chunk:
    data = {
        "chunk_id": "chunk-1",
        "source_file": "doc.txt",
        "source_type": "txt",
        "text": "chunk text",
        "locator": Locator(char_start=0, char_end=10),
    }
    data.update(overrides)
    return Chunk(**data)


def _valid_stored_chunk(**overrides) -> StoredChunk:
    data = {
        "chunk_id": "chunk-1",
        "source_file": "doc.csv",
        "source_type": "csv",
        "text": "stored text",
        "locator": Locator(row=2),
        "tenant_id": "tenant-a",
        "collection": "default",
    }
    data.update(overrides)
    return StoredChunk(**data)


class TestLocatorValidation:
    def test_accepts_pdf_page_locator(self) -> None:
        unit = _valid_extracted_unit(locator=Locator(page=1))
        assert unit.locator.page == 1

    def test_accepts_txt_char_locator(self) -> None:
        unit = _valid_extracted_unit(locator=Locator(char_start=0, char_end=10))
        assert unit.locator.char_start == 0
        assert unit.locator.char_end == 10

    def test_accepts_csv_row_locator(self) -> None:
        unit = _valid_extracted_unit(locator=Locator(row=2))
        assert unit.locator.row == 2

    def test_rejects_locator_with_no_position(self) -> None:
        with pytest.raises(ValidationError):
            _valid_extracted_unit(locator=Locator())

    def test_rejects_char_end_without_char_start(self) -> None:
        with pytest.raises(ValidationError):
            _valid_extracted_unit(locator=Locator(char_end=10))

    def test_rejects_char_end_before_char_start(self) -> None:
        with pytest.raises(ValidationError):
            _valid_extracted_unit(locator=Locator(char_start=10, char_end=5))


class TestExtractedUnit:
    def test_accepts_valid_unit(self) -> None:
        unit = _valid_extracted_unit()
        assert unit.unit_id == "unit-1"
        assert unit.source_file == "doc.pdf"

    def test_rejects_empty_unit_id(self) -> None:
        with pytest.raises(ValidationError):
            _valid_extracted_unit(unit_id="")

    def test_rejects_empty_source_file(self) -> None:
        with pytest.raises(ValidationError):
            _valid_extracted_unit(source_file="")

    def test_rejects_empty_text(self) -> None:
        with pytest.raises(ValidationError):
            _valid_extracted_unit(text="")


class TestChunk:
    def test_accepts_valid_chunk(self) -> None:
        chunk = _valid_chunk()
        assert chunk.chunk_id == "chunk-1"

    def test_preserves_source_unit_ids(self) -> None:
        chunk = _valid_chunk(source_unit_ids=["unit-1", "unit-2"])
        assert chunk.source_unit_ids == ["unit-1", "unit-2"]

    def test_accepts_non_negative_token_count(self) -> None:
        chunk = _valid_chunk(token_count=0)
        assert chunk.token_count == 0

    def test_rejects_negative_token_count(self) -> None:
        with pytest.raises(ValidationError):
            _valid_chunk(token_count=-1)


class TestStoredChunk:
    def test_accepts_valid_stored_chunk(self) -> None:
        stored = _valid_stored_chunk()
        assert stored.tenant_id == "tenant-a"

    def test_vector_id_and_embedding_model_optional(self) -> None:
        stored = _valid_stored_chunk()
        assert stored.vector_id is None
        assert stored.embedding_model is None

    def test_rejects_empty_tenant_id(self) -> None:
        with pytest.raises(ValidationError):
            _valid_stored_chunk(tenant_id="")

    def test_rejects_empty_collection(self) -> None:
        with pytest.raises(ValidationError):
            _valid_stored_chunk(collection="")


class TestRetrievalResult:
    def _result(self, **overrides) -> RetrievalResult:
        data = {
            "chunk": _valid_stored_chunk(),
            "score": 0.5,
            "rank": 1,
        }
        data.update(overrides)
        return RetrievalResult(**data)

    def test_accepts_score_zero(self) -> None:
        result = self._result(score=0.0)
        assert result.score == 0.0

    def test_accepts_score_one(self) -> None:
        result = self._result(score=1.0)
        assert result.score == 1.0

    def test_rejects_score_below_zero(self) -> None:
        with pytest.raises(ValidationError):
            self._result(score=-0.1)

    def test_rejects_score_above_one(self) -> None:
        with pytest.raises(ValidationError):
            self._result(score=1.1)

    def test_rejects_rank_less_than_one(self) -> None:
        with pytest.raises(ValidationError):
            self._result(rank=0)


class TestIngestResult:
    def _result(self, **overrides) -> IngestResult:
        data = {
            "source_file": "doc.pdf",
            "tenant_id": "tenant-a",
            "collection": "default",
            "extracted_count": 1,
            "chunk_count": 1,
            "stored_count": 1,
        }
        data.update(overrides)
        return IngestResult(**data)

    def test_accepts_valid_counts(self) -> None:
        result = self._result()
        assert result.extracted_count == 1

    def test_accepts_zero_counts(self) -> None:
        result = self._result(extracted_count=0, chunk_count=0, stored_count=0)
        assert result.stored_count == 0

    def test_rejects_negative_counts(self) -> None:
        with pytest.raises(ValidationError):
            self._result(extracted_count=-1)

    def test_defaults_skipped_count_to_zero(self) -> None:
        result = self._result()
        assert result.skipped_count == 0

    def test_defaults_replaced_existing_to_false(self) -> None:
        result = self._result()
        assert result.replaced_existing is False

    def test_defaults_errors_to_empty_list(self) -> None:
        result = self._result()
        assert result.errors == []

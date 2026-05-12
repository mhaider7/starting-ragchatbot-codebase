import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from vector_store import VectorStore, SearchResults
from models import CourseChunk


def make_store_with_mock_collections():
    """Create a VectorStore with mocked ChromaDB collections (no real DB)."""
    store = VectorStore.__new__(VectorStore)
    store.max_results = 5
    store.course_catalog = MagicMock()
    store.course_content = MagicMock()
    store.embedding_function = MagicMock()
    return store


# --- _build_filter tests ---

def test_build_filter_no_args_returns_none():
    store = make_store_with_mock_collections()
    assert store._build_filter(None, None) is None


def test_build_filter_course_only():
    store = make_store_with_mock_collections()
    result = store._build_filter("Python Basics", None)
    assert result == {"course_title": "Python Basics"}


def test_build_filter_lesson_only():
    store = make_store_with_mock_collections()
    result = store._build_filter(None, 1)
    assert result == {"lesson_number": 1}


def test_build_filter_both_uses_and():
    store = make_store_with_mock_collections()
    result = store._build_filter("Python Basics", 2)
    assert "$and" in result
    conditions = result["$and"]
    assert {"course_title": "Python Basics"} in conditions
    assert {"lesson_number": 2} in conditions


# --- search() tests ---

def test_search_returns_results_when_data_exists():
    store = make_store_with_mock_collections()
    store.course_content.count.return_value = 10
    store.course_content.query.return_value = {
        "documents": [["Python is great."]],
        "metadatas": [[{"course_title": "Python Basics", "lesson_number": 1, "chunk_index": 0}]],
        "distances": [[0.1]],
    }

    results = store.search("python language")

    assert not results.is_empty()
    assert results.documents[0] == "Python is great."


def test_search_empty_collection_returns_empty_result():
    store = make_store_with_mock_collections()
    store.course_content.count.return_value = 0

    results = store.search("anything")

    assert results.is_empty()
    assert results.error is not None


def test_search_handles_fewer_docs_than_n_results():
    """When collection has fewer docs than n_results, ChromaDB raises InvalidArgumentError.
    The current try/except catches it and returns SearchResults.empty."""
    store = make_store_with_mock_collections()
    store.course_content.count.return_value = 2
    store.course_content.query.side_effect = Exception(
        "n_results=5 but collection only has 2 elements"
    )

    results = store.search("test query")

    assert results.error is not None
    assert not results.is_empty() is False  # is_empty() returns True


def test_search_propagates_course_filter_to_query():
    store = make_store_with_mock_collections()
    store.course_content.count.return_value = 10
    store.course_catalog.query.return_value = {
        "documents": [["Python Basics"]],
        "metadatas": [[{"title": "Python Basics"}]],
    }
    store.course_content.query.return_value = {
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]],
    }

    store.search("variables", course_name="Python")

    call_kwargs = store.course_content.query.call_args[1]
    assert call_kwargs["where"] == {"course_title": "Python Basics"}


# --- add_course_content() with None lesson_number ---

def test_add_course_content_none_lesson_number_omits_field():
    """
    ChromaDB rejects None values in metadata.
    Chunks with lesson_number=None must omit the field rather than passing None.
    """
    store = make_store_with_mock_collections()

    chunks = [
        CourseChunk(content="Preamble", course_title="Python Basics", lesson_number=None, chunk_index=0)
    ]

    store.add_course_content(chunks)

    call_args = store.course_content.add.call_args
    metadata = call_args[1]["metadatas"][0]
    assert "lesson_number" not in metadata, (
        "lesson_number must be omitted from metadata when None — ChromaDB rejects null values"
    )
    assert metadata["course_title"] == "Python Basics"
    assert metadata["chunk_index"] == 0

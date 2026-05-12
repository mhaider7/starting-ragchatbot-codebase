import pytest
from unittest.mock import MagicMock
from search_tools import CourseSearchTool
from vector_store import SearchResults


def test_execute_returns_formatted_string(mock_vector_store, sample_search_results):
    mock_vector_store.search.return_value = sample_search_results
    tool = CourseSearchTool(mock_vector_store)

    result = tool.execute(query="python basics")

    assert "[Python Basics - Lesson 1]" in result
    assert "Python is a programming language." in result
    assert "[Python Basics - Lesson 2]" in result


def test_execute_returns_no_content_message_when_empty(mock_vector_store, empty_search_results):
    mock_vector_store.search.return_value = empty_search_results
    tool = CourseSearchTool(mock_vector_store)

    result = tool.execute(query="nonexistent topic")

    assert "No relevant content found" in result


def test_execute_returns_error_string_on_error(mock_vector_store, error_search_results):
    mock_vector_store.search.return_value = error_search_results
    tool = CourseSearchTool(mock_vector_store)

    result = tool.execute(query="test query")

    assert "Search error" in result


def test_execute_with_course_name_includes_filter_in_empty_msg(mock_vector_store, empty_search_results):
    mock_vector_store.search.return_value = empty_search_results
    tool = CourseSearchTool(mock_vector_store)

    result = tool.execute(query="variables", course_name="Python Basics")

    assert "Python Basics" in result
    assert "No relevant content found" in result


def test_execute_tracks_sources_in_last_sources(mock_vector_store, sample_search_results):
    mock_vector_store.search.return_value = sample_search_results
    mock_vector_store.get_lesson_link.return_value = "https://example.com/lesson/1"
    tool = CourseSearchTool(mock_vector_store)

    tool.execute(query="python basics")

    assert len(tool.last_sources) == 2
    assert tool.last_sources[0]["label"] == "Python Basics - Lesson 1"


def test_execute_sources_have_label_and_url_keys(mock_vector_store, sample_search_results):
    mock_vector_store.search.return_value = sample_search_results
    tool = CourseSearchTool(mock_vector_store)

    tool.execute(query="python basics")

    for source in tool.last_sources:
        assert "label" in source
        assert "url" in source

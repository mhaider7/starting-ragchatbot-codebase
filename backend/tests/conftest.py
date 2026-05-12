import sys
import os
import pytest
from unittest.mock import MagicMock

# Add backend directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vector_store import SearchResults
from models import CourseChunk, Course, Lesson
from tests.helpers import make_tool_call_mock, make_groq_response  # noqa: F401 — re-exported for tests


@pytest.fixture
def sample_search_results():
    return SearchResults(
        documents=["Python is a programming language.", "Lists store ordered data."],
        metadata=[
            {"course_title": "Python Basics", "lesson_number": 1, "chunk_index": 0},
            {"course_title": "Python Basics", "lesson_number": 2, "chunk_index": 0},
        ],
        distances=[0.1, 0.2],
    )


@pytest.fixture
def empty_search_results():
    return SearchResults(documents=[], metadata=[], distances=[])


@pytest.fixture
def error_search_results():
    return SearchResults.empty("Search error: n_results=5 but collection has 0 elements")


@pytest.fixture
def mock_vector_store(sample_search_results):
    store = MagicMock()
    store.search.return_value = sample_search_results
    store.get_lesson_link.return_value = "https://example.com/lesson/1"
    return store


@pytest.fixture
def sample_chunks():
    return [
        CourseChunk(content="Intro content", course_title="Python Basics", lesson_number=1, chunk_index=0),
        CourseChunk(content="Variables content", course_title="Python Basics", lesson_number=2, chunk_index=1),
        CourseChunk(content="Preamble text", course_title="Python Basics", lesson_number=None, chunk_index=2),
    ]


@pytest.fixture
def sample_course():
    return Course(
        title="Python Basics",
        course_link="https://example.com/python",
        instructor="Jane Doe",
        lessons=[
            Lesson(lesson_number=1, title="Introduction", lesson_link="https://example.com/lesson/1"),
            Lesson(lesson_number=2, title="Variables", lesson_link=None),
        ],
    )


@pytest.fixture
def mock_groq_client():
    return MagicMock()


def make_tool_call_mock(tool_name="search_course_content", arguments='{"query": "python variables"}', call_id="call_abc123"):
    tc = MagicMock()
    tc.id = call_id
    tc.function.name = tool_name
    tc.function.arguments = arguments
    return tc


def make_groq_response(content=None, finish_reason="stop", tool_calls=None):
    response = MagicMock()
    response.choices[0].finish_reason = finish_reason
    response.choices[0].message.content = content
    response.choices[0].message.tool_calls = tool_calls or []
    return response

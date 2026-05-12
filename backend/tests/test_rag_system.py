import pytest
from unittest.mock import MagicMock, patch


def make_rag_system_with_mocks():
    """Construct RAGSystem with all external components mocked."""
    from rag_system import RAGSystem

    with patch("rag_system.DocumentProcessor"), \
         patch("rag_system.VectorStore"), \
         patch("rag_system.AIGenerator") as MockGen, \
         patch("rag_system.SessionManager") as MockSession, \
         patch("rag_system.ToolManager") as MockManager, \
         patch("rag_system.CourseSearchTool"), \
         patch("rag_system.CourseOutlineTool"):

        from config import Config
        cfg = Config(GROQ_API_KEY="fake-key")
        system = RAGSystem(cfg)

    # Replace with fresh mocks for test control
    system.ai_generator = MagicMock()
    system.session_manager = MagicMock()
    system.tool_manager = MagicMock()
    system.tool_manager.get_tool_definitions.return_value = [{"type": "function"}]
    system.tool_manager.get_last_sources.return_value = [{"label": "Python Basics - Lesson 1", "url": None}]
    system.ai_generator.generate_response.return_value = "Python uses indentation for code blocks."
    system.session_manager.get_conversation_history.return_value = "User: hi\nAssistant: hello"

    return system


def test_query_returns_tuple_of_answer_and_sources():
    system = make_rag_system_with_mocks()

    answer, sources = system.query("What is Python?", session_id="sess_1")

    assert isinstance(answer, str)
    assert len(answer) > 0
    assert isinstance(sources, list)


def test_query_passes_tools_to_generate_response():
    system = make_rag_system_with_mocks()

    system.query("What is Python?")

    call_kwargs = system.ai_generator.generate_response.call_args[1]
    assert "tools" in call_kwargs
    assert call_kwargs["tools"] == [{"type": "function"}]


def test_query_passes_tool_manager_to_generate_response():
    system = make_rag_system_with_mocks()

    system.query("What is Python?")

    call_kwargs = system.ai_generator.generate_response.call_args[1]
    assert call_kwargs["tool_manager"] is system.tool_manager


def test_query_collects_sources_from_tool_manager():
    system = make_rag_system_with_mocks()

    _, sources = system.query("What is Python?", session_id="sess_1")

    system.tool_manager.get_last_sources.assert_called_once()
    assert sources == [{"label": "Python Basics - Lesson 1", "url": None}]


def test_query_resets_sources_after_retrieval():
    system = make_rag_system_with_mocks()

    system.query("What is Python?", session_id="sess_1")

    system.tool_manager.reset_sources.assert_called_once()


def test_query_updates_session_history():
    system = make_rag_system_with_mocks()

    system.query("What is Python?", session_id="sess_abc")

    system.session_manager.add_exchange.assert_called_once_with(
        "sess_abc", "What is Python?", "Python uses indentation for code blocks."
    )

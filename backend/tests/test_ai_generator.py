import pytest
from unittest.mock import MagicMock, call, patch
from ai_generator import AIGenerator
from tests.helpers import make_tool_call_mock, make_groq_response


def make_generator(mock_groq_client):
    gen = AIGenerator.__new__(AIGenerator)
    gen.client = mock_groq_client
    gen.model = "test-model"
    gen.base_params = {"model": "test-model", "temperature": 0, "max_tokens": 800}
    return gen


BASE_MESSAGES = [
    {"role": "system", "content": "You are helpful"},
    {"role": "user", "content": "test query"},
]

TOOL_DEFS = [{"type": "function", "function": {"name": "search_course_content"}}]


def test_generate_response_no_tools_returns_content(mock_groq_client):
    gen = make_generator(mock_groq_client)
    mock_groq_client.chat.completions.create.return_value = make_groq_response(
        content="Direct answer", finish_reason="stop"
    )

    result = gen.generate_response(query="What is Python?")

    assert result == "Direct answer"
    mock_groq_client.chat.completions.create.assert_called_once()


def test_generate_response_triggers_tool_execution(mock_groq_client):
    gen = make_generator(mock_groq_client)
    tool_call = make_tool_call_mock()

    first_response = make_groq_response(finish_reason="tool_calls", tool_calls=[tool_call])
    second_response = make_groq_response(content="Final answer after tool", finish_reason="stop")
    mock_groq_client.chat.completions.create.side_effect = [first_response, second_response]

    mock_tool_manager = MagicMock()
    mock_tool_manager.execute_tool.return_value = "Tool result: Python info"

    result = gen.generate_response(
        query="What is Python?",
        tools=TOOL_DEFS,
        tool_manager=mock_tool_manager,
    )

    assert result == "Final answer after tool"
    assert mock_groq_client.chat.completions.create.call_count == 2
    mock_tool_manager.execute_tool.assert_called_once_with("search_course_content", query="python variables")


def test_handle_tool_execution_calls_tool_manager(mock_groq_client):
    gen = make_generator(mock_groq_client)
    tool_call = make_tool_call_mock(arguments='{"query": "lists", "course_name": "Python"}')

    initial_response = make_groq_response(finish_reason="tool_calls", tool_calls=[tool_call])
    final_response = make_groq_response(content="Here is the answer")
    mock_groq_client.chat.completions.create.return_value = final_response

    mock_tool_manager = MagicMock()
    mock_tool_manager.execute_tool.return_value = "[Python Basics - Lesson 2]\nLists store ordered data."

    api_params = {**gen.base_params, "messages": BASE_MESSAGES, "tools": TOOL_DEFS, "tool_choice": "auto"}
    gen._handle_tool_execution(initial_response, api_params, mock_tool_manager)

    mock_tool_manager.execute_tool.assert_called_once_with(
        "search_course_content", query="lists", course_name="Python"
    )


def test_handle_tool_execution_assistant_message_content_not_none(mock_groq_client):
    """
    When Groq returns a tool call, assistant_message.content is None.
    The message sent to the second API call must NOT have content=None,
    or Groq raises BadRequestError — the root cause of 'query failed'.
    """
    gen = make_generator(mock_groq_client)
    tool_call = make_tool_call_mock()

    # Simulate Groq: content is None on a tool call response
    initial_response = make_groq_response(finish_reason="tool_calls", content=None, tool_calls=[tool_call])
    final_response = make_groq_response(content="Final answer")
    mock_groq_client.chat.completions.create.return_value = final_response

    mock_tool_manager = MagicMock()
    mock_tool_manager.execute_tool.return_value = "Tool result"

    api_params = {**gen.base_params, "messages": BASE_MESSAGES, "tools": TOOL_DEFS, "tool_choice": "auto"}
    gen._handle_tool_execution(initial_response, api_params, mock_tool_manager)

    # Inspect the messages passed to the second API call
    second_call_kwargs = mock_groq_client.chat.completions.create.call_args[1]
    messages = second_call_kwargs["messages"]
    assistant_msgs = [m for m in messages if m["role"] == "assistant"]
    assert len(assistant_msgs) == 1
    # This assertion FAILS with the current code (content is None)
    assert assistant_msgs[0]["content"] is not None, (
        "assistant message content must not be None — Groq rejects null content "
        "and raises BadRequestError, causing the 'query failed' HTTP 500"
    )


def test_handle_tool_execution_returns_final_response(mock_groq_client):
    gen = make_generator(mock_groq_client)
    tool_call = make_tool_call_mock()

    initial_response = make_groq_response(finish_reason="tool_calls", tool_calls=[tool_call])
    final_response = make_groq_response(content="The final synthesized answer")
    mock_groq_client.chat.completions.create.return_value = final_response

    mock_tool_manager = MagicMock()
    mock_tool_manager.execute_tool.return_value = "tool output"

    api_params = {**gen.base_params, "messages": BASE_MESSAGES, "tools": TOOL_DEFS, "tool_choice": "auto"}
    result = gen._handle_tool_execution(initial_response, api_params, mock_tool_manager)

    assert result == "The final synthesized answer"


def test_handle_tool_execution_tool_result_appended_as_tool_role(mock_groq_client):
    gen = make_generator(mock_groq_client)
    tool_call = make_tool_call_mock(call_id="call_xyz")

    initial_response = make_groq_response(finish_reason="tool_calls", tool_calls=[tool_call])
    final_response = make_groq_response(content="Answer")
    mock_groq_client.chat.completions.create.return_value = final_response

    mock_tool_manager = MagicMock()
    mock_tool_manager.execute_tool.return_value = "Search result content"

    api_params = {**gen.base_params, "messages": BASE_MESSAGES, "tools": TOOL_DEFS, "tool_choice": "auto"}
    gen._handle_tool_execution(initial_response, api_params, mock_tool_manager)

    second_call_kwargs = mock_groq_client.chat.completions.create.call_args[1]
    messages = second_call_kwargs["messages"]
    tool_msgs = [m for m in messages if m["role"] == "tool"]
    assert len(tool_msgs) == 1
    assert tool_msgs[0]["tool_call_id"] == "call_xyz"
    assert tool_msgs[0]["content"] == "Search result content"

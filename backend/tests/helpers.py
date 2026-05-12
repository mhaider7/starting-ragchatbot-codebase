from unittest.mock import MagicMock


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

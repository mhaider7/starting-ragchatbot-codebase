import json
from groq import Groq
from typing import List, Optional, Dict, Any

class AIGenerator:
    """Handles interactions with Groq API for generating responses"""

    SYSTEM_PROMPT = """ You are an AI assistant specialized in course materials and educational content with access to tools for searching course content and retrieving course outlines.

Tool Usage:
- **search_course_content**: Use for questions about specific course topics, concepts, or lesson details
- **get_course_outline**: Use for questions about a course's structure, lesson list, or overview (e.g. "what lessons are in X?", "give me the outline of X", "what does course X cover?")
- **One tool call per query maximum**
- If a tool yields no results, state this clearly without offering alternatives

Response Protocol:
- **General knowledge questions**: Answer using existing knowledge without searching
- **Course content questions**: Use search_course_content, then synthesize results into a direct answer
- **Course outline / structure questions**: Use get_course_outline, then present the course title, course link, and each lesson (number and title). Include lesson links when available.
- **No meta-commentary**: Provide direct answers only — no reasoning process, tool explanations, or question-type analysis. Do not mention "based on the search results".

All responses must be:
1. **Brief, Concise and focused** - Get to the point quickly
2. **Educational** - Maintain instructional value
3. **Clear** - Use accessible language
4. **Example-supported** - Include relevant examples when they aid understanding
Provide only the direct answer to what was asked.
"""

    def __init__(self, api_key: str, model: str):
        self.client = Groq(api_key=api_key)
        self.model = model

        self.base_params = {
            "model": self.model,
            "temperature": 0,
            "max_tokens": 800
        }

    def generate_response(self, query: str,
                         conversation_history: Optional[str] = None,
                         tools: Optional[List] = None,
                         tool_manager=None) -> str:
        system_content = (
            f"{self.SYSTEM_PROMPT}\n\nPrevious conversation:\n{conversation_history}"
            if conversation_history
            else self.SYSTEM_PROMPT
        )

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": query}
        ]

        api_params = {
            **self.base_params,
            "messages": messages,
        }

        if tools:
            api_params["tools"] = tools
            api_params["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**api_params)

        if response.choices[0].finish_reason == "tool_calls" and tool_manager:
            return self._handle_tool_execution(response, api_params, tool_manager)

        return response.choices[0].message.content

    def _handle_tool_execution(self, initial_response, base_params: Dict[str, Any], tool_manager) -> str:
        messages = base_params["messages"].copy()

        assistant_message = initial_response.choices[0].message
        messages.append({
            "role": "assistant",
            "content": assistant_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })

        for tool_call in assistant_message.tool_calls:
            tool_args = json.loads(tool_call.function.arguments)
            tool_result = tool_manager.execute_tool(tool_call.function.name, **tool_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

        final_response = self.client.chat.completions.create(
            **self.base_params,
            messages=messages
        )
        return final_response.choices[0].message.content

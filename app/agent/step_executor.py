import json

from app.agent.prompts import STEP_EXECUTOR_PROMPT
from app.agent.schema import tools
from app.agent.tools import fetch_url_sync, search_web_sync
from app.agent.agent import safe_chat_completion

TOOLS_MAP = {
    "search_web_sync": search_web_sync,
    "fetch_url_sync": fetch_url_sync,
}


class StepExecutor:
    async def execute(self, step_text: str) -> dict:
        messages = [
            {"role": "system", "content": STEP_EXECUTOR_PROMPT},
            {"role": "user", "content": step_text},
        ]

        used_sources: list[str] = []

        while True:
            response = await safe_chat_completion(
                model="gpt-4.1-mini",
                messages=messages,
                tools=tools,
            )

            msg = response.choices[0].message

            # финальный текст шага
            if not msg.tool_calls:
                return {
                    "text": msg.content,
                    "sources": used_sources,
                }

            call = msg.tool_calls[0]
            tool_name = call.function.name
            tool_args = json.loads(call.function.arguments)

            messages.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": call.type,
                            "function": {
                                "name": tool_name,
                                "arguments": call.function.arguments,
                            },
                        }
                    ],
                }
            )

            if tool_name == "search_web":
                result = search_web_sync(**tool_args)
                # добавляем только URL
                for item in result.get("results", []):
                    used_sources.append(item["url"])

            elif tool_name == "fetch_url":
                result = fetch_url_sync(**tool_args)
                used_sources.append(result["url"])
            else:
                result = None

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result),
                }
            )

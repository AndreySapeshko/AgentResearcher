import json

from openai import OpenAI

from app.agent.prompts import STEP_EXECUTOR_PROMPT
from app.agent.schema import tools
from app.agent.tools import fetch_url_sync, search_web_sync
from app.config import OPEN_AI_KEY

client = OpenAI(api_key=OPEN_AI_KEY)

TOOLS_MAP = {
    "search_web_sync": search_web_sync,
    "fetch_url_sync": fetch_url_sync,
}


class StepExecutor:
    def execute(self, step_text: str) -> str:
        messages = [
            {"role": "system", "content": STEP_EXECUTOR_PROMPT},
            {"role": "user", "content": step_text},
        ]

        while True:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=messages,
                tools=tools,
            )

            msg = response.choices[0].message

            # ✅ Если LLM вернул финальный текст — шаг выполнен
            if not msg.tool_calls:
                return msg.content

            # 🔧 Если нужен инструмент
            call = msg.tool_calls[0]
            tool_name = call.function.name
            tool_args = json.loads(call.function.arguments)

            # assistant tool_call
            messages.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": call.type,
                            "function": {"name": tool_name, "arguments": call.function.arguments},
                        }
                    ],
                }
            )

            # Python-инструмент
            result = TOOLS_MAP[tool_name](**tool_args)

            # tool response
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})

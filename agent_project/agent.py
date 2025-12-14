import json
import environ

from pathlib import Path
from openai import OpenAI
from tools import search_web, fetch_url, read_file, write_file
from schema import tools

env_file = Path(__file__).resolve().parent.parent / ".env"
env = environ.Env()
env.read_env(env_file)

api_key = env("OPEN_AI_KEY", default="my_open_ai_key")

client = OpenAI(api_key=api_key)

TOOLS_MAP = {
    "search_web": search_web,
    "fetch_url": fetch_url,
    "read_file": read_file,
    "write_file": write_file,
}


class ToolAgent:
    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": (
                    "Ты инструментальный AI-агент. "
                    "Ты анализируешь запрос пользователя, "
                    "вызываешь нужные инструменты, "
                    "а затем формируешь финальный ответ."
                )
            }
        ]

    def add_user_message(self, text: str):
        self.messages.append({"role": "user", "content": text})

    def run(self):
        while True:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=self.messages,
                tools=tools,
            )

            message = response.choices[0].message

            # 🟢 1. Если GPT не вызывает инструменты — финальный ответ
            if not message.tool_calls:
                self.messages.append({
                    "role": "assistant",
                    "content": message.content
                })
                return message.content

            # 🔵 2. GPT вызывает инструменты
            for call in message.tool_calls:
                tool_name = call.function.name
                tool_args = json.loads(call.function.arguments)

                # Добавляем assistant tool_call
                self.messages.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": call.id,
                            "type": call.type,
                            "function": {
                                "name": tool_name,
                                "arguments": call.function.arguments
                            }
                        }
                    ]
                })

                # Выполняем Python-инструмент
                result = TOOLS_MAP[tool_name](**tool_args)

                # Возвращаем результат в GPT
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result)
                })

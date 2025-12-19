import json

from app.agent.client import llm_client
from app.agent.prompts import SYSTEM_PROMPT

# async def safe_chat_completion(**kwargs):
#     for attempt in range(3):
#         try:
#             return await asyncio.to_thread(
#                 client.chat.completions.create,
#                 **kwargs
#             )
#         except openai.RateLimitError as e:
#             wait_time = 20
#             await asyncio.sleep(wait_time)
#
#     raise RuntimeError("Rate limit retry failed")


class ResearchPlanner:
    async def plan(self, user_input: str, memory_context: str = "") -> dict:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        if memory_context:
            messages.append({"role": "system", "content": memory_context})

        messages.append({"role": "user", "content": user_input})
        print("REQUEST LLM from planer")
        response = await llm_client.chat(
            model="gpt-4.1-mini",
            messages=messages,
        )

        content = response.choices[0].message.content
        return json.loads(content)

from app.agent.prompts import FINAL_REPORT_PROMPT
from app.agent.agent import safe_chat_completion


class FinalReportAgent:
    async def generate(self, steps_results: list[str]) -> str:
        content = "\n\n".join(f"Шаг {i + 1}:\n{result}" for i, result in enumerate(steps_results))

        response = await safe_chat_completion(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": FINAL_REPORT_PROMPT},
                {"role": "user", "content": content},
            ],
        )

        return response.choices[0].message.content

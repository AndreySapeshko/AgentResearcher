from openai import OpenAI

from app.agent.prompts import FINAL_REPORT_PROMPT
from app.config import OPEN_AI_KEY

client = OpenAI(api_key=OPEN_AI_KEY)


class FinalReportAgent:
    def generate(self, steps_results: list[str]) -> str:
        content = "\n\n".join(f"Шаг {i + 1}:\n{result}" for i, result in enumerate(steps_results))

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": FINAL_REPORT_PROMPT},
                {"role": "user", "content": content},
            ],
        )

        return response.choices[0].message.content

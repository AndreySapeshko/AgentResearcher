import json
from openai import OpenAI
from app.agent.prompts import SYSTEM_PROMPT
from app.config import OPEN_AI_KEY

client = OpenAI(api_key=OPEN_AI_KEY)

class ResearchPlanner:
    def plan(self, user_input: str) -> dict:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )

        content = response.choices[0].message.content
        return json.loads(content)

import asyncio

from app.agent.step_executor import StepExecutor
from app.db.crud import get_next_pending_step, mark_step_error, mark_step_in_progress, update_step_result


class TaskRunner:
    def __init__(self):
        self.executor = StepExecutor()

    async def run_task(self, session, task_id: int):
        while True:
            step = await get_next_pending_step(session, task_id)
            if not step:
                break

            await mark_step_in_progress(session, step.id)

            try:
                result = await asyncio.to_thread(self.executor.execute, step.description)
                await update_step_result(session, step.id, result)

            except Exception as e:
                await mark_step_error(session, step.id, str(e))
                break

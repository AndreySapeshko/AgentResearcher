import asyncio

from app.agent.final_report import FinalReportAgent
from app.agent.step_executor import StepExecutor
from app.db.crud import (
    get_completed_steps,
    get_next_pending_step,
    mark_step_error,
    mark_step_in_progress,
    save_memory,
    update_step_result,
)


class TaskRunner:
    def __init__(self):
        self.executor = StepExecutor()
        self.reporter = FinalReportAgent()

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

        # 2. собираем результаты
        steps = await get_completed_steps(session, task_id)
        steps_results = [step.result for step in steps]

        # 3. генерируем итог
        final_report = await asyncio.to_thread(self.reporter.generate, steps_results)

        # 4. сохраняем в память
        await save_memory(session, task_id, final_report)

        return final_report

from __future__ import annotations

from orcraft import (
	OrcraftStatus,
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftResultField,
	OrcraftConfigField,
	OrcraftLogger as Logger,
)


class StepReadMazeThreadConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Read Maze Thread")
	task = None
	join_timeout_sec = OrcraftConfigField.Numeric(default=5.0, label="Join Timeout Sec")


class StepReadMazeThreadResult(OrcraftTestStepResult):
	mazes_generated = OrcraftResultField.Numeric(default=0, label="Mazes Generated")
	avg_path_steps = OrcraftResultField.Numeric(default=0, label="Avg Path Steps")
	stopped = OrcraftResultField.Boolean(default=False, label="Stopped")


class StepReadMazeThread(OrcraftTestStep):
	def __init__(self, config: StepReadMazeThreadConfig | None = None) -> None:
		super().__init__(config or StepReadMazeThreadConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepReadMazeThreadResult()

		task = self.config.task
		if task is None:
			self.result.status = OrcraftStatus.ERROR
			self.result.error_description = "Task object is missing"
			return self.result

		task["stop_event"].set()

		task["thread"].join(timeout=float(self.config.join_timeout_sec))
		if task["thread"].is_alive():
			self.result.status = OrcraftStatus.ERROR
			self.result.error_description = "Background maze thread did not stop in time"
			return self.result

		with task["lock"]:
			count = int(task["count"])
			results = list(task["results"])

		step_counts = [result.steps for result in results]
		avg_steps = round(sum(step_counts) / len(step_counts), 1) if step_counts else 0

		self.result.mazes_generated = count
		self.result.avg_path_steps = avg_steps
		self.result.stopped = True

		Logger.log(
			f"Background maze thread stopped. Mazes generated: {count}\n",
			module_tag=False,
		)

		for i, result in enumerate(results, 1):
			Logger.log(f"--- Maze {i} of {count} ---\n\n{result.colored()}\n\n", module_tag=False)

		self.result.status = OrcraftStatus.PASS
		return self.result

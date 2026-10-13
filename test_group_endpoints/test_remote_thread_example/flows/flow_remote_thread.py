from __future__ import annotations

from orcraft import (
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftResultField,
	OrcraftConfigField,
)

from test_group_endpoints.test_remote_thread_example.steps.step_start_maze_thread import StepStartMazeThread
from test_group_endpoints.test_remote_thread_example.steps.step_read_maze_thread import StepReadMazeThread
from test_group_endpoints.test_remote_thread_example.steps.step_wait import StepWait


class FlowRemoteThreadConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Remote Thread")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	test_endpoint = OrcraftConfigField.Endpoint(default="localhost")
	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")
	wait_sec = OrcraftConfigField.Numeric(default=2.0, label="Wait Sec")


class FlowRemoteThreadResult(OrcraftTestFlowResult):
	mazes_generated = OrcraftResultField.Numeric(default=0, label="Mazes Generated")
	avg_path_steps = OrcraftResultField.Numeric(default=0, label="Avg Path Steps")


class FlowRemoteThread(OrcraftTestFlow):
	result_type = FlowRemoteThreadResult

	def __init__(self, config: FlowRemoteThreadConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		# Step 1: Start background maze-solving thread on test endpoint
		step_1_result = self.run_step(
			StepStartMazeThread,
			endpoint=self.config.test_endpoint,
			maze_executable_folder=self.config.maze_executable_folder,
			width=self.config.width,
			height=self.config.height,
		)

		if self.handle_errors(step_1_result, self.result):
			return

		# Step 2: Wait - thread keeps running, task object is held in step_1_result
		step_2_result = self.run_step(
			StepWait,
			endpoint=self.config.test_endpoint,
			wait_sec=self.config.wait_sec,
		)

		if self.handle_errors(step_2_result, self.result):
			self.run_step(
				StepReadMazeThread,
				endpoint=self.config.test_endpoint,
				task=step_1_result.task,
			)
			return

		# Step 3: Stop thread and collect results - using task from Step 1
		step_3_result = self.run_step(
			StepReadMazeThread,
			endpoint=self.config.test_endpoint,
			task=step_1_result.task,
		)

		if self.handle_errors(step_3_result, self.result):
			return

		self.result.mazes_generated = step_3_result.mazes_generated
		self.result.avg_path_steps = step_3_result.avg_path_steps

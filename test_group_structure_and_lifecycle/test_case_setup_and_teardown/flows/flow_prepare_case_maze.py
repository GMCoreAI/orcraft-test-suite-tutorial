from __future__ import annotations

from test_group_structure_and_lifecycle.test_case_setup_and_teardown.steps.step_prepare_case_maze import (
	StepPrepareCaseMaze,
)

from orcraft import (
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class FlowPrepareCaseMazeConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Prepare Case Maze")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	maze_index = OrcraftConfigField.Numeric(default=1, label="Maze Index")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class FlowPrepareCaseMazeResult(OrcraftTestFlowResult):
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	maze_file_size = OrcraftResultField.Numeric(default=0, label="Maze File Size")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class FlowPrepareCaseMaze(OrcraftTestFlow):
	result_type = FlowPrepareCaseMazeResult

	def __init__(self, config: FlowPrepareCaseMazeConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		step_result = self.run_step(
			StepPrepareCaseMaze,
			workspace_folder=self.config.workspace_folder,
			maze_index=self.config.maze_index,
		)

		if self.handle_errors(step_result, self.result):
			return

		self.result.maze_file_path = step_result.maze_file_path
		self.result.maze_file_size = step_result.maze_file_size

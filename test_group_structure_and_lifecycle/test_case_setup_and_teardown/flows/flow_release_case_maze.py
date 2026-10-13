from __future__ import annotations

from test_group_structure_and_lifecycle.test_case_setup_and_teardown.steps.step_release_case_maze import (
	StepReleaseCaseMaze,
)

from orcraft import (
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class FlowReleaseCaseMazeConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Release Case Maze")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	maze_index = OrcraftConfigField.Numeric(default=1, label="Maze Index")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class FlowReleaseCaseMazeResult(OrcraftTestFlowResult):
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	file_removed = OrcraftResultField.Boolean(default=False, label="File Removed")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class FlowReleaseCaseMaze(OrcraftTestFlow):
	result_type = FlowReleaseCaseMazeResult

	def __init__(self, config: FlowReleaseCaseMazeConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		step_result = self.run_step(
			StepReleaseCaseMaze,
			workspace_folder=self.config.workspace_folder,
			maze_index=self.config.maze_index,
		)

		if self.handle_errors(step_result, self.result):
			return

		self.result.maze_file_path = step_result.maze_file_path
		self.result.file_removed = step_result.file_removed

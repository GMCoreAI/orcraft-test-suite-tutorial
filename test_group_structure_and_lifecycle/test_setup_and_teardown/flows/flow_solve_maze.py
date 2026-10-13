from __future__ import annotations

from test_group_structure_and_lifecycle.test_setup_and_teardown.steps.step_solve_maze import StepSolveMaze

from orcraft import (
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class FlowSolveMazeConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Solve Maze")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	maze_index = OrcraftConfigField.Numeric(default=1, label="Maze Index")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class FlowSolveMazeResult(OrcraftTestFlowResult):
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	path_found = OrcraftResultField.Boolean(default=False, label="Path Found")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class FlowSolveMaze(OrcraftTestFlow):
	result_type = FlowSolveMazeResult

	def __init__(self, config: FlowSolveMazeConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		step_result = self.run_step(
			StepSolveMaze,
			maze_executable_folder=self.config.maze_executable_folder,
			workspace_folder=self.config.workspace_folder,
			maze_index=self.config.maze_index,
		)

		if self.handle_errors(step_result, self.result):
			return

		self.result.maze_file_path = step_result.maze_file_path
		self.result.path_found = step_result.path_found
		self.result.path_length = step_result.path_length

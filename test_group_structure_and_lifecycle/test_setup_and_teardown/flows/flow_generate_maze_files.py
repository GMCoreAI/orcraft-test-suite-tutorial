from __future__ import annotations

from test_group_structure_and_lifecycle.test_setup_and_teardown.steps.step_generate_maze_files import StepGenerateMazeFiles

from orcraft import (
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class FlowGenerateMazeFilesConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Generate Maze Files")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	count = OrcraftConfigField.Numeric(default=10, label="Maze Count")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class FlowGenerateMazeFilesResult(OrcraftTestFlowResult):
	workspace_folder = OrcraftResultField.Text(default="", label="Workspace Folder")
	files_generated = OrcraftResultField.Numeric(default=0, label="Files Generated")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class FlowGenerateMazeFiles(OrcraftTestFlow):
	result_type = FlowGenerateMazeFilesResult

	def __init__(self, config: FlowGenerateMazeFilesConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		step_result = self.run_step(
			StepGenerateMazeFiles,
			maze_executable_folder=self.config.maze_executable_folder,
			workspace_folder=self.config.workspace_folder,
			count=self.config.count,
		)

		if self.handle_errors(step_result, self.result):
			return

		self.result.workspace_folder = step_result.workspace_folder
		self.result.files_generated = step_result.files_generated

from __future__ import annotations

from test_group_structure_and_lifecycle.test_setup_and_teardown.steps.step_delete_maze_files import StepDeleteMazeFiles

from orcraft import (
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class FlowDeleteMazeFilesConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Delete Maze Files")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class FlowDeleteMazeFilesResult(OrcraftTestFlowResult):
	files_removed = OrcraftResultField.Numeric(default=0, label="Files Removed")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class FlowDeleteMazeFiles(OrcraftTestFlow):
	result_type = FlowDeleteMazeFilesResult

	def __init__(self, config: FlowDeleteMazeFilesConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		step_result = self.run_step(
			StepDeleteMazeFiles,
			workspace_folder=self.config.workspace_folder,
		)

		if self.handle_errors(step_result, self.result):
			return

		self.result.files_removed = step_result.files_removed

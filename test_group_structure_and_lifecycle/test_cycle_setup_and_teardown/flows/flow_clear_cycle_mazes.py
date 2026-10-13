from __future__ import annotations

from test_group_structure_and_lifecycle.test_cycle_setup_and_teardown.steps.step_clear_cycle_mazes import (
	StepClearCycleMazes,
)

from orcraft import (
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class FlowClearCycleMazesConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Clear Cycle Mazes")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class FlowClearCycleMazesResult(OrcraftTestFlowResult):
	workspace_folder = OrcraftResultField.Text(default="", label="Workspace Folder")
	files_removed = OrcraftResultField.Numeric(default=0, label="Files Removed")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class FlowClearCycleMazes(OrcraftTestFlow):
	result_type = FlowClearCycleMazesResult

	def __init__(self, config: FlowClearCycleMazesConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		step_result = self.run_step(
			StepClearCycleMazes,
			workspace_folder=self.config.workspace_folder,
		)

		if self.handle_errors(step_result, self.result):
			return

		self.result.workspace_folder = step_result.workspace_folder
		self.result.files_removed = step_result.files_removed

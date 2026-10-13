from __future__ import annotations

import os

from common.maze_file_utils import normalize_long_path

from orcraft import (
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class StepClearCycleMazesConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Clear Cycle Mazes")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepClearCycleMazesResult(OrcraftTestStepResult):
	workspace_folder = OrcraftResultField.Text(default="", label="Workspace Folder")
	files_removed = OrcraftResultField.Numeric(default=0, label="Files Removed")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepClearCycleMazes(OrcraftTestStep):
	"""Drop the maze files this cycle generated, keeping the workspace folder.

	The folder itself belongs to the test scope, so only the per-cycle fixtures
	are removed here — the next cycle's setup regenerates them from scratch.
	"""

	def __init__(self, config: StepClearCycleMazesConfig | None = None) -> None:
		super().__init__(config or StepClearCycleMazesConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepClearCycleMazesResult()

		workspace_folder = normalize_long_path(self.config.workspace_folder)

		if not workspace_folder or not os.path.isdir(workspace_folder):
			self.checkpoint(True, f"No workspace folder to clear: {workspace_folder}", "")
			return self.result

		removed = 0
		for entry in os.listdir(workspace_folder):
			if entry.startswith("maze_") and entry.endswith(".json"):
				try:
					os.remove(os.path.join(workspace_folder, entry))
					removed += 1
				except OSError:
					# Cleanup problems must not mask the cycle result.
					pass

		self.result.workspace_folder = workspace_folder
		self.result.files_removed = removed
		self.checkpoint(
			True,
			f"Cleared {removed} maze file(s) from {workspace_folder}.",
			"",
		)

		return self.result

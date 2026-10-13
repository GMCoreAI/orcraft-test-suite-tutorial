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


class StepDeleteMazeFilesConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Delete Maze Files")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepDeleteMazeFilesResult(OrcraftTestStepResult):
	files_removed = OrcraftResultField.Numeric(default=0, label="Files Removed")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepDeleteMazeFiles(OrcraftTestStep):
	"""Delete every maze file setup generated, then remove the workspace folder.

	This is the kind of work a test does once, *after* all cases run: clean up
	the shared fixtures so nothing is left behind.
	"""

	def __init__(self, config: StepDeleteMazeFilesConfig | None = None) -> None:
		super().__init__(config or StepDeleteMazeFilesConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepDeleteMazeFilesResult()

		workspace_folder = normalize_long_path(self.config.workspace_folder)

		if not workspace_folder or not os.path.isdir(workspace_folder):
			self.checkpoint(
				True,
				f"No workspace folder to clean up: {workspace_folder}",
				"",
			)
			return self.result

		removed = 0
		for entry in os.listdir(workspace_folder):
			if entry.startswith("maze_") and entry.endswith(".json"):
				try:
					os.remove(os.path.join(workspace_folder, entry))
					removed += 1
				except OSError:
					pass

		# Remove the folder itself if it is now empty.
		try:
			if not os.listdir(workspace_folder):
				os.rmdir(workspace_folder)
		except OSError:
			pass

		self.result.files_removed = removed
		self.checkpoint(
			True,
			f"Removed {removed} maze file(s) from {workspace_folder}.",
			"",
		)

		return self.result

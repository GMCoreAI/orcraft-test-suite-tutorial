from __future__ import annotations

import os

from common.maze_file_utils import maze_file_for_index, normalize_long_path

from orcraft import (
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class StepReleaseCaseMazeConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Release Case Maze")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	maze_index = OrcraftConfigField.Numeric(default=1, label="Maze Index")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepReleaseCaseMazeResult(OrcraftTestStepResult):
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	file_removed = OrcraftResultField.Boolean(default=False, label="File Removed")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepReleaseCaseMaze(OrcraftTestStep):
	"""Drop the maze file this case owned, once all of its cycles have finished.

	The per-cycle setup regenerates the whole set, so releasing a single case
	fixture here never starves the cases that follow.
	"""

	def __init__(self, config: StepReleaseCaseMazeConfig | None = None) -> None:
		super().__init__(config or StepReleaseCaseMazeConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepReleaseCaseMazeResult()

		workspace_folder = normalize_long_path(self.config.workspace_folder)
		maze_index = int(self.config.maze_index)

		if not workspace_folder:
			self.checkpoint(True, "No workspace folder to release.", "")
			return self.result

		maze_file = maze_file_for_index(workspace_folder, maze_index)
		removed = False

		if os.path.isfile(maze_file):
			try:
				os.remove(maze_file)
				removed = True
			except OSError as exc:
				# Cleanup problems must not mask the case result.
				self.checkpoint(True, f"Could not remove {maze_file}: {exc}", "")
				return self.result

		self.result.maze_file_path = maze_file
		self.result.file_removed = removed
		self.checkpoint(
			True,
			f"Released case maze {maze_index}: {maze_file} (removed={removed})",
			"",
		)

		return self.result

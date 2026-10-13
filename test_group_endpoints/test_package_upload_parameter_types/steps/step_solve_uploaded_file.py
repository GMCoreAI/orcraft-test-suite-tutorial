from __future__ import annotations

import os

from common.maze_app import MazeApp
from common.maze_file_utils import normalize_long_path

from orcraft import (
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class StepSolveUploadedFileConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Solve Uploaded File")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	maze_file = OrcraftConfigField.PackageFile(default="", label="Maze File")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepSolveUploadedFileResult(OrcraftTestStepResult):
	path_found = OrcraftResultField.Boolean(default=False, label="Path Found")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepSolveUploadedFile(OrcraftTestStep):
	"""Solves a single maze uploaded via a PackageFile parameter.

	The path arrives already rewritten to its remote upload location, so the step
	simply solves it.
	"""

	def __init__(self, config: StepSolveUploadedFileConfig | None = None) -> None:
		super().__init__(config or StepSolveUploadedFileConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepSolveUploadedFileResult()

		maze_file = normalize_long_path(self.config.maze_file)

		self.checkpoint(
			bool(maze_file) and os.path.exists(maze_file),
			f"Uploaded maze file exists: {maze_file}",
			f"Uploaded maze file is missing: {maze_file}",
		)

		if not (maze_file and os.path.exists(maze_file)):
			return self.result

		result = MazeApp(
			normalize_long_path(self.config.maze_executable_folder),
			"solve",
			maze_file=maze_file,
		).run()

		self.result.path_found = result.solved

		if result.solved:
			self.result.path_length = result.steps

		self.checkpoint(
			result.solved,
			f"Solved {os.path.basename(maze_file)} in {result.steps} step(s).",
			f"No path found for {os.path.basename(maze_file)}.",
		)

		return self.result

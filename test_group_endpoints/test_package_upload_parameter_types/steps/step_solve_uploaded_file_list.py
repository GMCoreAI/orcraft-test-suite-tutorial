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


class StepSolveUploadedFileListConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Solve Uploaded File List")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	maze_files = OrcraftConfigField.PackageFileList(default=(), label="Maze Files")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepSolveUploadedFileListResult(OrcraftTestStepResult):
	mazes_solved = OrcraftResultField.Numeric(default=0, label="Mazes Solved")
	mazes_total = OrcraftResultField.Numeric(default=0, label="Mazes Total")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepSolveUploadedFileList(OrcraftTestStep):
	"""Solves every maze uploaded via a PackageFileList parameter.

	Each path in the list arrives already rewritten to its remote upload location.
	"""

	def __init__(self, config: StepSolveUploadedFileListConfig | None = None) -> None:
		super().__init__(config or StepSolveUploadedFileListConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepSolveUploadedFileListResult()

		maze_executable_folder = normalize_long_path(self.config.maze_executable_folder)
		maze_files = [normalize_long_path(maze_file) for maze_file in self.config.maze_files if normalize_long_path(maze_file)]

		self.checkpoint(
			bool(maze_files),
			f"Received {len(maze_files)} uploaded maze file(s) to solve.",
			"No uploaded maze files were provided.",
		)

		if not maze_files:
			return self.result

		solved_count = 0

		for maze_file in maze_files:
			file_exists = os.path.exists(maze_file)
			self.checkpoint(
				file_exists,
				f"Uploaded maze file exists: {maze_file}",
				f"Uploaded maze file is missing: {maze_file}",
			)

			if not file_exists:
				continue

			result = MazeApp(
				maze_executable_folder,
				"solve",
				maze_file=maze_file,
			).run()

			if result.solved:
				solved_count += 1

			self.checkpoint(
				result.solved,
				f"Solved {os.path.basename(maze_file)} in {result.steps} step(s).",
				f"No path found for {os.path.basename(maze_file)}.",
			)

		self.result.mazes_total = len(maze_files)
		self.result.mazes_solved = solved_count

		return self.result

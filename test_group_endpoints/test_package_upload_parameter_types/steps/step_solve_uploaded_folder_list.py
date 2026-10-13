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


class StepSolveUploadedFolderListConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Solve Uploaded Folder List")
	maze_folders = OrcraftConfigField.PackageFolderList(default=(), label="Maze Folders")
	width = OrcraftConfigField.Numeric(default=10, label="Width")
	height = OrcraftConfigField.Numeric(default=10, label="Height")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepSolveUploadedFolderListResult(OrcraftTestStepResult):
	versions_solved = OrcraftResultField.Numeric(default=0, label="Versions Solved")
	versions_total = OrcraftResultField.Numeric(default=0, label="Versions Total")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepSolveUploadedFolderList(OrcraftTestStep):
	"""Runs each maze app version uploaded via a PackageFolderList parameter.

	Each uploaded folder is a self-contained maze app version (its own executable).
	The step runs every version's executable once — generating and solving a fresh
	maze with that version's binary. Any maze files inside the folders are ignored;
	the point is to exercise each uploaded version.
	"""

	def __init__(self, config: StepSolveUploadedFolderListConfig | None = None) -> None:
		super().__init__(config or StepSolveUploadedFolderListConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepSolveUploadedFolderListResult()

		solved_count = 0
		total_count = 0

		for maze_folder in self.config.maze_folders:
			normalized_folder = normalize_long_path(maze_folder)
			if not normalized_folder:
				continue

			total_count += 1

			# Run this version's own executable to generate and solve a fresh maze.
			maze_app = MazeApp(
				normalized_folder,
				"solve",
				width=self.config.width,
				height=self.config.height,
			)
			result = maze_app.run()

			if result.solved:
				solved_count += 1

			version = maze_app.get_version() or "unknown"
			self.checkpoint(
				result.solved,
				f"Maze app v{version} solved a fresh maze in {result.steps} step(s).",
				f"Maze app v{version} found no path.",
			)

		self.result.versions_total = total_count
		self.result.versions_solved = solved_count

		return self.result

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


class StepPrepareCaseMazeConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Prepare Case Maze")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	maze_index = OrcraftConfigField.Numeric(default=1, label="Maze Index")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepPrepareCaseMazeResult(OrcraftTestStepResult):
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	maze_file_size = OrcraftResultField.Numeric(default=0, label="Maze File Size")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepPrepareCaseMaze(OrcraftTestStep):
	"""Claim the one maze file this case owns, before any of its cycles run.

	This is the kind of work a test does once *per case*: validate the single
	fixture that case depends on, instead of the whole shared set.
	"""

	def __init__(self, config: StepPrepareCaseMazeConfig | None = None) -> None:
		super().__init__(config or StepPrepareCaseMazeConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepPrepareCaseMazeResult()

		workspace_folder = normalize_long_path(self.config.workspace_folder)
		maze_index = int(self.config.maze_index)

		self.checkpoint(
			bool(workspace_folder),
			f"Workspace folder set: {workspace_folder}",
			"Workspace folder is empty.",
		)

		if not workspace_folder:
			return self.result

		maze_file = maze_file_for_index(workspace_folder, maze_index)
		file_size = os.path.getsize(maze_file) if os.path.isfile(maze_file) else 0

		self.checkpoint(
			file_size > 0,
			f"Case maze {maze_index} is ready: {maze_file} ({file_size} bytes)",
			f"Case maze {maze_index} is missing or empty: {maze_file}",
		)

		if file_size <= 0:
			return self.result

		self.result.maze_file_path = maze_file
		self.result.maze_file_size = file_size

		return self.result

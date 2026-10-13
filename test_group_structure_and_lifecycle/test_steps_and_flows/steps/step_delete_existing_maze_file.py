from __future__ import annotations

import os

from common.maze_file_utils import make_maze_file_path, normalize_long_path

from orcraft import (
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class StepDeleteExistingMazeFileConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Delete Existing Maze File")
	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")
	subfolder = OrcraftConfigField.Text(default="", label="Subfolder")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepDeleteExistingMazeFileResult(OrcraftTestStepResult):
	maze_file = OrcraftResultField.Text(default="", label="Maze File")
	maze_folder = OrcraftResultField.Text(default="", label="Maze Folder")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepDeleteExistingMazeFile(OrcraftTestStep):
	def __init__(self, config: StepDeleteExistingMazeFileConfig | None = None) -> None:
		super().__init__(config or StepDeleteExistingMazeFileConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepDeleteExistingMazeFileResult()

		subfolder = normalize_long_path(self.config.subfolder)
		if subfolder:
			import tempfile
			output_folder = os.path.join(tempfile.gettempdir(), subfolder)
		else:
			output_folder = ""

		maze_file = make_maze_file_path(
			output_folder,
			self.config.width,
			self.config.height,
		)

		self.result.maze_file = maze_file
		self.result.maze_folder = maze_file.rsplit("/", 1)[0]

		was_deleted = os.path.exists(maze_file)

		if was_deleted:
			os.remove(maze_file)

		self.checkpoint(
			True,
			f"Existing maze file deleted: {maze_file}" if was_deleted else f"No existing maze file (nothing to delete): {maze_file}",
			"",
		)

		return self.result

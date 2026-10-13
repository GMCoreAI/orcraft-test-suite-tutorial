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


class StepGenerateSaveConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Generate / Save")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	maze_file = OrcraftConfigField.Text(default="", label="Maze File")
	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepGenerateSaveResult(OrcraftTestStepResult):
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	maze_area = OrcraftResultField.Numeric(default=0, label="Maze Area")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepGenerateSave(OrcraftTestStep):
	def __init__(self, config: StepGenerateSaveConfig | None = None) -> None:
		super().__init__(config or StepGenerateSaveConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepGenerateSaveResult()

		maze_file = normalize_long_path(self.config.maze_file)

		self.checkpoint(bool(maze_file), "Maze file path is set.", "Maze file path is empty.")

		if not maze_file:
			return self.result

		parent = os.path.dirname(maze_file)
		if parent:
			os.makedirs(parent, exist_ok=True)

		MazeApp(
			normalize_long_path(self.config.maze_executable_folder),
			"save",
			width=self.config.width,
			height=self.config.height,
			maze_file=maze_file,
		).run()

		file_exists = os.path.exists(maze_file)
		self.checkpoint(
			file_exists,
			f"Maze file created: {maze_file}",
			f"Maze file was not created: {maze_file}",
		)

		if not file_exists:
			return self.result

		file_size = os.path.getsize(maze_file)
		self.checkpoint(
			file_size > 0,
			f"Maze file is non-empty ({file_size} bytes).",
			f"Maze file is empty: {maze_file}",
		)

		if file_size <= 0:
			return self.result

		self.result.maze_file_path = maze_file
		self.result.maze_area = self.config.width * self.config.height

		return self.result

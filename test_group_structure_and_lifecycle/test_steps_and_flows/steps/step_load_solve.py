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


class StepLoadSolveConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Load / Solve")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	maze_file = OrcraftConfigField.Text(default="", label="Maze File")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepLoadSolveResult(OrcraftTestStepResult):
	path_found = OrcraftResultField.Boolean(default=False, label="Path Found")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepLoadSolve(OrcraftTestStep):
	def __init__(self, config: StepLoadSolveConfig | None = None) -> None:
		super().__init__(config or StepLoadSolveConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepLoadSolveResult()

		maze_file = normalize_long_path(self.config.maze_file)

		self.checkpoint(
			bool(maze_file),
			"Maze file path is set.",
			"Maze file path is empty.",
		)

		if not maze_file:
			return self.result

		self.checkpoint(
			os.path.exists(maze_file),
			f"Maze file exists: {maze_file}",
			f"Maze file does not exist: {maze_file}",
		)

		if not os.path.exists(maze_file):
			return self.result

		result = MazeApp(
			normalize_long_path(self.config.maze_executable_folder),
			"solve",
			maze_file=maze_file,
		).run()

		self.result.path_found = result.solved

		if result.solved:
			self.result.path_length = result.steps

		return self.result

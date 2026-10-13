from __future__ import annotations

import os

from common.maze_app import MazeApp
from common.maze_file_utils import normalize_long_path

from common.maze_file_utils import maze_file_for_index

from orcraft import (
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class StepSolveMazeConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Solve Maze")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	maze_index = OrcraftConfigField.Numeric(default=1, label="Maze Index")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepSolveMazeResult(OrcraftTestStepResult):
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	path_found = OrcraftResultField.Boolean(default=False, label="Path Found")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepSolveMaze(OrcraftTestStep):
	"""Load and solve the maze file that setup generated for this case's index."""

	def __init__(self, config: StepSolveMazeConfig | None = None) -> None:
		super().__init__(config or StepSolveMazeConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepSolveMazeResult()

		workspace_folder = normalize_long_path(self.config.workspace_folder)
		maze_file = maze_file_for_index(workspace_folder, int(self.config.maze_index))

		self.checkpoint(
			os.path.exists(maze_file),
			f"Maze file exists: {maze_file}",
			f"Maze file does not exist (was setup skipped?): {maze_file}",
		)

		if not os.path.exists(maze_file):
			return self.result

		result = MazeApp(
			normalize_long_path(self.config.maze_executable_folder),
			"solve",
			maze_file=maze_file,
		).run()

		self.result.maze_file_path = maze_file
		self.result.path_found = result.solved

		if result.solved:
			self.result.path_length = result.steps

		self.checkpoint(
			result.solved,
			f"Path found: {result.steps} step(s).",
			"No path found in maze output.",
		)

		return self.result

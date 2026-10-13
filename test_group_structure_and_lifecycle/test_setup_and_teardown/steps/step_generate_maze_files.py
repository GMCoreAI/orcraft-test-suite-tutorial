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


class StepGenerateMazeFilesConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Generate Maze Files")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	workspace_folder = OrcraftConfigField.Text(default="", label="Workspace Folder")
	count = OrcraftConfigField.Numeric(default=10, label="Maze Count")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepGenerateMazeFilesResult(OrcraftTestStepResult):
	workspace_folder = OrcraftResultField.Text(default="", label="Workspace Folder")
	files_generated = OrcraftResultField.Numeric(default=0, label="Files Generated")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepGenerateMazeFiles(OrcraftTestStep):
	"""Generate the shared set of maze files that every case will later solve.

	This is the kind of work a test does once, *before* any case runs: build the
	fixtures all cases depend on. Each file gets a slightly larger maze and a
	distinct seed so the cases exercise different mazes.
	"""

	def __init__(self, config: StepGenerateMazeFilesConfig | None = None) -> None:
		super().__init__(config or StepGenerateMazeFilesConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepGenerateMazeFilesResult()

		workspace_folder = normalize_long_path(self.config.workspace_folder)
		count = int(self.config.count)

		self.checkpoint(
			bool(workspace_folder) and count > 0,
			f"Workspace folder set and count is {count}.",
			"Workspace folder is empty or count is not positive.",
		)

		if not workspace_folder or count <= 0:
			return self.result

		os.makedirs(workspace_folder, exist_ok=True)

		executable_folder = normalize_long_path(self.config.maze_executable_folder)
		generated = 0

		for index in range(1, count + 1):
			maze_file = maze_file_for_index(workspace_folder, index)
			width = 5 + index
			height = 5 + index

			MazeApp(
				executable_folder,
				"save",
				width=width,
				height=height,
				seed=index,
				maze_file=maze_file,
			).run()

			file_ok = os.path.exists(maze_file) and os.path.getsize(maze_file) > 0
			self.checkpoint(
				file_ok,
				f"Generated maze {index}/{count}: {maze_file}",
				f"Failed to generate maze {index}/{count}: {maze_file}",
			)

			if not file_ok:
				return self.result

			generated += 1

		self.result.workspace_folder = workspace_folder
		self.result.files_generated = generated

		return self.result

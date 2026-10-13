from __future__ import annotations

import os

from common.maze_file_utils import normalize_long_path, wall_off_end

from orcraft import (
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class StepCorruptSavedFileConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Corrupt Saved File")
	maze_file = OrcraftConfigField.Text(default="", label="Maze File")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class StepCorruptSavedFileResult(OrcraftTestStepResult):
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class StepCorruptSavedFile(OrcraftTestStep):
	def __init__(self, config: StepCorruptSavedFileConfig | None = None) -> None:
		super().__init__(config or StepCorruptSavedFileConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepCorruptSavedFileResult()

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

		_, _, _ = wall_off_end(maze_file)

		return self.result

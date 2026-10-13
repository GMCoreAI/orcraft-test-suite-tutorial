from __future__ import annotations

import os
import socket

from orcraft import (
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftResultField,
	OrcraftConfigField,
)

from test_group_structure_and_lifecycle.test_steps_and_flows.steps.step_delete_existing_maze_file import StepDeleteExistingMazeFile
from test_group_structure_and_lifecycle.test_steps_and_flows.steps.step_generate_save import StepGenerateSave
from test_group_structure_and_lifecycle.test_steps_and_flows.steps.step_corrupt_saved_file import StepCorruptSavedFile
from test_group_structure_and_lifecycle.test_steps_and_flows.steps.step_load_solve import StepLoadSolve


class FlowGenerateSaveCorruptLoadSolveConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Generate/Save -> Corrupt Saved File -> Load/Solve")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class FlowGenerateSaveCorruptLoadSolveResult(OrcraftTestFlowResult):
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	maze_area = OrcraftResultField.Numeric(default=0, label="Maze Area")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class FlowGenerateSaveCorruptLoadSolve(OrcraftTestFlow):
	result_type = FlowGenerateSaveCorruptLoadSolveResult

	def __init__(self, config: FlowGenerateSaveCorruptLoadSolveConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		# A folder of this run's own: several runs may share one endpoint at the
		# same time, and each must generate, corrupt and solve its own file.
		step_1_result = self.run_step(
			StepDeleteExistingMazeFile,
			subfolder=f"orcraft-maze-{socket.gethostname()}-{os.getpid()}",
			width=self.config.width,
			height=self.config.height,
		)

		if self.handle_errors(step_1_result, self.result):
			return

		step_2_result = self.run_step(
			StepGenerateSave,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_file=step_1_result.maze_file,
			width=self.config.width,
			height=self.config.height,
		)

		if self.handle_errors(step_2_result, self.result):
			return

		self.result.maze_file_path = step_2_result.maze_file_path
		self.result.maze_area = step_2_result.maze_area

		step_3_result = self.run_step(
			StepCorruptSavedFile,
			maze_file=step_2_result.maze_file_path,
		)

		if self.handle_errors(step_3_result, self.result):
			return

		step_4_result = self.run_step(
			StepLoadSolve,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_file=step_2_result.maze_file_path,
		)

		if self.handle_errors(step_4_result, self.result):
			return

		self.checkpoint(
			not step_4_result.path_found,
			"Corrupted maze has no solution as expected.",
			"Corrupted maze unexpectedly returned a solution.",
		)

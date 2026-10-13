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
from test_group_structure_and_lifecycle.test_steps_and_flows.steps.step_load_solve import StepLoadSolve


class FlowGenerateSaveLoadSolveConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Generate/Save -> Load/Solve")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class FlowGenerateSaveLoadSolveResult(OrcraftTestFlowResult):
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	maze_area = OrcraftResultField.Numeric(default=0, label="Maze Area")
	path_length = OrcraftResultField.Numeric(default=0, label="Path Length")
	area_path_ratio = OrcraftResultField.Numeric(default=0.0, label="Area/Path Ratio")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class FlowGenerateSaveLoadSolve(OrcraftTestFlow):
	result_type = FlowGenerateSaveLoadSolveResult

	def __init__(self, config: FlowGenerateSaveLoadSolveConfig) -> None:
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
			StepLoadSolve,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_file=step_2_result.maze_file_path,
		)

		if self.handle_errors(step_3_result, self.result):
			return

		self.result.path_length = step_3_result.path_length

		if step_3_result.path_found and step_3_result.path_length > 0:
			self.result.area_path_ratio = round(step_2_result.maze_area / step_3_result.path_length, 2)
			self.checkpoint(
				step_3_result.path_length <= step_2_result.maze_area,
				f"Path length ({step_3_result.path_length}) is within maze area ({step_2_result.maze_area}).",
				f"Path length ({step_3_result.path_length}) exceeds maze area ({step_2_result.maze_area}) — unexpected.",
			)

		self.checkpoint(
			step_3_result.path_found,
			f"Path found: {step_3_result.path_length} step(s).",
			"No path found in maze output.",
		)

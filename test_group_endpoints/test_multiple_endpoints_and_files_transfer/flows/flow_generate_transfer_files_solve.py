from __future__ import annotations

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


class FlowGenerateTransferFilesSolveConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Generate Two Mazes -> Transfer Files -> Solve")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	endpoint_1 = OrcraftConfigField.Endpoint(default="localhost", label="Endpoint 1")
	endpoint_2 = OrcraftConfigField.Endpoint(default="localhost", label="Endpoint 2")
	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class FlowGenerateTransferFilesSolveResult(OrcraftTestFlowResult):
	maze_area_1 = OrcraftResultField.Numeric(default=0, label="Maze Area A")
	maze_area_2 = OrcraftResultField.Numeric(default=0, label="Maze Area B")
	path_length_1 = OrcraftResultField.Numeric(default=0, label="Path Length A")
	path_length_2 = OrcraftResultField.Numeric(default=0, label="Path Length B")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class FlowGenerateTransferFilesSolve(OrcraftTestFlow):
	result_type = FlowGenerateTransferFilesSolveResult

	def __init__(self, config: FlowGenerateTransferFilesSolveConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		# Step 1a: delete any existing maze A file on test endpoint (width × height)
		step_1a_result = self.run_step(
			StepDeleteExistingMazeFile,
			endpoint=self.config.endpoint_1,
			width=self.config.width,
			height=self.config.height,
		)

		if self.handle_errors(step_1a_result, self.result):
			return

		# Step 1b: delete any existing maze B file on test endpoint (height × width)
		step_1b_result = self.run_step(
			StepDeleteExistingMazeFile,
			endpoint=self.config.endpoint_1,
			width=self.config.height,
			height=self.config.width,
		)

		if self.handle_errors(step_1b_result, self.result):
			return

		# Step 2a: generate and save maze A on test endpoint (width × height)
		step_2a_result = self.run_step(
			StepGenerateSave,
			endpoint=self.config.endpoint_1,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_file=step_1a_result.maze_file,
			width=self.config.width,
			height=self.config.height,
		)

		if self.handle_errors(step_2a_result, self.result):
			return

		self.result.maze_area_1 = step_2a_result.maze_area

		# Step 2b: generate and save maze B on test endpoint (height × width)
		step_2b_result = self.run_step(
			StepGenerateSave,
			endpoint=self.config.endpoint_1,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_file=step_1b_result.maze_file,
			width=self.config.height,
			height=self.config.width,
		)

		if self.handle_errors(step_2b_result, self.result):
			return

		self.result.maze_area_2 = step_2b_result.maze_area

		# Transfer both mazes from test endpoint to aux endpoint in a single call
		transfer_result = self.transfer(
			src_endpoint=self.config.endpoint_1,
			dst_endpoint=self.config.endpoint_2,
			paths=[
				step_2a_result.maze_file_path,
				step_2b_result.maze_file_path,
			],
		)
		if transfer_result:
			return

		# Step 3a: solve maze A on aux endpoint
		step_3a_result = self.run_step(
			StepLoadSolve,
			endpoint=self.config.endpoint_2,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_file=transfer_result.dst_paths[0],
		)

		if self.handle_errors(step_3a_result, self.result):
			return

		self.result.path_length_1 = step_3a_result.path_length

		# Step 3b: solve maze B on aux endpoint
		step_3b_result = self.run_step(
			StepLoadSolve,
			endpoint=self.config.endpoint_2,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_file=transfer_result.dst_paths[1],
		)

		if self.handle_errors(step_3b_result, self.result):
			return

		self.result.path_length_2 = step_3b_result.path_length

		self.checkpoint(
			step_3a_result.path_found and step_3b_result.path_found,
			"Both mazes solved on aux endpoint after transfer.",
			"One or both mazes failed to solve after transfer.",
		)

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


class FlowGenerateTransferFileSolveConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Generate -> Transfer File -> Solve")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	endpoint_1 = OrcraftConfigField.Endpoint(default="localhost", label="Endpoint 1")
	endpoint_2 = OrcraftConfigField.Endpoint(default="localhost", label="Endpoint 2")
	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class FlowGenerateTransferFileSolveResult(OrcraftTestFlowResult):
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	maze_area = OrcraftResultField.Numeric(default=0, label="Maze Area")
	path_length = OrcraftResultField.Numeric(default=0, label="Path Length")
	area_path_ratio = OrcraftResultField.Numeric(default=0.0, label="Area/Path Ratio")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class FlowGenerateTransferFileSolve(OrcraftTestFlow):
	result_type = FlowGenerateTransferFileSolveResult

	def __init__(self, config: FlowGenerateTransferFileSolveConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		# Step 1: delete any existing maze file on test endpoint
		step_1_result = self.run_step(
			StepDeleteExistingMazeFile,
			endpoint=self.config.endpoint_1,
			width=self.config.width,
			height=self.config.height,
		)

		if self.handle_errors(step_1_result, self.result):
			return

		# Step 2: generate and save maze on test endpoint
		step_2_result = self.run_step(
			StepGenerateSave,
			endpoint=self.config.endpoint_1,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_file=step_1_result.maze_file,
			width=self.config.width,
			height=self.config.height,
		)

		if self.handle_errors(step_2_result, self.result):
			return

		self.result.maze_file_path = step_2_result.maze_file_path
		self.result.maze_area = step_2_result.maze_area

		# Transfer the maze file from test endpoint to aux endpoint
		transfer_result = self.transfer(
			src_endpoint=self.config.endpoint_1,
			dst_endpoint=self.config.endpoint_2,
			paths=step_2_result.maze_file_path,
		)
		if transfer_result:
			return

		# Step 3: load and solve the transferred maze on aux endpoint
		step_3_result = self.run_step(
			StepLoadSolve,
			endpoint=self.config.endpoint_2,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_file=transfer_result.dst_paths[0],
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
			f"Path found on endpoint 2 after transfer: {step_3_result.path_length} step(s).",
			"No path found after cross-endpoint transfer.",
		)

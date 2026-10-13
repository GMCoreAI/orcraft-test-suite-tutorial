from __future__ import annotations

from orcraft import (
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftConfigField,
)

from test_group_endpoints.test_type_fidelity.steps.step_produce_maze_typed_data import StepProduceMazeTypedData
from test_group_endpoints.test_type_fidelity.steps.step_verify_maze_typed_data import StepVerifyMazeTypedData


class FlowTypeFidelityConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Type Fidelity")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	test_endpoint = OrcraftConfigField.Endpoint(default="localhost")
	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")


class FlowTypeFidelityResult(OrcraftTestFlowResult):
	pass


class FlowTypeFidelity(OrcraftTestFlow):
	result_type = FlowTypeFidelityResult

	def __init__(self, config: FlowTypeFidelityConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		# Step 1: Generate a maze on the test endpoint and assemble typed result data
		step_1_result = self.run_step(
			StepProduceMazeTypedData,
			endpoint=self.config.test_endpoint,
			maze_executable_folder=self.config.maze_executable_folder,
			width=self.config.width,
			height=self.config.height,
		)

		if self.handle_errors(step_1_result, self.result):
			return

		# Step 2: Verify that all types survived the RPC round-trip
		step_2_result = self.run_step(
			StepVerifyMazeTypedData,
			endpoint=self.config.test_endpoint,
			dimensions=step_1_result.dimensions,
			solve_status=step_1_result.solve_status,
			start_coords=step_1_result.start_coords,
			metadata=step_1_result.metadata,
		)

		if self.handle_errors(step_2_result, self.result):
			return

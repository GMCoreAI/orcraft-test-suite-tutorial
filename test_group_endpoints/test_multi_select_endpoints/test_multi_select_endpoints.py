from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestCase,
	OrcraftTestConfig,
	OrcraftTestResult,
	OrcraftResultField,
	OrcraftConfigField,
)

from test_group_endpoints.test_multiple_endpoints_and_files_transfer.flows.flow_generate_transfer_file_solve import FlowGenerateTransferFileSolve, FlowGenerateTransferFileSolveConfig
from test_group_endpoints.test_multiple_endpoints_and_files_transfer.flows.flow_generate_transfer_files_solve import FlowGenerateTransferFilesSolve, FlowGenerateTransferFilesSolveConfig
from test_group_endpoints.test_multiple_endpoints_and_files_transfer.flows.flow_generate_transfer_folder_solve import FlowGenerateTransferFolderSolve, FlowGenerateTransferFolderSolveConfig


class TestMultiSelectEndpointsConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Multi-Select Endpoints")

	description = OrcraftConfigField.Text(
		default=(
			"Uses a single test endpoint as the generator and a set of aux endpoints as solvers. "
			"For each aux endpoint, runs the same three file-transfer flows as the "
			"Multiple Endpoints and Files Transfer test.\n"
			"Flow 1 generates a maze on the test endpoint, transfers the single file "
			"to the aux endpoint, then solves it there.\n"
			"Flow 2 generates two mazes on the test endpoint, transfers both files in "
			"a single call to the aux endpoint, then solves them there.\n"
			"Flow 3 generates two mazes into a dedicated subfolder on the test endpoint, "
			"transfers the entire folder to the aux endpoint in one call, then solves both mazes there."
		)
	)

	test_endpoint = OrcraftConfigField.Endpoint(default="localhost", label="Test Endpoint")
	aux_endpoints = OrcraftConfigField.MultiSelectEndpoints(default=("localhost",), label="Aux Endpoints")

	maze_executable_folder = OrcraftConfigField.PackageFolder(
		default="",
		label="Maze Executable Folder",
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
	)

	matrix = OrcraftConfigField.Matrix(
		OrcraftConfigField.Dimension("width", (5, 10)),
		OrcraftConfigField.Dimension("height", (8, 12)),
	)

	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class TestMultiSelectEndpointsResult(OrcraftTestResult):
	maze_area = OrcraftResultField.Numeric(default=None, label="Maze Area")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")
	area_path_ratio = OrcraftResultField.Numeric(default=None, label="Area/Path Ratio")
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class TestMultiSelectEndpoints(OrcraftTest):
	def __init__(self, config: TestMultiSelectEndpointsConfig | None = None) -> None:
		super().__init__(config or TestMultiSelectEndpointsConfig())

	def _run_case(self, case: OrcraftTestCase) -> OrcraftTestResult:
		case.result = TestMultiSelectEndpointsResult()

		for aux_endpoint in self.config.aux_endpoints:
			# Flow 1: generate on test endpoint, transfer single file, solve on aux endpoint
			flow_1 = FlowGenerateTransferFileSolve(
				FlowGenerateTransferFileSolveConfig(
					maze_executable_folder=self.config.maze_executable_folder,
					endpoint_1=self.config.test_endpoint,
					endpoint_2=aux_endpoint,
					width=case.params["width"],
					height=case.params["height"],
				)
			)
			flow_1_result = flow_1.run()

			if self.handle_errors(flow_1_result, case.result):
				return case.result

			case.result.maze_area = flow_1_result.maze_area
			case.result.path_length = flow_1_result.path_length
			case.result.area_path_ratio = flow_1_result.area_path_ratio
			case.result.maze_file_path = flow_1_result.maze_file_path

			# Flow 2: generate two mazes on test endpoint, transfer both files, solve on aux endpoint
			flow_2 = FlowGenerateTransferFilesSolve(
				FlowGenerateTransferFilesSolveConfig(
					maze_executable_folder=self.config.maze_executable_folder,
					endpoint_1=self.config.test_endpoint,
					endpoint_2=aux_endpoint,
					width=case.params["width"],
					height=case.params["height"],
				)
			)
			flow_2_result = flow_2.run()

			if self.handle_errors(flow_2_result, case.result):
				return case.result

			# Flow 3: generate two mazes into a subfolder, transfer the folder, solve on aux endpoint
			flow_3 = FlowGenerateTransferFolderSolve(
				FlowGenerateTransferFolderSolveConfig(
					maze_executable_folder=self.config.maze_executable_folder,
					endpoint_1=self.config.test_endpoint,
					endpoint_2=aux_endpoint,
					width=case.params["width"],
					height=case.params["height"],
				)
			)
			flow_3_result = flow_3.run()

			if self.handle_errors(flow_3_result, case.result):
				return case.result

		return case.result


def main() -> None:
	test = TestMultiSelectEndpoints()
	test.run()


if __name__ == "__main__":
	main()

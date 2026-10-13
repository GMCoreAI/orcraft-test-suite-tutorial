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


class TestEndpointFanoutPermutationsConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Endpoint Fanout - Permutations")

	description = OrcraftConfigField.Text(
		default=(
			"Uses Endpoint 1 as the generator and Endpoint 2 as the solver. "
			"Both Endpoint 1 and Endpoint 2 are fanout parameters — selecting multiple endpoints in the Run dialog "
			"spawns a separate test run for every combination (permutation) of the two automatically.\n"
			"Because Endpoint 1 is also a fanout parameter, runs that share the same Endpoint 1 are no longer "
			"guaranteed to write to the same fixed paths, so they are not queued — each permutation is an "
			"independent run.\n"
			"Flow 1 generates a maze on Endpoint 1, transfers the single file "
			"to Endpoint 2, then solves it there.\n"
			"Flow 2 generates two mazes on Endpoint 1, transfers both files in "
			"a single call to Endpoint 2, then solves them there.\n"
			"Flow 3 generates two mazes into a dedicated subfolder on Endpoint 1, "
			"transfers the entire folder to Endpoint 2 in one call, then solves both mazes there."
		)
	)

	endpoint_1 = OrcraftConfigField.EndpointFanout(default=("localhost",), label="Endpoint 1")
	endpoint_2 = OrcraftConfigField.EndpointFanout(default=("localhost",), label="Endpoint 2")

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


class TestEndpointFanoutPermutationsResult(OrcraftTestResult):
	maze_area = OrcraftResultField.Numeric(default=None, label="Maze Area")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")
	area_path_ratio = OrcraftResultField.Numeric(default=None, label="Area/Path Ratio")
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class TestEndpointFanoutPermutations(OrcraftTest):
	def __init__(self, config: TestEndpointFanoutPermutationsConfig | None = None) -> None:
		super().__init__(config or TestEndpointFanoutPermutationsConfig())

	def _run_case(self, case: OrcraftTestCase) -> OrcraftTestResult:
		case.result = TestEndpointFanoutPermutationsResult()

		# Flow 1: generate on Endpoint 1, transfer single file, solve on Endpoint 2
		flow_1 = FlowGenerateTransferFileSolve(
			FlowGenerateTransferFileSolveConfig(
				maze_executable_folder=self.config.maze_executable_folder,
				endpoint_1=self.config.endpoint_1,
				endpoint_2=self.config.endpoint_2,
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

		# Flow 2: generate two mazes on Endpoint 1, transfer both files, solve on Endpoint 2
		flow_2 = FlowGenerateTransferFilesSolve(
			FlowGenerateTransferFilesSolveConfig(
				maze_executable_folder=self.config.maze_executable_folder,
				endpoint_1=self.config.endpoint_1,
				endpoint_2=self.config.endpoint_2,
				width=case.params["width"],
				height=case.params["height"],
			)
		)
		flow_2_result = flow_2.run()

		if self.handle_errors(flow_2_result, case.result):
			return case.result

		# Flow 3: generate two mazes into a subfolder, transfer the folder, solve on Endpoint 2
		flow_3 = FlowGenerateTransferFolderSolve(
			FlowGenerateTransferFolderSolveConfig(
				maze_executable_folder=self.config.maze_executable_folder,
				endpoint_1=self.config.endpoint_1,
				endpoint_2=self.config.endpoint_2,
				width=case.params["width"],
				height=case.params["height"],
			)
		)
		flow_3_result = flow_3.run()

		if self.handle_errors(flow_3_result, case.result):
			return case.result

		return case.result


def main() -> None:
	test = TestEndpointFanoutPermutations()
	test.run()


if __name__ == "__main__":
	main()

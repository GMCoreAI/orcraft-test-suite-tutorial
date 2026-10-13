from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestCase,
	OrcraftTestConfig,
	OrcraftTestResult,
	OrcraftResultField,
	OrcraftConfigField,
)

from test_group_structure_and_lifecycle.test_steps_and_flows.flows.flow_generate_save_load_solve import FlowGenerateSaveLoadSolve, FlowGenerateSaveLoadSolveConfig
from test_group_structure_and_lifecycle.test_steps_and_flows.flows.flow_generate_save_corrupt_load_solve import FlowGenerateSaveCorruptLoadSolve, FlowGenerateSaveCorruptLoadSolveConfig


class TestDefaultEndpointAndPackageUploadConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Default Endpoint and Package Upload")

	description = OrcraftConfigField.Text(
		default=(
			"Runs the same flows as the Steps and Flows test, but targets the default test endpoint.\n"
			"Demonstrates how adding a test endpoint parameter routes execution to a remote machine "
			"with no changes to the flows or steps themselves.\n"
			"Flow 1 generates a maze, saves it to a file, then loads and solves it — verifying the full round trip.\n"
			"Flow 2 does the same but corrupts the saved file by walling off the end point, "
			"then verifies the solver finds no path."
		)
	)

	test_endpoint = OrcraftConfigField.Endpoint(default="localhost", label="Test Endpoint")

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


class TestDefaultEndpointAndPackageUploadResult(OrcraftTestResult):
	maze_area = OrcraftResultField.Numeric(default=None, label="Maze Area")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")
	area_path_ratio = OrcraftResultField.Numeric(default=None, label="Area/Path Ratio")
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class TestDefaultEndpointAndPackageUpload(OrcraftTest):
	def __init__(self, config: TestDefaultEndpointAndPackageUploadConfig | None = None) -> None:
		super().__init__(config or TestDefaultEndpointAndPackageUploadConfig())

	def _run_case(self, case: OrcraftTestCase) -> OrcraftTestResult:
		case.result = TestDefaultEndpointAndPackageUploadResult()

		# Flow: Generate/Save -> Load/Solve
		flow_generate_save = FlowGenerateSaveLoadSolve(
			FlowGenerateSaveLoadSolveConfig(
				maze_executable_folder=self.config.maze_executable_folder,
				width=case.params["width"],
				height=case.params["height"],
			)
		)
		flow_generate_save_result = flow_generate_save.run()

		if self.handle_errors(flow_generate_save_result, case.result):
			return case.result

		case.result.maze_area = flow_generate_save_result.maze_area
		case.result.path_length = flow_generate_save_result.path_length
		case.result.area_path_ratio = flow_generate_save_result.area_path_ratio
		case.result.maze_file_path = flow_generate_save_result.maze_file_path

		# Flow: Generate/Save -> Corrupt Saved File -> Load/Solve
		flow_generate_save_corrupt = FlowGenerateSaveCorruptLoadSolve(
			FlowGenerateSaveCorruptLoadSolveConfig(
				maze_executable_folder=self.config.maze_executable_folder,
				width=case.params["width"],
				height=case.params["height"],
			)
		)

		flow_generate_save_corrupt_result = flow_generate_save_corrupt.run()

		if self.handle_errors(flow_generate_save_corrupt_result, case.result):
			return case.result

		return case.result


def main() -> None:
	test = TestDefaultEndpointAndPackageUpload()
	test.run()


if __name__ == "__main__":
	main()

from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestCase,
	OrcraftTestConfig,
	OrcraftTestResult,
	OrcraftResultField,
	OrcraftConfigField,
)

from test_group_endpoints.test_package_upload_parameter_types.flows.flow_solve_uploaded_mazes import (
	FlowSolveUploadedMazes,
	FlowSolveUploadedMazesConfig,
)


class TestPackageUploadParameterTypesConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Package Upload Parameter Types")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates every package-upload parameter type and how each can be linked to "
			"specific endpoints so files upload only where they are needed."
		)
	)

	test_endpoint = OrcraftConfigField.Endpoint(default="localhost", label="Test Endpoint")
	endpoint_1 = OrcraftConfigField.EndpointFanout(default=("localhost",), label="Endpoint 1")
	endpoint_2 = OrcraftConfigField.Endpoint(default="localhost", label="Endpoint 2")
	aux_endpoints = OrcraftConfigField.MultiSelectEndpoints(default=("localhost",), label="Aux Endpoints")

	maze_executable_folder = OrcraftConfigField.PackageFolder(
		default="",
		label="Maze Executable Folder",
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
	)

	maze_file = OrcraftConfigField.PackageFile(
		default="",
		label="Maze File",
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
		endpoints=[endpoint_1],
	)

	maze_files = OrcraftConfigField.PackageFileList(
		default=(),
		label="Maze Files",
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
		endpoints=[endpoint_2],
	)

	maze_folders = OrcraftConfigField.PackageFolderList(
		default=(),
		label="Maze Folders",
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
		endpoints=[test_endpoint, aux_endpoints],
	)

	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class TestPackageUploadParameterTypesResult(OrcraftTestResult):
	mazes_solved = OrcraftResultField.Numeric(default=0, label="Mazes Solved")
	mazes_total = OrcraftResultField.Numeric(default=0, label="Mazes Total")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class TestPackageUploadParameterTypes(OrcraftTest):
	def __init__(self, config: TestPackageUploadParameterTypesConfig | None = None) -> None:
		super().__init__(config or TestPackageUploadParameterTypesConfig())

	def _run_case(self, case: OrcraftTestCase) -> OrcraftTestResult:
		case.result = TestPackageUploadParameterTypesResult()

		flow = FlowSolveUploadedMazes(
			FlowSolveUploadedMazesConfig(
				maze_executable_folder=self.config.maze_executable_folder,
				maze_file=self.config.maze_file,
				maze_files=self.config.maze_files,
				maze_folders=self.config.maze_folders,
				test_endpoint=self.config.test_endpoint,
				endpoint_2=self.config.endpoint_2,
				endpoint_1=self.config.endpoint_1,
			)
		)

		flow_result = flow.run()

		if self.handle_errors(flow_result, case.result):
			return case.result

		case.result.mazes_solved = flow_result.mazes_solved
		case.result.mazes_total = flow_result.mazes_total

		return case.result


def main() -> None:
	test = TestPackageUploadParameterTypes()
	test.run()


if __name__ == "__main__":
	main()

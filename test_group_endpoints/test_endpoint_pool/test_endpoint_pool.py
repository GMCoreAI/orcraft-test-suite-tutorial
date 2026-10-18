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


class TestEndpointPoolConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Endpoint Pool")

	description = OrcraftConfigField.Text(
		default=(
			"Uses a test endpoint as the generator and two aux endpoints as solvers, like the Multi-Select "
			"Endpoints test, but none of the machines is named in the test: every endpoint field's default is "
			"an endpoint pool, and the run picks the machines when it starts.\n"
			"The test endpoint asks for any available machine whose operating system is Linux or Windows. "
			"The aux endpoints ask for any two available machines with distinct operating systems.\n"
			"A pool's conditions are Query records: match keeps the machines whose attribute has one of the "
			"values, distinct makes the picked machines differ on the attribute; count says how many machines "
			"a multi-select pool takes. A pool never takes the test's own machine twice, and never localhost.\n"
			"The Run dialog shows each pool with Any available ticked and may change it for a run: other "
			"conditions, fewer candidates, another count, or machines picked by hand.\n"
			"The test body is the same either way: by the time it runs, the fields hold the picked endpoints.\n"
			"This test needs three remote endpoints, two of them of different operating systems; with fewer "
			"the run is refused before it starts.\n"
			"For each aux endpoint, the flow generates a maze on the test endpoint, transfers the file to the "
			"aux endpoint and solves it there."
		)
	)

	test_endpoint = OrcraftConfigField.Endpoint(
		default=OrcraftConfigField.EndpointPool(
			OrcraftConfigField.Query.match("os", ("Linux", "Windows")),
		),
		label="Test Endpoint",
	)

	aux_endpoints = OrcraftConfigField.MultiSelectEndpoints(
		default=OrcraftConfigField.EndpointPool(
			OrcraftConfigField.Query.distinct("os"),
			count=2,
		),
		label="Aux Endpoints",
	)

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


class TestEndpointPoolResult(OrcraftTestResult):
	maze_area = OrcraftResultField.Numeric(default=None, label="Maze Area")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")
	area_path_ratio = OrcraftResultField.Numeric(default=None, label="Area/Path Ratio")
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class TestEndpointPool(OrcraftTest):
	def __init__(self, config: TestEndpointPoolConfig | None = None) -> None:
		super().__init__(config or TestEndpointPoolConfig())

	def _run_case(self, case: OrcraftTestCase) -> OrcraftTestResult:
		case.result = TestEndpointPoolResult()

		for aux_endpoint in self.config.aux_endpoints:
			# Generate on the picked test endpoint, transfer the file, solve on the picked aux endpoint
			flow = FlowGenerateTransferFileSolve(
				FlowGenerateTransferFileSolveConfig(
					maze_executable_folder=self.config.maze_executable_folder,
					endpoint_1=self.config.test_endpoint,
					endpoint_2=aux_endpoint,
					width=case.params["width"],
					height=case.params["height"],
				)
			)
			flow_result = flow.run()

			if self.handle_errors(flow_result, case.result):
				return case.result

			case.result.maze_area = flow_result.maze_area
			case.result.path_length = flow_result.path_length
			case.result.area_path_ratio = flow_result.area_path_ratio
			case.result.maze_file_path = flow_result.maze_file_path

		return case.result


def main() -> None:
	test = TestEndpointPool()
	test.run()


if __name__ == "__main__":
	main()

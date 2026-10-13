from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestCase,
	OrcraftTestConfig,
	OrcraftTestResult,
	OrcraftConfigField,
)

from test_group_endpoints.test_type_fidelity.flows.flow_type_fidelity import (
	FlowTypeFidelity,
	FlowTypeFidelityConfig,
)


class TestTypeFidelityConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Type Fidelity")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates that Orcraft's RPC serialization preserves Python types "
			"(tuples, enums, nested structures) across remote step execution.\n"
			"On the test endpoint, the maze app generates a maze and the result is assembled "
			"into structured typed data: a tuple of dimensions, a MazeSolveStatus enum, "
			"tuple coordinates, and a nested dict with mixed types.\n"
			"A second step on the same endpoint verifies that every type was preserved "
			"exactly after the RPC round-trip."
		)
	)

	test_endpoint = OrcraftConfigField.Endpoint(default="localhost", label="Test Endpoint")

	maze_executable_folder = OrcraftConfigField.PackageFolder(
		default="",
		label="Maze Executable Folder",
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
	)

	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")


class TestTypeFidelityResult(OrcraftTestResult):
	pass


class TestTypeFidelity(OrcraftTest):
	def __init__(self, config: TestTypeFidelityConfig | None = None) -> None:
		super().__init__(config or TestTypeFidelityConfig())

	def _run_case(self, case: OrcraftTestCase) -> OrcraftTestResult:
		case.result = TestTypeFidelityResult()

		flow = FlowTypeFidelity(
			FlowTypeFidelityConfig(
				maze_executable_folder=self.config.maze_executable_folder,
				test_endpoint=self.config.test_endpoint,
				width=self.config.width,
				height=self.config.height,
			)
		)
		flow_result = flow.run()

		if self.handle_errors(flow_result, case.result):
			return case.result

		return case.result

		return case.result


def main() -> None:
	test = TestTypeFidelity()
	test.run()


if __name__ == "__main__":
	main()

from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestCase,
	OrcraftTestConfig,
	OrcraftTestResult,
	OrcraftResultField,
	OrcraftConfigField,
)

from test_group_endpoints.test_controlled_endpoint_disconnection.flows.flow_endpoint_lifecycle import (
	FlowEndpointLifecycle,
	FlowEndpointLifecycleConfig,
)


class TestEndpointRestartConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Endpoint Restart")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates endpoint process restart to refresh the OS environment without a full machine reboot.\n"
			"A maze is generated and saved on the test endpoint before the restart.\n"
			"The endpoint process is then restarted using the Orcraft restart API. "
			"After reconnection, the saved maze is loaded and solved to verify the endpoint has recovered.\n"
			"The test endpoint is a fanout parameter — selecting multiple endpoints in the Run dialog "
			"spawns a separate test run for each one automatically."
		)
	)

	test_endpoint = OrcraftConfigField.EndpointFanout(default=("localhost",), label="Test Endpoint")

	maze_executable_folder = OrcraftConfigField.PackageFolder(
		default="",
		label="Maze Executable Folder",
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
	)

	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")
	disconnect_timeout_sec = OrcraftConfigField.Numeric(default=120, label="Disconnect Timeout Sec")
	connect_timeout_sec = OrcraftConfigField.Numeric(default=300, label="Connect Timeout Sec")


class TestEndpointRestartResult(OrcraftTestResult):
	maze_area = OrcraftResultField.Numeric(default=None, label="Maze Area")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")


class TestEndpointRestart(OrcraftTest):
	def __init__(self, config: TestEndpointRestartConfig | None = None) -> None:
		super().__init__(config or TestEndpointRestartConfig())

	def _run_case(self, case: OrcraftTestCase) -> OrcraftTestResult:
		case.result = TestEndpointRestartResult()

		flow = FlowEndpointLifecycle(
			FlowEndpointLifecycleConfig(
				test_endpoint=self.config.test_endpoint,
				maze_executable_folder=self.config.maze_executable_folder,
				width=self.config.width,
				height=self.config.height,
				mode="restart",
				disconnect_timeout_sec=self.config.disconnect_timeout_sec,
				connect_timeout_sec=self.config.connect_timeout_sec,
			)
		)

		flow_result = flow.run()

		if self.handle_errors(flow_result, case.result):
			return case.result

		case.result.maze_area = flow_result.maze_area
		case.result.path_length = flow_result.path_length

		return case.result


def main() -> None:
	test = TestEndpointRestart()
	test.run()


if __name__ == "__main__":
	main()

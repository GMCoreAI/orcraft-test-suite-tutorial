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


class TestControlledEndpointDisconnectionConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Controlled Endpoint Disconnection")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates controlled endpoint reboot with graceful disconnection and reconnection handling.\n"
			"Before the reboot, a maze is generated and solved on the test endpoint to confirm it is functional. "
			"The endpoint is then rebooted (set enable_reboot=True) or skipped (enable_reboot=False for dry runs).\n"
			"After reconnection, a maze is generated and solved again to verify the endpoint has recovered fully."
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
	enable_reboot = OrcraftConfigField.Boolean(default=False, label="Enable Reboot")
	reboot_delay_sec = OrcraftConfigField.Numeric(default=0, label="Reboot Delay Sec")
	disconnect_timeout_sec = OrcraftConfigField.Numeric(default=60, label="Disconnect Timeout Sec")
	connect_timeout_sec = OrcraftConfigField.Numeric(default=300, label="Connect Timeout Sec")


class TestControlledEndpointDisconnectionResult(OrcraftTestResult):
	maze_area = OrcraftResultField.Numeric(default=None, label="Maze Area")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")


class TestControlledEndpointDisconnectionResult(OrcraftTestResult):
	maze_area = OrcraftResultField.Numeric(default=None, label="Maze Area")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")


class TestControlledEndpointDisconnection(OrcraftTest):
	def __init__(self, config: TestControlledEndpointDisconnectionConfig | None = None) -> None:
		super().__init__(config or TestControlledEndpointDisconnectionConfig())

	def _run_case(self, case: OrcraftTestCase) -> OrcraftTestResult:
		case.result = TestControlledEndpointDisconnectionResult()

		flow = FlowEndpointLifecycle(
			FlowEndpointLifecycleConfig(
				test_endpoint=(self.config.test_endpoint,),
				maze_executable_folder=self.config.maze_executable_folder,
				width=self.config.width,
				height=self.config.height,
				mode="disconnect",
				enable_reboot=self.config.enable_reboot,
				reboot_delay_sec=self.config.reboot_delay_sec,
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
	test = TestControlledEndpointDisconnection()
	test.run()


if __name__ == "__main__":
	main()

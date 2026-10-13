from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestCase,
	OrcraftTestConfig,
	OrcraftTestResult,
	OrcraftResultField,
	OrcraftConfigField,
)

from test_group_endpoints.test_remote_thread_example.flows.flow_remote_thread import (
	FlowRemoteThread,
	FlowRemoteThreadConfig,
)


class TestRemoteThreadExampleConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Remote Thread Example")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates that a step result can carry an arbitrary Python object (a thread handle) "
			"and be accessed again in a later step.\n"
			"Step 1 starts a background thread on the test endpoint that continuously solves mazes. "
			"Step 2 simply waits, letting the thread accumulate results. "
			"Step 3 retrieves the same task object from Step 1 to stop the thread and collect the count."
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
	wait_sec = OrcraftConfigField.Numeric(default=2.0, label="Wait Sec")


class TestRemoteThreadExampleResult(OrcraftTestResult):
	mazes_generated = OrcraftResultField.Numeric(default=0, label="Mazes Generated")
	avg_path_steps = OrcraftResultField.Numeric(default=0, label="Avg Path Steps")


class TestRemoteThreadExample(OrcraftTest):
	def __init__(self, config: TestRemoteThreadExampleConfig | None = None) -> None:
		super().__init__(config or TestRemoteThreadExampleConfig())

	def _run_case(self, case: OrcraftTestCase) -> OrcraftTestResult:
		case.result = TestRemoteThreadExampleResult()

		flow = FlowRemoteThread(
			FlowRemoteThreadConfig(
				maze_executable_folder=self.config.maze_executable_folder,
				test_endpoint=self.config.test_endpoint,
				width=self.config.width,
				height=self.config.height,
				wait_sec=self.config.wait_sec,
			)
		)
		flow_result = flow.run()

		if self.handle_errors(flow_result, case.result):
			return case.result

		case.result.mazes_generated = flow_result.mazes_generated
		case.result.avg_path_steps = flow_result.avg_path_steps

		return case.result


def main() -> None:
	test = TestRemoteThreadExample()
	test.run()


if __name__ == "__main__":
	main()

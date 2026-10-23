from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestResult,
	OrcraftTestCase,
	OrcraftConfigField,
	OrcraftResultField,
)

from test_group_endpoints.test_hello_endpoint.flows.flow_hello_endpoint import (
	FlowHelloEndpoint,
	FlowHelloEndpointConfig,
)


class TestHelloEndpointConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Hello Endpoint")

	description = OrcraftConfigField.Text(
		default=(
			"The simplest test that runs on an endpoint.\n"
			"One flow sends one step to the Test Endpoint; the step runs the hostname command there and logs the answer.\n"
			"With the default localhost the step runs on the controller's machine; choose an endpoint in the run panel and it runs there."
		)
	)

	test_endpoint = OrcraftConfigField.Endpoint(default="localhost", label="Test Endpoint")


class TestHelloEndpointResult(OrcraftTestResult):
	hostname = OrcraftResultField.Text(default="", label="Hostname")


class TestHelloEndpoint(OrcraftTest):
	def __init__(self, config: TestHelloEndpointConfig | None = None) -> None:
		super().__init__(config or TestHelloEndpointConfig())

	def _run_case(self, case: OrcraftTestCase) -> OrcraftTestResult:
		case.result = TestHelloEndpointResult()

		flow = FlowHelloEndpoint(FlowHelloEndpointConfig())
		flow_result = flow.run()

		if self.handle_errors(flow_result, case.result):
			return case.result

		case.result.hostname = flow_result.hostname

		return case.result


def main() -> None:
	test = TestHelloEndpoint()
	test.run()


if __name__ == "__main__":
	main()

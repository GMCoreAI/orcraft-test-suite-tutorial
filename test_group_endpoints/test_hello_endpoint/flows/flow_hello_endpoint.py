from __future__ import annotations

from orcraft import (
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftResultField,
	OrcraftConfigField,
)

from test_group_endpoints.test_hello_endpoint.steps.step_hostname import StepHostname


class FlowHelloEndpointConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Hello Endpoint")


class FlowHelloEndpointResult(OrcraftTestFlowResult):
	hostname = OrcraftResultField.Text(default="", label="Hostname")


class FlowHelloEndpoint(OrcraftTestFlow):
	result_type = FlowHelloEndpointResult

	def __init__(self, config: FlowHelloEndpointConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		# No endpoint is named here: the step goes to the test's Test Endpoint.
		step_result = self.run_step(StepHostname)

		if self.handle_errors(step_result, self.result):
			return

		self.result.hostname = step_result.hostname

from __future__ import annotations

from orcraft import (
	OrcraftEndpointState,
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftResultField,
	OrcraftConfigField,
)

from test_group_structure_and_lifecycle.test_steps_and_flows.steps.step_delete_existing_maze_file import StepDeleteExistingMazeFile
from test_group_structure_and_lifecycle.test_steps_and_flows.steps.step_generate_save import StepGenerateSave
from test_group_structure_and_lifecycle.test_steps_and_flows.steps.step_load_solve import StepLoadSolve
from test_group_endpoints.test_controlled_endpoint_disconnection.steps.step_trigger_reboot import StepTriggerReboot


class FlowEndpointLifecycleConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Endpoint Lifecycle")
	test_endpoint = OrcraftConfigField.EndpointFanout(default=("localhost",))
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")
	mode = OrcraftConfigField.Text(default="disconnect")  # "disconnect" or "restart"
	enable_reboot = OrcraftConfigField.Boolean(default=False, label="Enable Reboot")
	reboot_delay_sec = OrcraftConfigField.Numeric(default=0, label="Reboot Delay Sec")
	disconnect_timeout_sec = OrcraftConfigField.Numeric(default=60, label="Disconnect Timeout Sec")
	connect_timeout_sec = OrcraftConfigField.Numeric(default=300, label="Connect Timeout Sec")


class FlowEndpointLifecycleResult(OrcraftTestFlowResult):
	maze_area = OrcraftResultField.Numeric(default=None, label="Maze Area")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")


class FlowEndpointLifecycle(OrcraftTestFlow):
	result_type = FlowEndpointLifecycleResult

	def __init__(self, config: FlowEndpointLifecycleConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		endpoint = self._resolve_endpoint()

		# Step 1: delete any existing maze file
		step_1_result = self.run_step(
			StepDeleteExistingMazeFile,
			endpoint=endpoint,
			width=self.config.width,
			height=self.config.height,
		)

		if self.handle_errors(step_1_result, self.result):
			return

		# Step 2: generate and save the maze before disconnection
		step_2_result = self.run_step(
			StepGenerateSave,
			endpoint=endpoint,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_file=step_1_result.maze_file,
			width=self.config.width,
			height=self.config.height,
		)

		if self.handle_errors(step_2_result, self.result):
			return

		# Trigger disconnect or restart
		mode = self.config.mode

		if mode == "disconnect":
			step_trigger = self.run_step(
				StepTriggerReboot,
				endpoint=endpoint,
				enable_reboot=self.config.enable_reboot,
				reboot_delay_sec=self.config.reboot_delay_sec,
			)

			if self.handle_errors(step_trigger, self.result):
				return

			if self.config.enable_reboot:
				if self.wait_for_endpoint_state(
					OrcraftEndpointState.OFFLINE,
					endpoint=endpoint,
					timeout_sec=self.config.disconnect_timeout_sec,
				):
					return
			else:
				if self.wait_for_endpoint_state(
					OrcraftEndpointState.ONLINE,
					endpoint=endpoint,
					timeout_sec=self.config.disconnect_timeout_sec,
				):
					return

			if self.wait_for_endpoint_state(
				OrcraftEndpointState.READY,
				endpoint=endpoint,
				timeout_sec=self.config.connect_timeout_sec,
				poll_interval_sec=5,
			):
				return

		elif mode == "restart":
			if self.restart_endpoint(
				endpoint=endpoint,
				disconnect_timeout_sec=self.config.disconnect_timeout_sec,
				connect_timeout_sec=self.config.connect_timeout_sec,
			):
				return

		# Step 3: load and solve the saved maze to confirm the endpoint has recovered
		step_3_result = self.run_step(
			StepLoadSolve,
			endpoint=endpoint,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_file=step_2_result.maze_file_path,
		)

		if self.handle_errors(step_3_result, self.result):
			return

		self.result.maze_area = step_2_result.maze_area
		self.result.path_length = step_3_result.path_length

		self.checkpoint(
			step_3_result.path_found,
			f"Endpoint recovered — maze solved in {step_3_result.path_length} step(s).",
			"Endpoint did not recover — maze could not be solved after reconnection.",
		)

	def _resolve_endpoint(self) -> object:
		value = getattr(self.config, "test_endpoint", None)
		if isinstance(value, (list, tuple, set)):
			for ep in value:
				if ep:
					return ep
			return "localhost"
		return value or "localhost"

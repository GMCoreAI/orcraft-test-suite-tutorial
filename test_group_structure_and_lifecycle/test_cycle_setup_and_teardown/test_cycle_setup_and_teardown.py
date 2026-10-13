from __future__ import annotations

from orcraft import (
	OrcraftConfigField,
	OrcraftLogger as Logger,
)

from test_group_structure_and_lifecycle.test_setup_and_teardown.test_setup_and_teardown import (
	TestSetupAndTeardown,
	TestSetupAndTeardownConfig,
)
from test_group_structure_and_lifecycle.test_setup_and_teardown.flows.flow_generate_maze_files import (
	FlowGenerateMazeFiles,
	FlowGenerateMazeFilesConfig,
)
from test_group_structure_and_lifecycle.test_cycle_setup_and_teardown.flows.flow_clear_cycle_mazes import (
	FlowClearCycleMazes,
	FlowClearCycleMazesConfig,
)


class TestCycleSetupAndTeardownConfig(TestSetupAndTeardownConfig):
	name = OrcraftConfigField.Text(default="Cycle Setup and Teardown")

	description = OrcraftConfigField.Text(
		default=(
			"Builds on Setup and Teardown by adding the per-test-cycle hooks.\n"
			"_setup()/_teardown() still run once, bracketing the whole test.\n"
			"_test_cycle_setup() runs at the start of every test cycle and regenerates "
			"the maze files, so each cycle starts from freshly generated inputs and never "
			"inherits residue from the previous cycle.\n"
			"_test_cycle_teardown() runs at the end of every test cycle and clears those "
			"files again, leaving the workspace folder itself to the test scope.\n"
			"With two cycles you can see the test-cycle banners nested inside each cycle."
		)
	)

	# Two cycles and a small matrix make the added per-cycle scope easy to read.
	number_of_cycles = OrcraftConfigField.Numeric(label="Cycles", default=2)

	matrix = OrcraftConfigField.Matrix(
		OrcraftConfigField.Dimension("maze_index", tuple(range(1, 4))),
	)


class TestCycleSetupAndTeardown(TestSetupAndTeardown):
	def __init__(self, config: TestCycleSetupAndTeardownConfig | None = None) -> None:
		super().__init__(config or TestCycleSetupAndTeardownConfig())

	def _test_cycle_setup(self, test_cycle_index: int) -> None:
		workspace_folder = self._workspace_folder()
		maze_count = int(self.config.maze_count)

		Logger.log(
			f"Test cycle {test_cycle_index}: regenerating {maze_count} maze files "
			f"in {workspace_folder}",
			color=Logger.Color.CYAN,
		)

		flow = FlowGenerateMazeFiles(
			FlowGenerateMazeFilesConfig(
				maze_executable_folder=self.config.maze_executable_folder,
				workspace_folder=workspace_folder,
				count=maze_count,
			)
		)

		# Raising here fails only this cycle; the next cycle still runs.
		if self.handle_errors(flow.run(), self.result):
			raise RuntimeError(
				self.result.error_description
				or self.result.failure_description
				or "Test cycle setup failed to regenerate the maze files."
			)

	def _test_cycle_teardown(self, test_cycle_index: int) -> None:
		workspace_folder = self._workspace_folder()

		Logger.log(
			f"Test cycle {test_cycle_index}: clearing the maze files it generated "
			f"in {workspace_folder}",
			color=Logger.Color.CYAN,
		)

		# Teardown does not raise — cleanup problems should not mask cycle results.
		FlowClearCycleMazes(
			FlowClearCycleMazesConfig(
				workspace_folder=workspace_folder,
			)
		).run()


def main() -> None:
	test = TestCycleSetupAndTeardown()
	test.run()


if __name__ == "__main__":
	main()

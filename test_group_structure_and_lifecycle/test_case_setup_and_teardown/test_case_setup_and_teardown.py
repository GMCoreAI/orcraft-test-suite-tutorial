from __future__ import annotations

from orcraft import (
	OrcraftConfigField,
	OrcraftTestCase,
	OrcraftLogger as Logger,
)

from test_group_structure_and_lifecycle.test_cycle_setup_and_teardown.test_cycle_setup_and_teardown import (
	TestCycleSetupAndTeardown,
	TestCycleSetupAndTeardownConfig,
)
from test_group_structure_and_lifecycle.test_case_setup_and_teardown.flows.flow_prepare_case_maze import (
	FlowPrepareCaseMaze,
	FlowPrepareCaseMazeConfig,
)
from test_group_structure_and_lifecycle.test_case_setup_and_teardown.flows.flow_release_case_maze import (
	FlowReleaseCaseMaze,
	FlowReleaseCaseMazeConfig,
)


class TestCaseSetupAndTeardownConfig(TestCycleSetupAndTeardownConfig):
	name = OrcraftConfigField.Text(default="Case Setup and Teardown")

	description = OrcraftConfigField.Text(
		default=(
			"Builds on Cycle Setup and Teardown by adding the per-case hooks.\n"
			"_setup()/_teardown() bracket the whole test; _test_cycle_setup()/"
			"_test_cycle_teardown() bracket each test cycle.\n"
			"_case_setup() runs one flow that claims the single maze file the case "
			"owns, and _case_teardown() runs one flow that releases it again — both "
			"nested beneath the case banner, with their flows and steps shown inside "
			"the setup and teardown scopes.\n"
			"With two test cycles and two case cycles you can see all four lifecycle "
			"scopes at once."
		)
	)

	# Two case cycles make the per-case scope (which brackets the case cycles)
	# clearly distinct from the case-cycle loop it wraps.
	case_number_of_cycles = OrcraftConfigField.Numeric(label="Case Cycles", default=2)


class TestCaseSetupAndTeardown(TestCycleSetupAndTeardown):
	def __init__(self, config: TestCaseSetupAndTeardownConfig | None = None) -> None:
		super().__init__(config or TestCaseSetupAndTeardownConfig())

	def _case_setup(self, case: OrcraftTestCase, test_cycle_index: int) -> None:
		maze_index = case.params["maze_index"]

		Logger.log(
			f"Case setup (cycle {test_cycle_index}): claiming maze_index={maze_index}",
			color=Logger.Color.CYAN,
		)

		flow = FlowPrepareCaseMaze(
			FlowPrepareCaseMazeConfig(
				workspace_folder=self._workspace_folder(),
				maze_index=maze_index,
			)
		)

		# Raising from _case_setup fails this case only: its case cycles are
		# skipped and the matching _case_teardown does not run.
		flow_result = flow.run()
		if self.handle_errors(flow_result, case.result):
			raise RuntimeError(
				case.result.error_description
				or case.result.failure_description
				or f"Case setup could not claim the maze file for maze_index={maze_index}."
			)

	def _case_teardown(self, case: OrcraftTestCase, test_cycle_index: int) -> None:
		maze_index = case.params["maze_index"]

		Logger.log(
			f"Case teardown (cycle {test_cycle_index}): releasing maze_index={maze_index}",
			color=Logger.Color.CYAN,
		)

		# Teardown does not raise — cleanup problems should not mask case results.
		FlowReleaseCaseMaze(
			FlowReleaseCaseMazeConfig(
				workspace_folder=self._workspace_folder(),
				maze_index=maze_index,
			)
		).run()


def main() -> None:
	test = TestCaseSetupAndTeardown()
	test.run()


if __name__ == "__main__":
	main()

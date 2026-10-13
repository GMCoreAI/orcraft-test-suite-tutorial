from __future__ import annotations

from orcraft import (
	OrcraftTestGroup,
	OrcraftTestGroupConfig,
	OrcraftTestGroupResult,
	OrcraftConfigField,
)

from test_group_structure_and_lifecycle.test_steps_and_flows.test_steps_and_flows import TestStepsAndFlows
from test_group_structure_and_lifecycle.test_setup_and_teardown.test_setup_and_teardown import TestSetupAndTeardown
from test_group_structure_and_lifecycle.test_cycle_setup_and_teardown.test_cycle_setup_and_teardown import TestCycleSetupAndTeardown
from test_group_structure_and_lifecycle.test_case_setup_and_teardown.test_case_setup_and_teardown import TestCaseSetupAndTeardown


class TestGroupStructureAndLifecycleConfig(OrcraftTestGroupConfig):
	name = OrcraftConfigField.Text(default="Structure and Lifecycle")
	description = OrcraftConfigField.Text(
		default=(
			"Shows how a test is built (structure) and when its optional hooks run (lifecycle).\n"
			"Steps and Flows composes a test body from reusable steps and flows.\n"
			"The setup/teardown tests then add one lifecycle scope at a time — test, then "
			"test cycle, then case — so each test is a strict superset of the previous one."
		)
	)
	tests = OrcraftConfigField.Tests(
		default_factory=lambda: [
			TestStepsAndFlows(),
			TestSetupAndTeardown(),
			TestCycleSetupAndTeardown(),
			TestCaseSetupAndTeardown(),
		]
	)


class TestGroupStructureAndLifecycleResult(OrcraftTestGroupResult):
	pass


class TestGroupStructureAndLifecycle(OrcraftTestGroup):
	def __init__(self) -> None:
		super().__init__(config=TestGroupStructureAndLifecycleConfig())
		self.result = TestGroupStructureAndLifecycleResult()


def main() -> None:
	group = TestGroupStructureAndLifecycle()
	group.run()


if __name__ == "__main__":
	main()

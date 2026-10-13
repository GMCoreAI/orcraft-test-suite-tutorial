from __future__ import annotations

from orcraft import (
	OrcraftTestGroup,
	OrcraftTestGroupConfig,
	OrcraftTestGroupResult,
	OrcraftConfigField,
)

from test_group_statuses_and_results.test_status_pass_with_warning.test_status_pass_with_warning import TestStatusPassWithWarning
from test_group_statuses_and_results.test_status_fail.test_status_fail import TestStatusFail
from test_group_statuses_and_results.test_status_error.test_status_error import TestStatusError
from test_group_statuses_and_results.test_checkpoints.test_checkpoints import TestCheckpoints
from test_group_statuses_and_results.test_result_fields.test_result_fields import TestResultFields


class TestGroupStatusesAndResultsConfig(OrcraftTestGroupConfig):
	name = OrcraftConfigField.Text(default="Statuses and Results")
	description = OrcraftConfigField.Text(
		default=(
			"Covers tests that demonstrate how to capture and validate test output.\n"
			"Shows how custom result fields expose meaningful data and how status is set to Fail\n"
			"when the actual output does not match what is expected."
		)
	)
	tests = OrcraftConfigField.Tests(
		default_factory=lambda: [
			TestStatusPassWithWarning(),
			TestStatusFail(),
			TestStatusError(),
			TestCheckpoints(),
			TestResultFields(),
		]
	)


class TestGroupStatusesAndResultsResult(OrcraftTestGroupResult):
	pass


class TestGroupStatusesAndResults(OrcraftTestGroup):
	def __init__(self) -> None:
		super().__init__(config=TestGroupStatusesAndResultsConfig())
		self.result = TestGroupStatusesAndResultsResult()


def main() -> None:
	group = TestGroupStatusesAndResults()
	group.run()


if __name__ == "__main__":
	main()

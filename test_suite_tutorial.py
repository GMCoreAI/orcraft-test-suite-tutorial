from __future__ import annotations

from orcraft import (
	OrcraftTestSuite,
	OrcraftTestSuiteConfig,
	OrcraftTestSuiteResult,
	OrcraftConfigField,
)

from test_group_intro.test_group_intro import TestGroupIntro
from test_group_basic_configuration_parameters.test_group_basic_configuration_parameters import TestGroupBasicConfigurationParameters
from test_group_advanced_configuration_parameters.test_group_advanced_configuration_parameters import TestGroupAdvancedConfigurationParameters
from test_group_statuses_and_results.test_group_statuses_and_results import TestGroupStatusesAndResults
from test_group_structure_and_lifecycle.test_group_structure_and_lifecycle import TestGroupStructureAndLifecycle
from test_group_endpoints.test_group_endpoints import TestGroupEndpoints


class TestSuiteTutorialConfig(OrcraftTestSuiteConfig):
	name = OrcraftConfigField.Text(default="Orcraft Tutorial")
	description = OrcraftConfigField.Text(
		default="Demonstrates the Orcraft tutorial suite with real tests of the maze app."
	)
	version = OrcraftConfigField.Text(default="0.0.1")
	groups = OrcraftConfigField.Groups(
		default_factory=lambda: [
			TestGroupIntro(),
			TestGroupBasicConfigurationParameters(),
			TestGroupAdvancedConfigurationParameters(),
			TestGroupStatusesAndResults(),
			TestGroupStructureAndLifecycle(),
			TestGroupEndpoints(),
		]
	)

class TestSuiteTutorialResult(OrcraftTestSuiteResult):
	pass


class TestSuiteTutorial(OrcraftTestSuite):
	def __init__(self) -> None:
		super().__init__(config=TestSuiteTutorialConfig())
		self.result = TestSuiteTutorialResult()


def main() -> None:
	suite = TestSuiteTutorial()
	# suite.log_info()
	suite.run()


if __name__ == "__main__":
	main()

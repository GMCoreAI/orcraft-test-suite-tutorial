from __future__ import annotations

from orcraft import (
	OrcraftTestGroup,
	OrcraftTestGroupConfig,
	OrcraftTestGroupResult,
	OrcraftConfigField,
)

from test_group_advanced_configuration_parameters.test_lambda_selector_parameter.test_lambda_selector_parameter import TestLambdaSelectorParameter
from test_group_advanced_configuration_parameters.test_lambda_multi_selector_parameter.test_lambda_multi_selector_parameter import TestLambdaMultiSelectorParameter
from test_group_advanced_configuration_parameters.test_matrix_and_cases.test_matrix_and_cases import TestMatrixAndCases
from test_group_advanced_configuration_parameters.test_cases_exclusion.test_cases_exclusion import TestCasesExclusion
from test_group_advanced_configuration_parameters.test_matrix_dimensions_randomization.test_matrix_dimensions_randomization import TestMatrixDimensionsRandomization
from test_group_advanced_configuration_parameters.test_exclude_rules_on_random_dimensions.test_exclude_rules_on_random_dimensions import TestExcludeRulesOnRandomDimensions
from test_group_advanced_configuration_parameters.test_matrix_lambda_dimensions.test_matrix_lambda_dimensions import TestMatrixLambdaDimensions


class TestGroupAdvancedConfigurationParametersConfig(OrcraftTestGroupConfig):
	name = OrcraftConfigField.Text(default="Advanced Configuration Parameters")
	description = OrcraftConfigField.Text(
		default="Covers tests that demonstrate advanced configuration parameters used with the maze app."
	)
	tests = OrcraftConfigField.Tests(
		default_factory=lambda: [
			TestLambdaSelectorParameter(),
			TestLambdaMultiSelectorParameter(),
			TestMatrixAndCases(),
			TestCasesExclusion(),
			TestMatrixDimensionsRandomization(),
			# TestExcludeRulesOnRandomDimensions(),
			TestMatrixLambdaDimensions(),
		]
	)

class TestGroupAdvancedConfigurationParametersResult(OrcraftTestGroupResult):
	pass


class TestGroupAdvancedConfigurationParameters(OrcraftTestGroup):
	def __init__(self) -> None:
		super().__init__(config=TestGroupAdvancedConfigurationParametersConfig())
		self.result = TestGroupAdvancedConfigurationParametersResult()


def main() -> None:
	group = TestGroupAdvancedConfigurationParameters()
	group.run()


if __name__ == "__main__":
	main()

from __future__ import annotations

from orcraft import (
	OrcraftTestGroup,
	OrcraftTestGroupConfig,
	OrcraftTestGroupResult,
	OrcraftConfigField,
)

from test_group_basic_configuration_parameters.test_folder_parameter.test_folder_parameter import TestFolderParameter
from test_group_basic_configuration_parameters.test_boolean_parameter.test_boolean_parameter import TestBooleanParameter
from test_group_basic_configuration_parameters.test_selector_parameter.test_selector_parameter import TestSelectorParameter
from test_group_basic_configuration_parameters.test_folder_list_parameter.test_folder_list_parameter import TestFolderListParameter
from test_group_basic_configuration_parameters.test_file_parameter.test_file_parameter import TestFileParameter
from test_group_basic_configuration_parameters.test_file_list_parameter.test_file_list_parameter import TestFileListParameter
from test_group_basic_configuration_parameters.test_numeric_parameter.test_numeric_parameter import TestNumericParameter
from test_group_basic_configuration_parameters.test_multi_selector_parameter.test_multi_selector_parameter import TestMultiSelectorParameter
from test_group_basic_configuration_parameters.test_string_parameter.test_string_parameter import TestStringParameter


class TestGroupBasicConfigurationParametersConfig(OrcraftTestGroupConfig):
	name = OrcraftConfigField.Text(default="Basic Configuration Parameters")
	description = OrcraftConfigField.Text(
		default="Covers tests that demonstrate configuration parameters used with the maze app."
	)
	tests = OrcraftConfigField.Tests(
		default_factory=lambda: [
			TestFolderParameter(),
			TestBooleanParameter(),
			TestSelectorParameter(),
			TestFolderListParameter(),
			TestFileParameter(),
			TestFileListParameter(),
			TestNumericParameter(),
			TestMultiSelectorParameter(),
			TestStringParameter(),
		]
	)

class TestGroupBasicConfigurationParametersResult(OrcraftTestGroupResult):
	pass


class TestGroupBasicConfigurationParameters(OrcraftTestGroup):
	def __init__(self) -> None:
		super().__init__(config=TestGroupBasicConfigurationParametersConfig())
		self.result = TestGroupBasicConfigurationParametersResult()


def main() -> None:
	group = TestGroupConfigurationParameters()
	group.run()


if __name__ == "__main__":
	main()

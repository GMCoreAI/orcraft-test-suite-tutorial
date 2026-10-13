from __future__ import annotations

import os

from orcraft import (
	OrcraftTest,
	OrcraftTestCase,
	OrcraftTestConfig,
	OrcraftTestResult,
	OrcraftResultField,
	OrcraftConfigField,
	OrcraftLogger as Logger,
)

from common.maze_file_utils import resolve_workspace_folder
from test_group_structure_and_lifecycle.test_setup_and_teardown.flows.flow_generate_maze_files import (
	FlowGenerateMazeFiles,
	FlowGenerateMazeFilesConfig,
)
from test_group_structure_and_lifecycle.test_setup_and_teardown.flows.flow_solve_maze import (
	FlowSolveMaze,
	FlowSolveMazeConfig,
)
from test_group_structure_and_lifecycle.test_setup_and_teardown.flows.flow_delete_maze_files import (
	FlowDeleteMazeFiles,
	FlowDeleteMazeFilesConfig,
)


class TestSetupAndTeardownConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Setup and Teardown")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates the optional _setup() and _teardown() hooks.\n"
			"_setup() runs once before any case and generates one maze file per value "
			"of the 'maze_index' matrix dimension.\n"
			"Each case then loads and solves one of those files, chosen by its "
			"'maze_index'.\n"
			"_teardown() runs once after every case and deletes the generated files."
		)
	)

	maze_executable_folder = OrcraftConfigField.PackageFolder(
		default="",
		label="Maze Executable Folder",
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
	)

	maze_count = OrcraftConfigField.Numeric(label="Maze Count", default=4)

	matrix = OrcraftConfigField.Matrix(
		OrcraftConfigField.Dimension("maze_index", tuple(range(1, 5))),
	)

	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class TestSetupAndTeardownResult(OrcraftTestResult):
	maze_file_path = OrcraftResultField.Text(default="", label="Maze File Path")
	path_found = OrcraftResultField.Boolean(default=False, label="Path Found")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class TestSetupAndTeardown(OrcraftTest):
	def __init__(self, config: TestSetupAndTeardownConfig | None = None) -> None:
		super().__init__(config or TestSetupAndTeardownConfig())

	def _workspace_folder(self) -> str:
		"""Per-test-run maze folder so concurrent tests never share generated files."""
		return resolve_workspace_folder(scope=f"{self.config.name}-{os.getpid()}")

	def _setup(self) -> None:
		workspace_folder = self._workspace_folder()
		maze_count = int(self.config.maze_count)

		Logger.log(
			f"Setup: generating {maze_count} maze files in {workspace_folder}",
			color=Logger.Color.CYAN,
		)

		flow = FlowGenerateMazeFiles(
			FlowGenerateMazeFilesConfig(
				maze_executable_folder=self.config.maze_executable_folder,
				workspace_folder=workspace_folder,
				count=maze_count,
			)
		)

		# Raising from _setup aborts the test: no cases run and _teardown is skipped.
		if self.handle_errors(flow.run(), self.result):
			raise RuntimeError(
				self.result.error_description
				or self.result.failure_description
				or "Setup failed to generate the maze files."
			)

	def _run_case(self, case: OrcraftTestCase) -> OrcraftTestResult:
		case.result = TestSetupAndTeardownResult()

		flow = FlowSolveMaze(
			FlowSolveMazeConfig(
				maze_executable_folder=self.config.maze_executable_folder,
				workspace_folder=self._workspace_folder(),
				maze_index=case.params["maze_index"],
			)
		)
		flow_result = flow.run()

		if self.handle_errors(flow_result, case.result):
			return case.result

		case.result.maze_file_path = flow_result.maze_file_path
		case.result.path_found = flow_result.path_found
		case.result.path_length = flow_result.path_length

		return case.result

	def _teardown(self) -> None:
		workspace_folder = self._workspace_folder()

		Logger.log(
			f"Teardown: deleting maze files in {workspace_folder}",
			color=Logger.Color.CYAN,
		)

		# Teardown does not raise — cleanup problems should not mask case results.
		flow = FlowDeleteMazeFiles(
			FlowDeleteMazeFilesConfig(
				workspace_folder=workspace_folder,
			)
		)
		flow.run()


def main() -> None:
	test = TestSetupAndTeardown()
	test.run()


if __name__ == "__main__":
	main()

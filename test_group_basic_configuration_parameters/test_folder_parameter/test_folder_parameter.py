from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestFolderParameterConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Folder Parameter")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates a folder configuration parameter.\n"
			"Runs the maze app executable with no arguments to display its help page and logs the output."
		)
	)
	
	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True)


class TestFolderParameter(OrcraftTest):
	def __init__(self, config: TestFolderParameterConfig | None = None) -> None:
		super().__init__(config or TestFolderParameterConfig())

	def _run_case(self, case: OrcraftTestCase):

		maze_app = MazeApp(self.config.maze_executable_folder)

		maze_app.run()

		return case.result


def main() -> None:
	test = TestFolderParameter()
	test.run()


if __name__ == "__main__":
	main()

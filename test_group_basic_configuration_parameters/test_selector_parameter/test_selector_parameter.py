from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestSelectorParameterConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Selector Parameter")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates a selector configuration parameter.\n"
			"Presents the available maze app commands as options and runs the maze app with the selected one."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True)
	
	command = OrcraftConfigField.Select(
		default="generate",
		label="Command",
		options=("generate", "solve", "save"),
	)


class TestSelectorParameter(OrcraftTest):
	def __init__(self, config: TestSelectorParameterConfig | None = None) -> None:
		super().__init__(config or TestSelectorParameterConfig())

	def _run_case(self, case: OrcraftTestCase):

		maze_app = MazeApp(self.config.maze_executable_folder, self.config.command)

		maze_app.run()

		return case.result


def main() -> None:
	test = TestSelectorParameter()
	test.run()


if __name__ == "__main__":
	main()

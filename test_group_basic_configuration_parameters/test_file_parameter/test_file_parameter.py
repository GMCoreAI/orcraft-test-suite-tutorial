from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestFileParameterConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="File Parameter")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates a file configuration parameter.\n"
			"Uses a file path for save/load operations with the maze app."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True)

	command = OrcraftConfigField.Select(
		default="solve",
		label="Command",
		options=("solve", "save", "load"),
	)
	
	maze_file = OrcraftConfigField.File(default="", label="Maze Save/Load File", required=True)


class TestFileParameter(OrcraftTest):
	def __init__(self, config: TestFileParameterConfig | None = None) -> None:
		super().__init__(config or TestFileParameterConfig())

	def _run_case(self, case: OrcraftTestCase):

		maze_app = MazeApp(self.config.maze_executable_folder, self.config.command, maze_file=self.config.maze_file)

		maze_app.run()

		return case.result


def main() -> None:
	test = TestFileParameter()
	test.run()


if __name__ == "__main__":
	main()

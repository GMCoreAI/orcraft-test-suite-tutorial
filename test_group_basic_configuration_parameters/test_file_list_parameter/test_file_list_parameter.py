from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestFileListParameterConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="File List Parameter")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates a file list configuration parameter.\n"
			"Uses a list of file paths for save/load operations with the maze app, running once per file."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True)

	command = OrcraftConfigField.Select(
		default="solve",
		label="Command",
		options=("solve", "save", "load"),
	)
	
	maze_files = OrcraftConfigField.FileList(default=(), label="Maze Save/Load Files", required=True)


class TestFileListParameter(OrcraftTest):
	def __init__(self, config: TestFileListParameterConfig | None = None) -> None:
		super().__init__(config or TestFileListParameterConfig())

	def _run_case(self, case: OrcraftTestCase):

		for maze_file in self.config.maze_files:

			maze_app = MazeApp(self.config.maze_executable_folder, self.config.command, maze_file=maze_file)

			maze_app.run()

		return case.result


def main() -> None:
	test = TestFileListParameter()
	test.run()


if __name__ == "__main__":
	main()

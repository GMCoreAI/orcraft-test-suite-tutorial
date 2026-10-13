from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestFolderListParameterConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Folder List Parameter")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates a folder list configuration parameter.\n"
			"Presents the available maze app commands as options and runs the maze app once per selected folder."
		)
	)

	maze_executable_folders = OrcraftConfigField.FolderList(default=(), label="Maze Executable Folders", required=True)
	
	command = OrcraftConfigField.Select(
		default="generate",
		label="Command",
		options=("generate", "solve", "save"),
	)


class TestFolderListParameter(OrcraftTest):
	def __init__(self, config: TestFolderListParameterConfig | None = None) -> None:
		super().__init__(config or TestFolderListParameterConfig())

	def _run_case(self, case: OrcraftTestCase):

		for folder in self.config.maze_executable_folders:

			maze_app = MazeApp(folder, self.config.command)

			maze_app.run()

		return case.result


def main() -> None:
	test = TestFolderListParameter()
	test.run()


if __name__ == "__main__":
	main()

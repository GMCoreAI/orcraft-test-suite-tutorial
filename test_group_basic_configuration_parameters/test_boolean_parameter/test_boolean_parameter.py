from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestBooleanParameterConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Boolean Parameter")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates a boolean configuration parameter.\n"
			"Runs the maze app executable with or without the --help switch based on the toggle."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True)
	
	use_help_switch = OrcraftConfigField.Boolean(default=False, label="Use --help Switch")


class TestBooleanParameter(OrcraftTest):
	def __init__(self, config: TestBooleanParameterConfig | None = None) -> None:
		super().__init__(config or TestBooleanParameterConfig())

	def _run_case(self, case: OrcraftTestCase):

		maze_app = MazeApp(self.config.maze_executable_folder, "--help" if self.config.use_help_switch else "")

		maze_app.run()

		return case.result


def main() -> None:
	test = TestBooleanParameter()
	test.run()


if __name__ == "__main__":
	main()

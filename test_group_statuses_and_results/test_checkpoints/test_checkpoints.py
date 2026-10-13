from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestCheckpointsConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Checkpoints")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates checkpoint usage.\n"
			"Each case passes through multiple checkpoints that individually validate distinct aspects of the app's output: "
			"the version banner, the path-found message with step count and arrow count, and the error message for invalid inputs. "
			"Runs the maze app across a matrix of commands and coordinates that includes invalid inputs "
			"('slove' command, out-of-bounds start_row and start_col). "
			"Cases with negative coordinates fail because argparse misinterprets them as flags, "
			"producing a different error than expected — illustrating how a single failing checkpoint marks the whole case as Fail."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(
		default="",
		label="Maze Executable Folder",
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
	)

	matrix = OrcraftConfigField.Matrix(
		OrcraftConfigField.Dimension("command", ("solve", "slove")),
		OrcraftConfigField.Dimension("width", (5,)),
		OrcraftConfigField.Dimension("height", (10, 15)),
		OrcraftConfigField.Dimension("start_row", (0, -1)),
		OrcraftConfigField.Dimension("start_col", (0, -2)),
	)


class TestCheckpoints(OrcraftTest):
	def __init__(self, config: TestCheckpointsConfig | None = None) -> None:
		super().__init__(config or TestCheckpointsConfig())

	def _run_case(self, case: OrcraftTestCase):

		maze_app = MazeApp(
			self.config.maze_executable_folder,
			case.params["command"],
			width=case.params["width"],
			height=case.params["height"],
			start_row=case.params["start_row"],
			start_col=case.params["start_col"],
		)

		maze_app.test(case)

		return case.result


def main() -> None:
	test = TestCheckpoints()
	test.run()


if __name__ == "__main__":
	main()

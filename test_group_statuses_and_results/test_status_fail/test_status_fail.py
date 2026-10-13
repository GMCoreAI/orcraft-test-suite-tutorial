from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
	OrcraftStatus,
)

from common.maze_app import MazeApp


class TestStatusFailConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Status: Fail")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates FAIL status.\n"
			"Runs the maze app across a matrix of commands and coordinates that includes invalid inputs "
			"('slove' command, out-of-bounds start_row and start_col). "
			"Any run that produces stderr output is intentionally marked as Fail — purely to demonstrate "
			"how FAIL status is set. This does not imply the app is misbehaving; "
			"the app is expected to write error messages for invalid inputs."
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


class TestStatusFail(OrcraftTest):
	def __init__(self, config: TestStatusFailConfig | None = None) -> None:
		super().__init__(config or TestStatusFailConfig())

	def _run_case(self, case: OrcraftTestCase):

		maze_app = MazeApp(
			self.config.maze_executable_folder,
			case.params["command"],
			width=case.params["width"],
			height=case.params["height"],
			start_row=case.params["start_row"],
			start_col=case.params["start_col"],
		)

		result = maze_app.run()

		if result.error:
			case.result.failure_description = result.error

		return case.result


def main() -> None:
	test = TestStatusFail()
	test.run()


if __name__ == "__main__":
	main()

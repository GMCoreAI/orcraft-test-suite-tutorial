from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestStatusErrorConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Status: Error")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates ERROR status.\n"
			"Runs the maze app across a matrix of versions and commands. "
			"Version v4.0.0 does not exist, so the maze app executable cannot be found — "
			"causing an unhandled exception that reports Error status."
		)
	)

	maze_bin_folder = OrcraftConfigField.Folder(
		default="",
		label="Maze Bin Folder",
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
	)
	
	matrix = OrcraftConfigField.Matrix(
		OrcraftConfigField.Dimension("maze_version", ("v3.0.0", "v4.0.0")),
		OrcraftConfigField.Dimension("command", ("solve",)),
		OrcraftConfigField.Dimension("width", (5,)),
		OrcraftConfigField.Dimension("height", (10, 15)),
	)


class TestStatusError(OrcraftTest):
	def __init__(self, config: TestStatusErrorConfig | None = None) -> None:
		super().__init__(config or TestStatusErrorConfig())

	def _run_case(self, case: OrcraftTestCase):

		bin_folder = f"{self.config.maze_bin_folder.rstrip('/\\')}/{case.params['maze_version']}"
		
		maze_app = MazeApp(
			bin_folder,
			case.params["command"],
			width=case.params["width"],
			height=case.params["height"],
		)

		maze_app.run()

		return case.result


def main() -> None:
	test = TestStatusError()
	test.run()


if __name__ == "__main__":
	main()

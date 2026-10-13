from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestMatrixAndCasesConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Matrix and Cases")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates matrix-driven case generation.\n"
			"Runs the maze app across all combinations of algorithm, seed, height, and width."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True, layout=OrcraftConfigField.Layout.NewRow)
	
	matrix = OrcraftConfigField.Matrix(
		OrcraftConfigField.Dimension("algorithm", ("BFS", "DFS", "ASTAR")),
		OrcraftConfigField.Dimension("seed", (42, 100)),
		OrcraftConfigField.Dimension("height", (5, 10)),
		OrcraftConfigField.Dimension("width", (15, 20)),
	)


class TestMatrixAndCases(OrcraftTest):
	def __init__(self, config: TestMatrixAndCasesConfig | None = None) -> None:
		super().__init__(config or TestMatrixAndCasesConfig())

	def _run_case(self, case: OrcraftTestCase):

		maze_app = MazeApp(
			self.config.maze_executable_folder,
			"solve",
			width=case.params["width"],
			height=case.params["height"],
			seed=case.params["seed"],
			start_row=0,
			start_col=0,
			end_row=case.params["height"] - 1,
			end_col=case.params["width"] - 1,
			algorithm=case.params["algorithm"],
		)

		maze_app.run()

		return case.result


def main() -> None:
	test = TestMatrixAndCases()
	test.run()


if __name__ == "__main__":
	main()

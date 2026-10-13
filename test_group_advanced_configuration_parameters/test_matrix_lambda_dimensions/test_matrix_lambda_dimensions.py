from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.github_repo_access import fetch_maze_app_release_versions, get_maze_app_bin_folder
from common.maze_app import MazeApp


class TestMatrixLambdaDimensionsConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Matrix Lambda Dimensions")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates lambda-generated dimension values in a matrix test.\n"
			"Fetches the latest maze app release versions from GitHub and runs them across multiple commands."
		)
	)

	matrix = OrcraftConfigField.Matrix(
		OrcraftConfigField.Dimension.lambda_choice(label="Maze App Version", factory=lambda: fetch_maze_app_release_versions()),
		OrcraftConfigField.Dimension(label="command", values=("generate", "solve", "save")),
		OrcraftConfigField.Dimension(label="algorithm", values=(None, "BFS", "DFS", "ASTAR")),

		exclude=[
			lambda case: case.params["command"] in ("generate", "save") and case.params["algorithm"] is not None,
		],
	)


class TestMatrixLambdaDimensions(OrcraftTest):
	def __init__(self, config: TestMatrixLambdaDimensionsConfig | None = None) -> None:
		super().__init__(config or TestMatrixLambdaDimensionsConfig())

	def _run_case(self, case: OrcraftTestCase):

		bin_folder = get_maze_app_bin_folder(case.params["Maze App Version"])
		
		maze_app = MazeApp(bin_folder, case.params["command"], algorithm=case.params["algorithm"])

		maze_app.run()

		return case.result


def main() -> None:
	test = TestMatrixLambdaDimensions()
	test.run()


if __name__ == "__main__":
	main()

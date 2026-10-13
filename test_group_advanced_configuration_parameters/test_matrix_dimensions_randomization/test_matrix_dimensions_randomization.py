from __future__ import annotations

import string

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestMatrixDimensionsRandomizationConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Matrix Dimensions Randomization")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates random dimension values in a matrix test.\n"
			"Runs the maze app with a randomly selected seed, random height, random width ratio (calculated from height), and a random illegal argument (appended as postfix to command) across multiple commands.\n"
			"Excludes only reference static dimensions, so the planned case count stays the same between runs."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True, layout=OrcraftConfigField.Layout.NewRow)

	matrix = OrcraftConfigField.Matrix(
		OrcraftConfigField.Dimension(label="command", values=("generate", "solve")),
		OrcraftConfigField.Dimension(label="algorithm", values=(None, "BFS")),
		OrcraftConfigField.Dimension.random_choice(label="seed", values=(1, 7, 42, 100, 2024), size=2),
		OrcraftConfigField.Dimension.random(label="height", min_value=5, max_value=15, size=2),
		OrcraftConfigField.Dimension.random(label="width_ratio", min_value=1.5, max_value=2.0, size=2),
		OrcraftConfigField.Dimension.random_string(label="illegal_arg", min_length=1, max_length=2, size=2, charset=" MG"),
		
		random_order=True,
		
		exclude=[
			lambda case: case.params["command"] == "generate" and case.params["algorithm"] is not None,
		],
	)


class TestMatrixDimensionsRandomization(OrcraftTest):
	def __init__(self, config: TestMatrixDimensionsRandomizationConfig | None = None) -> None:
		super().__init__(config or TestMatrixDimensionsRandomizationConfig())

	def _run_case(self, case: OrcraftTestCase):

		maze_app = MazeApp(
			self.config.maze_executable_folder,
			(case.params["command"] + case.params["illegal_arg"]).strip(),
			width=round(case.params["height"] * case.params["width_ratio"]),
			height=case.params["height"],
			seed=case.params["seed"],
			algorithm=case.params["algorithm"],
		)

		maze_app.run()

		return case.result


def main() -> None:
	test = TestMatrixDimensionsRandomization()
	test.run()


if __name__ == "__main__":
	main()

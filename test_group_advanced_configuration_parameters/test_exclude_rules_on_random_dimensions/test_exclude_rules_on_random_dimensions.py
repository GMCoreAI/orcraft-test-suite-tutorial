from __future__ import annotations

import string

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestExcludeRulesOnRandomDimensionsConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Exclude Rules on Random Dimensions")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates exclude rules that act on randomized matrix dimensions.\n"
			"Because excludes can drop a variable number of randomly sampled cases, the planned case count may legitimately differ between runs."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True, layout=OrcraftConfigField.Layout.NewRow)
	maze_file = OrcraftConfigField.File(default="", label="Maze Save/Load File", layout=OrcraftConfigField.Layout.UnderPrevious)

	matrix = OrcraftConfigField.Matrix(
		OrcraftConfigField.Dimension(label="command", values=("generate", "solve", "save")),
		OrcraftConfigField.Dimension.random_choice(label="algorithm", values=(None, "BFS", "DFS", "astar"), size=2),
		OrcraftConfigField.Dimension.random(label="height", min_value=5, max_value=15, size=2),
		OrcraftConfigField.Dimension.random(label="width_ratio", min_value=1.5, max_value=2.0, size=2),
		OrcraftConfigField.Dimension(label="use_file", values=(False, True)),
		OrcraftConfigField.Dimension.random_string(label="illegal_arg", min_length=1, max_length=2, size=3, charset=" MG"),
		
		random_order=True,
		
		exclude=[
			lambda case: case.params["command"] in ("generate", "save") and case.params["algorithm"] is not None,
			{"command": "generate", "use_file": True},
			lambda case: case.params["command"] == "solve" and case.params["use_file"],
		],
	)


class TestExcludeRulesOnRandomDimensions(OrcraftTest):
	def __init__(self, config: TestExcludeRulesOnRandomDimensionsConfig | None = None) -> None:
		super().__init__(config or TestExcludeRulesOnRandomDimensionsConfig())

	def _run_case(self, case: OrcraftTestCase):

		maze_app = MazeApp(
			self.config.maze_executable_folder,
			(case.params["command"] + case.params["illegal_arg"]).strip(),
			width=round(case.params["height"] * case.params["width_ratio"]),
			height=case.params["height"],
			algorithm=case.params["algorithm"],
			maze_file=self.config.maze_file if case.params["use_file"] else None,
		)

		maze_app.run()

		return case.result


def main() -> None:
	test = TestExcludeRulesOnRandomDimensions()
	test.run()


if __name__ == "__main__":
	main()

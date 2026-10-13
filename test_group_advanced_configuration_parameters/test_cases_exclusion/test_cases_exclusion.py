from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestCasesExclusionConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Cases Exclusion")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates matrix case exclusion using dict rules and lambdas.\n"
			"Excludes invalid maze command and parameter combinations from the generated case set."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True, layout=OrcraftConfigField.Layout.NewRow)
	maze_file = OrcraftConfigField.File(default="", label="Maze Save/Load File", layout=OrcraftConfigField.Layout.UnderPrevious)

	matrix = OrcraftConfigField.Matrix(
		OrcraftConfigField.Dimension("command", ("generate", "solve", "save", "load")),
		OrcraftConfigField.Dimension("algorithm", (None, "BFS", "DFS", "ASTAR")),
		OrcraftConfigField.Dimension("seed", (None, 42)),
		OrcraftConfigField.Dimension("height", (None, 5)),
		OrcraftConfigField.Dimension("width", (None, 10)),
		OrcraftConfigField.Dimension("use_file", (False, True)),
		
		exclude=[
			{"command": "generate", "algorithm": "BFS"},
			{"command": "generate", "algorithm": "DFS"},
			{"command": "generate", "algorithm": "ASTAR"},
			{"command": "generate", "use_file": True},
			{"command": "load", "use_file": False},
			lambda case: case.params["command"] in ("save", "load") and case.params["algorithm"] is not None,
			lambda case: case.params["command"] == "load" and any(case.params[p] is not None for p in ("seed", "height", "width")),
			lambda case: case.params["command"] == "solve" and case.params["use_file"] and any(case.params[p] is not None for p in ("seed", "height", "width")),
		],
	)


class TestCasesExclusion(OrcraftTest):
	def __init__(self, config: TestCasesExclusionConfig | None = None) -> None:
		super().__init__(config or TestCasesExclusionConfig())

	def _run_case(self, case: OrcraftTestCase):

		maze_app = MazeApp(
			self.config.maze_executable_folder,
			case.params["command"],
			width=case.params["width"],
			height=case.params["height"],
			seed=case.params["seed"],
			algorithm=case.params["algorithm"],
			maze_file=self.config.maze_file if case.params["use_file"] else None,
		)

		maze_app.run()

		return case.result


def main() -> None:
	test = TestCasesExclusion()
	test.run()


if __name__ == "__main__":
	main()

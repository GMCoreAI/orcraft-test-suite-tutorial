from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestResult,
	OrcraftTestCase,
	OrcraftConfigField,
	OrcraftResultField,
)

from common.maze_app import MazeApp


class TestResultFieldsConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Result Fields")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates custom result fields.\n"
			"Runs the maze app across a matrix of valid solve configurations and exposes meaningful "
			"values produced by each run as result fields: maze area (width × height), solution path length, "
			"and their ratio. Cases where the area/path ratio falls below 1.8 — indicating a long path "
			"relative to the maze size — are flagged with a warning."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(
		default="",
		label="Maze Executable Folder",
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
	)

	matrix = OrcraftConfigField.Matrix(
		OrcraftConfigField.Dimension("width", (5, 10)),
		OrcraftConfigField.Dimension("height", (15, 20)),
		OrcraftConfigField.Dimension("seed", (13, 17, 42)),
	)


class TestResultFieldsResult(OrcraftTestResult):
	maze_area = OrcraftResultField.Numeric(default=None, label="Maze Area")
	path_length = OrcraftResultField.Numeric(default=None, label="Path Length")
	area_path_ratio = OrcraftResultField.Numeric(default=None, label="Area / Path Ratio")


class TestResultFields(OrcraftTest):
	def __init__(self, config: TestResultFieldsConfig | None = None) -> None:
		super().__init__(config or TestResultFieldsConfig())

	def _run_case(self, case: OrcraftTestCase) -> TestResultFieldsResult:
		case.result = TestResultFieldsResult()

		maze_app = MazeApp(
			self.config.maze_executable_folder,
			"solve",
			width=case.params["width"],
			height=case.params["height"],
			seed=case.params["seed"],
		)

		maze_app.run_and_validate(case)

		return case.result


def main() -> None:
	test = TestResultFields()
	test.run()


if __name__ == "__main__":
	main()

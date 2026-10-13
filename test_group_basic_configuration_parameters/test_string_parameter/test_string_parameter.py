from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestStringParameterConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="String Parameter")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates a string configuration parameter.\n"
			"Optionally passes a raw command-line string to the maze app."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True, layout=OrcraftConfigField.Layout.NewRow)
	maze_file = OrcraftConfigField.File(default="", label="Maze Save/Load File", layout=OrcraftConfigField.Layout.UnderPrevious)

	use_command_line = OrcraftConfigField.Boolean(default=True, label="Use String Command Line", layout=OrcraftConfigField.Layout.NewRow)

	command_line = OrcraftConfigField.Text(default="solve --width 20 --height 10 --seed 42 --start 0,0 --end 9,19", label="Command Line", width=520)

	command = OrcraftConfigField.Select(
		default="solve",
		label="Command",
		options=("generate", "solve", "save", "load"),
		layout=OrcraftConfigField.Layout.NewRow,
	)

	solve_switches = OrcraftConfigField.MultiSelect(
		default=("--algorithm", "--file"),
		label="Solve Switches",
		options=("--algorithm", "--file"),
	)

	algorithms = OrcraftConfigField.MultiSelect(
		default=("BFS",),
		label="Algorithms",
		options=("BFS", "DFS", "ASTAR"),
	)

	generation_switches = OrcraftConfigField.MultiSelect(
		default=("--width", "--height", "--seed", "--start", "--end"),
		label="Generation Switches",
		options=("--width", "--height", "--seed", "--start", "--end"),
		layout=OrcraftConfigField.Layout.NewRow,
	)

	height = OrcraftConfigField.Numeric(default=10, label="Height")
	start_row = OrcraftConfigField.Numeric(default=0, label="Start Row", layout=OrcraftConfigField.Layout.UnderPrevious)
	end_row = OrcraftConfigField.Numeric(default=9, label="End Row", layout=OrcraftConfigField.Layout.UnderPrevious)

	width = OrcraftConfigField.Numeric(default=20, label="Width")
	start_col = OrcraftConfigField.Numeric(default=0, label="Start Col", layout=OrcraftConfigField.Layout.UnderPrevious)
	end_col = OrcraftConfigField.Numeric(default=19, label="End Col", layout=OrcraftConfigField.Layout.UnderPrevious)
	
	seed = OrcraftConfigField.Numeric(default=42, label="Seed")


class TestStringParameter(OrcraftTest):
	def __init__(self, config: TestStringParameterConfig | None = None) -> None:
		super().__init__(config or TestStringParameterConfig())

	def _run_case(self, case: OrcraftTestCase):

		if self.config.use_command_line:

			maze_app = MazeApp(self.config.maze_executable_folder, raw_args=self.config.command_line)

			maze_app.run()

			return case.result

		for algorithm in self.config.algorithms:

			maze_app = MazeApp(
				self.config.maze_executable_folder,
				self.config.command,
				width=self.config.width,
				height=self.config.height,
				seed=self.config.seed,
				start_row=self.config.start_row,
				start_col=self.config.start_col,
				end_row=self.config.end_row,
				end_col=self.config.end_col,
				algorithm=algorithm,
				maze_file=self.config.maze_file,
			)

			maze_app.run()

		return case.result


def main() -> None:
	test = TestStringParameter()
	test.run()


if __name__ == "__main__":
	main()

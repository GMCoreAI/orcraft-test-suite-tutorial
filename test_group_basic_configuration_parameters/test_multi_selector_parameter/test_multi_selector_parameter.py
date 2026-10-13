from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestMultiSelectorParameterConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Multi-Selector Parameter")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates a multi-selector configuration parameter.\n"
			"Selects one or more solving algorithms and runs the maze app once per selection."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True, layout=OrcraftConfigField.Layout.NewRow)

	maze_file = OrcraftConfigField.File(default="", label="Maze Save/Load File", layout=OrcraftConfigField.Layout.UnderPrevious)

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


class TestMultiSelectorParameter(OrcraftTest):
	def __init__(self, config: TestMultiSelectorParameterConfig | None = None) -> None:
		super().__init__(config or TestMultiSelectorParameterConfig())

	def _run_case(self, case: OrcraftTestCase):

		gen_sw = set(self.config.generation_switches)
		solve_sw = set(self.config.solve_switches)

		for algorithm in self.config.algorithms:

			maze_app = MazeApp(
				self.config.maze_executable_folder,
				self.config.command,
				width=self.config.width if "--width" in gen_sw else None,
				height=self.config.height if "--height" in gen_sw else None,
				seed=self.config.seed if "--seed" in gen_sw else None,
				start_row=self.config.start_row if "--start" in gen_sw else None,
				start_col=self.config.start_col if "--start" in gen_sw else None,
				end_row=self.config.end_row if "--end" in gen_sw else None,
				end_col=self.config.end_col if "--end" in gen_sw else None,
				algorithm=algorithm if "--algorithm" in solve_sw else None,
				maze_file=self.config.maze_file if "--file" in solve_sw else None,
			)

			maze_app.run()

		return case.result


def main() -> None:
	test = TestMultiSelectorParameter()
	test.run()


if __name__ == "__main__":
	main()

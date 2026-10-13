from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.maze_app import MazeApp


class TestNumericParameterConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Numeric Parameter")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates numeric configuration parameters.\n"
			"Configures maze dimensions, seed, start/end coordinates, and runs the maze app."
		)
	)

	maze_executable_folder = OrcraftConfigField.Folder(default="", label="Maze Executable Folder", required=True)

	command = OrcraftConfigField.Select(
		default="generate",
		label="Command",
		options=("generate", "solve", "save"),
	)

	width = OrcraftConfigField.Numeric(default=20, label="Width", layout=OrcraftConfigField.Layout.NewRow)
	height = OrcraftConfigField.Numeric(default=10, label="Height")

	seed = OrcraftConfigField.Numeric(default=42, label="Seed")

	start_row = OrcraftConfigField.Numeric(default=0, label="Start Row", layout=OrcraftConfigField.Layout.NewRow)
	start_col = OrcraftConfigField.Numeric(default=0, label="Start Col")
	
	end_row = OrcraftConfigField.Numeric(default=9, label="End Row", layout=OrcraftConfigField.Layout.NewRow)
	end_col = OrcraftConfigField.Numeric(default=19, label="End Col")


class TestNumericParameter(OrcraftTest):
	def __init__(self, config: TestNumericParameterConfig | None = None) -> None:
		super().__init__(config or TestNumericParameterConfig())

	def _run_case(self, case: OrcraftTestCase):

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
		)

		maze_app.run()

		return case.result


def main() -> None:
	test = TestNumericParameter()
	test.run()


if __name__ == "__main__":
	main()

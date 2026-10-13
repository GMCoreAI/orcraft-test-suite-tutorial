from __future__ import annotations

from common.maze_app import MazeApp
from common.maze_file_utils import normalize_long_path

from orcraft import (
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftConfigField,
	OrcraftLogger as Logger,
)


class StepProduceMazeTypedDataConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Produce Maze Typed Data")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")


class StepProduceMazeTypedDataResult(OrcraftTestStepResult):
	pass


class StepProduceMazeTypedData(OrcraftTestStep):
	def __init__(self, config: StepProduceMazeTypedDataConfig | None = None) -> None:
		super().__init__(config or StepProduceMazeTypedDataConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepProduceMazeTypedDataResult()

		exe_folder = normalize_long_path(self.config.maze_executable_folder)
		width = int(self.config.width)
		height = int(self.config.height)

		result = MazeApp(exe_folder, "solve", width=width, height=height).run()

		# Determine solve status from the run result
		status = result.status
		maze_area = width * height

		# Assemble typed data that exercises RPC type preservation:
		# - tuple (would flatten to list without proper serialization)
		# - enum (would flatten to string value without proper serialization)
		# - nested dict with mixed types
		self.result.dimensions = (width, height)
		self.result.solve_status = status
		self.result.start_coords = (0, 0)
		self.result.metadata = {
			"bounds": (0, 0, width - 1, height - 1),
			"tags": ("maze", "tutorial", "generated"),
			"status": status,
			"nested": {
				"area": maze_area,
				"pair": (True, False),
			},
		}

		Logger.log(f"dimensions   = {self.result.dimensions!r}", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"solve_status = {self.result.solve_status!r}", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"start_coords = {self.result.start_coords!r}", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"metadata     = {self.result.metadata!r}", color=Logger.Color.BLUE, module_tag=False)

		return self.result

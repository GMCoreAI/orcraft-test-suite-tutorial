from __future__ import annotations

import threading

from common.maze_app import MazeApp
from common.maze_file_utils import normalize_long_path


from orcraft import (
	OrcraftStatus,
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftConfigField,
	OrcraftLogger as Logger,
)



class StepStartMazeThreadConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Start Maze Thread")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	width = OrcraftConfigField.Numeric(default=5, label="Width")
	height = OrcraftConfigField.Numeric(default=8, label="Height")


class StepStartMazeThreadResult(OrcraftTestStepResult):
	pass


class StepStartMazeThread(OrcraftTestStep):
	def __init__(self, config: StepStartMazeThreadConfig | None = None) -> None:
		super().__init__(config or StepStartMazeThreadConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepStartMazeThreadResult()

		exe_folder = normalize_long_path(self.config.maze_executable_folder)
		width = int(self.config.width)
		height = int(self.config.height)

		task = {
			"count": 0,
			"results": [],
			"lock": threading.Lock(),
			"stop_event": threading.Event(),
		}

		def _worker() -> None:
			while not task["stop_event"].is_set():
				try:
					result = MazeApp(exe_folder, "solve", width=width, height=height).run_silent()
					if result.solved:
						with task["lock"]:
							task["count"] += 1
							task["results"].append(result)
				except Exception:
					pass

		thread = threading.Thread(target=_worker, daemon=True)
		task["thread"] = thread
		thread.start()

		Logger.log(
			f"Started background maze-generation thread (width={width}, height={height})",
			module_tag=False,
		)

		self.result.task = task
		self.result.status = OrcraftStatus.PASS
		return self.result

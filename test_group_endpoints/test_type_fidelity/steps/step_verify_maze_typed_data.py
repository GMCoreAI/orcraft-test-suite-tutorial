from __future__ import annotations

from common.maze_app import MazeSolveStatus

from orcraft import (
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftConfigField,
	OrcraftLogger as Logger,
)


class StepVerifyMazeTypedDataConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Verify Maze Typed Data")
	dimensions = None
	solve_status = None
	start_coords = None
	metadata = None


class StepVerifyMazeTypedDataResult(OrcraftTestStepResult):
	pass


class StepVerifyMazeTypedData(OrcraftTestStep):
	def __init__(self, config: StepVerifyMazeTypedDataConfig | None = None) -> None:
		super().__init__(config or StepVerifyMazeTypedDataConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepVerifyMazeTypedDataResult()

		dimensions = self.config.dimensions
		solve_status = self.config.solve_status
		start_coords = self.config.start_coords
		metadata = self.config.metadata

		bounds = metadata.get("bounds") if isinstance(metadata, dict) else None
		tags = metadata.get("tags") if isinstance(metadata, dict) else None
		meta_status = metadata.get("status") if isinstance(metadata, dict) else None
		nested = metadata.get("nested") if isinstance(metadata, dict) else None
		pair = nested.get("pair") if isinstance(nested, dict) else None
		area = nested.get("area") if isinstance(nested, dict) else None

		Logger.log(f"'dimensions'        : {dimensions!r}  (type: {type(dimensions).__name__})", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"'solve_status'      : {solve_status!r}  (type: {type(solve_status).__name__})", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"'start_coords'      : {start_coords!r}  (type: {type(start_coords).__name__})", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"'metadata'          : {metadata!r}  (type: {type(metadata).__name__})", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"  'metadata.bounds'        : {bounds!r}  (type: {type(bounds).__name__})", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"  'metadata.tags'          : {tags!r}  (type: {type(tags).__name__})", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"  'metadata.status'        : {meta_status!r}  (type: {type(meta_status).__name__})", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"  'metadata.nested'        : {nested!r}  (type: {type(nested).__name__})", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"    'metadata.nested.pair' : {pair!r}  (type: {type(pair).__name__})", color=Logger.Color.BLUE, module_tag=False)
		Logger.log(f"    'metadata.nested.area' : {area!r}  (type: {type(area).__name__})", color=Logger.Color.BLUE, module_tag=False)

		self.checkpoint(isinstance(dimensions, tuple), "'dimensions' is tuple", f"'dimensions' type is {type(dimensions).__name__}")
		self.checkpoint(isinstance(dimensions, tuple) and len(dimensions) == 2, "'dimensions' has length 2", "'dimensions' length is not 2")
		self.checkpoint(isinstance(solve_status, MazeSolveStatus), "'solve_status' is MazeSolveStatus enum", f"'solve_status' type is {type(solve_status).__name__}")
		self.checkpoint(isinstance(solve_status, MazeSolveStatus) and solve_status in list(MazeSolveStatus), "'solve_status' has valid value", "'solve_status' value is not valid")
		self.checkpoint(isinstance(start_coords, tuple), "'start_coords' is tuple", f"'start_coords' type is {type(start_coords).__name__}")
		self.checkpoint(isinstance(start_coords, tuple) and len(start_coords) == 2, "'start_coords' has length 2", "'start_coords' length is not 2")
		self.checkpoint(isinstance(metadata, dict), "'metadata' is dict", f"'metadata' type is {type(metadata).__name__}")
		self.checkpoint(isinstance(bounds, tuple), "'metadata.bounds' is tuple", f"'metadata.bounds' type is {type(bounds).__name__}")
		self.checkpoint(isinstance(tags, tuple), "'metadata.tags' is tuple", f"'metadata.tags' type is {type(tags).__name__}")
		self.checkpoint(isinstance(meta_status, MazeSolveStatus), "'metadata.status' is MazeSolveStatus enum", f"'metadata.status' type is {type(meta_status).__name__}")
		self.checkpoint(isinstance(nested, dict), "'metadata.nested' is dict", f"'metadata.nested' type is {type(nested).__name__}")
		self.checkpoint(isinstance(pair, tuple), "'metadata.nested.pair' is tuple", f"'metadata.nested.pair' type is {type(pair).__name__}")
		self.checkpoint(isinstance(area, int), "'metadata.nested.area' is int", f"'metadata.nested.area' type is {type(area).__name__}")

		return self.result

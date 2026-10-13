from __future__ import annotations

from orcraft import (
	OrcraftTestFlow,
	OrcraftTestFlowConfig,
	OrcraftTestFlowResult,
	OrcraftResultField,
	OrcraftConfigField,
)

from test_group_endpoints.test_package_upload_parameter_types.steps.step_solve_uploaded_file import StepSolveUploadedFile
from test_group_endpoints.test_package_upload_parameter_types.steps.step_solve_uploaded_file_list import StepSolveUploadedFileList
from test_group_endpoints.test_package_upload_parameter_types.steps.step_solve_uploaded_folder_list import StepSolveUploadedFolderList


class FlowSolveUploadedMazesConfig(OrcraftTestFlowConfig):
	name = OrcraftConfigField.Text(default="Solve Uploaded Mazes")
	maze_executable_folder = OrcraftConfigField.PackageFolder(default="", label="Maze Executable Folder")
	maze_file = OrcraftConfigField.PackageFile(default="", label="Maze File")
	maze_files = OrcraftConfigField.PackageFileList(default=(), label="Maze Files")
	maze_folders = OrcraftConfigField.PackageFolderList(default=(), label="Maze Folders")
	test_endpoint = OrcraftConfigField.Endpoint(default="localhost", label="Test Endpoint")
	endpoint_2 = OrcraftConfigField.Endpoint(default="localhost", label="Endpoint 2")
	endpoint_1 = OrcraftConfigField.EndpointFanout(default=("localhost",), label="Endpoint 1")
	log_orientation = OrcraftConfigField.Format(default=OrcraftConfigField.LogTableOrientation.VERTICAL)


class FlowSolveUploadedMazesResult(OrcraftTestFlowResult):
	mazes_solved = OrcraftResultField.Numeric(default=0, label="Mazes Solved")
	mazes_total = OrcraftResultField.Numeric(default=0, label="Mazes Total")
	log_orientation = OrcraftResultField.Format(default=OrcraftResultField.LogTableOrientation.VERTICAL)


class FlowSolveUploadedMazes(OrcraftTestFlow):
	result_type = FlowSolveUploadedMazesResult

	def __init__(self, config: FlowSolveUploadedMazesConfig) -> None:
		super().__init__(config)

	def _run_flow(self) -> None:
		# Step 1: a single maze uploaded via PackageFile, linked to the fanout endpoint(s).
		# Solve it on every fanout endpoint where it was uploaded.
		fanout_endpoints = list(self.config.endpoint_1)
		file_total = 0
		file_solved = 0
		for fanout_endpoint in fanout_endpoints:
			step_file_result = self.run_step(
				StepSolveUploadedFile,
				endpoint=fanout_endpoint,
				maze_executable_folder=self.config.maze_executable_folder,
				maze_file=self.config.maze_file,
			)

			if self.handle_errors(step_file_result, self.result):
				return

			file_total += 1
			if step_file_result.path_found:
				file_solved += 1

		# Step 2: several mazes uploaded via PackageFileList, linked to the secondary endpoint.
		step_file_list_result = self.run_step(
			StepSolveUploadedFileList,
			endpoint=self.config.endpoint_2,
			maze_executable_folder=self.config.maze_executable_folder,
			maze_files=self.config.maze_files,
		)

		if self.handle_errors(step_file_list_result, self.result):
			return

		# Step 3: each maze app version uploaded via PackageFolderList, linked to the primary endpoint.
		# Each uploaded folder is a self-contained maze app version, so the step
		# runs every version's own executable (ignoring any maze files inside).
		step_folder_list_result = self.run_step(
			StepSolveUploadedFolderList,
			endpoint=self.config.test_endpoint,
			maze_folders=self.config.maze_folders,
		)

		if self.handle_errors(step_folder_list_result, self.result):
			return

		mazes_total = file_total + step_file_list_result.mazes_total + step_folder_list_result.versions_total
		mazes_solved = (
			file_solved
			+ step_file_list_result.mazes_solved
			+ step_folder_list_result.versions_solved
		)

		self.result.mazes_total = mazes_total
		self.result.mazes_solved = mazes_solved

		self.checkpoint(
			mazes_total > 0 and mazes_solved == mazes_total,
			f"All {mazes_total} uploaded maze(s) solved.",
			f"Only {mazes_solved} of {mazes_total} uploaded maze(s) solved.",
		)

from __future__ import annotations

import enum
import os
import re as _re
import shlex
import subprocess
import sys
from dataclasses import dataclass

from orcraft import OrcraftLogger as Logger, OrcraftTestCase


class MazeSolveStatus(enum.Enum):
	SOLVED = "solved"
	UNSOLVABLE = "unsolvable"
	UNKNOWN = "unknown"


def _colorize_output(output: str, arrow_color: Logger.Color = Logger.Color.YELLOW) -> str:
	parts = _re.split(r"([→←↑↓]|(?<= )[SE](?= ))", output)
	result = []
	for part in parts:
		if not part:
			continue
		if _re.fullmatch(r"[→←↑↓]", part):
			result.append(Logger.colorize(part, arrow_color))
		elif _re.fullmatch(r"[SE]", part):
			result.append(Logger.colorize(part, Logger.Color.GREEN))
		else:
			result.append(Logger.colorize(part, Logger.Color.BLUE))
	return "".join(result)


@dataclass
class MazeResult:
	"""High-level outcome of a maze app run. Hides stdout/stderr parsing from callers."""

	stdout: str
	stderr: str

	@property
	def solved(self) -> bool:
		"""True when the maze app reported a solved path."""
		return bool(_re.search(r"Path found:", self.stdout))

	@property
	def steps(self) -> int:
		"""Number of steps in the solved path, or 0 if no path was found."""
		match = _re.search(r"Path found: (\d+) step", self.stdout)
		return int(match.group(1)) if match else 0

	@property
	def error(self) -> str:
		"""Error message produced by the maze app, or empty string."""
		return self.stderr

	@property
	def status(self) -> MazeSolveStatus:
		"""Solve status derived from the maze output."""
		if self.solved:
			return MazeSolveStatus.SOLVED
		if self.stdout:
			return MazeSolveStatus.UNSOLVABLE
		return MazeSolveStatus.UNKNOWN

	def colored(self) -> str:
		"""Render the maze output with ANSI colors for logging."""
		arrow_color = Logger.Color.YELLOW if self.solved else Logger.Color.RED
		return _colorize_output(self.stdout, arrow_color)


class MazeApp:
	def __init__(
		self,
		executable_folder: str,
		command: str = "",
		*,
		raw_args: str | None = None,
		width: int | None = None,
		height: int | None = None,
		seed: int | None = None,
		start_row: int | None = None,
		start_col: int | None = None,
		end_row: int | None = None,
		end_col: int | None = None,
		algorithm: str | None = None,
		maze_file: str | None = None,
	) -> None:
		self.executable_folder = executable_folder
		self.command = command
		self.raw_args = raw_args
		self.width = width
		self.height = height
		self.seed = seed
		self.start_row = start_row
		self.start_col = start_col
		self.end_row = end_row
		self.end_col = end_col
		self.algorithm = algorithm
		self.maze_file = maze_file

	@classmethod
	def from_release(cls, tag: str, command: str = "", *, force: bool = False, **kwargs) -> MazeApp:
		from common.github_repo_access import get_maze_app_bin_folder
		return cls(get_maze_app_bin_folder(tag, force=force), command, **kwargs)

	def get_version(self) -> str | None:
		name = os.path.basename(self._resolve_executable())
		stem = name.rsplit("-", 1)[0]  # "maze1.0.0-win" → "maze1.0.0"
		version = stem[len("maze"):]   # "maze1.0.0" → "1.0.0"
		return version.lstrip("v-") or None

	def run(self) -> MazeResult:
		"""Run the maze app, logging its output, and return the result."""
		return self._execute()

	def run_silent(self) -> MazeResult:
		"""Run the maze app without logging any output."""
		args = self._build_args()
		exe = self._resolve_executable()
		completed = subprocess.run(
			[exe] + args,
			cwd=self.executable_folder,
			capture_output=True,
			text=True,
			encoding="utf-8",
		)
		return MazeResult(completed.stdout.strip(), completed.stderr.strip())

	def run_and_validate(self, case: OrcraftTestCase) -> None:
		result = self._execute()
		maze_area = (self.width or 0) * (self.height or 0)
		case.result.maze_area = maze_area  # type: ignore[attr-defined]
		if result.solved:
			path_length = result.steps
			area_path_ratio = round(maze_area / path_length, 2)
			case.result.path_length = path_length  # type: ignore[attr-defined]
			case.result.area_path_ratio = area_path_ratio  # type: ignore[attr-defined]
			if area_path_ratio < 1.8:
				case.result.warning_description = (  # type: ignore[attr-defined]
					f"Area/path ratio is {area_path_ratio}, which is less than 1.8. "
					"The solution path is long relative to the maze area."
				)

	def test(self, case: OrcraftTestCase) -> None:
		result = self._execute()
		self._test_version_logging(result.stdout, case)
		self._test_path_found_message(result, case)
		self._test_error_messages(result.stderr, case)

	def _build_args(self) -> list[str]:
		if self.raw_args is not None:
			return shlex.split(self.raw_args)
		args = [self.command] if self.command else []
		accepts_generation_args = self.command != "load"
		if accepts_generation_args:
			if self.width is not None:
				args += ["--width", str(self.width)]
			if self.height is not None:
				args += ["--height", str(self.height)]
			if self.seed is not None:
				args += ["--seed", str(self.seed)]
			if self.start_row is not None and self.start_col is not None:
				args += ["--start", f"{self.start_row},{self.start_col}"]
			if self.end_row is not None and self.end_col is not None:
				args += ["--end", f"{self.end_row},{self.end_col}"]
		if self.maze_file:
			if self.command == "save":
				args += ["--output", self.maze_file]
			elif self.command in ("solve", "load"):
				args += ["--file", self.maze_file]
		if self.algorithm is not None and self.command == "solve":
			args += ["--algorithm", self.algorithm.lower()]
		return args

	def popen(self, **kwargs) -> subprocess.Popen:
		"""Launch the maze app as a non-blocking Popen object."""
		args = self._build_args()
		exe = self._resolve_executable()
		return subprocess.Popen(
			[exe] + args,
			cwd=self.executable_folder,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			text=True,
			encoding="utf-8",
			**kwargs,
		)

	def _execute(self) -> MazeResult:
		args = self._build_args()
		exe = self._resolve_executable()
		cmd_str = " ".join([os.path.basename(exe)] + args)
		Logger.log(f"Running from {self.executable_folder}:\n\t{cmd_str}\n", module_tag=False)
		completed = subprocess.run(
			[exe] + args,
			cwd=self.executable_folder,
			capture_output=True,
			text=True,
			encoding="utf-8",
		)
		result = MazeResult(completed.stdout.strip(), completed.stderr.strip())
		if completed.stdout:
			use_red = self.command == "solve" and not result.solved
			arrow_color = Logger.Color.RED if use_red else Logger.Color.YELLOW
			Logger.log(_colorize_output(completed.stdout, arrow_color), module_tag=False)
		if completed.stderr:
			Logger.log(completed.stderr, color=Logger.Color.RED, module_tag=False)
		if completed.returncode != 0:
			Logger.log(f"Maze app exited with code {completed.returncode}: {cmd_str}", color=Logger.Color.RED, module_tag=False)
		return result

	def _resolve_executable(self) -> str:
		import glob
		import stat
		if sys.platform == "win32":
			matches = glob.glob(os.path.join(self.executable_folder, "maze*-win*"))
			# Windows CreateProcess needs a real executable extension, so a bare
			# PE path (e.g. an older 'maze-v3.0.0-win' with no extension) raises
			# [WinError 2]. Prefer a '.exe' match; only fall back otherwise.
			exe_matches = [m for m in matches if m.lower().endswith(".exe")]
			if exe_matches:
				return exe_matches[0]
			if matches:
				return matches[0]
			return os.path.join(self.executable_folder, "maze-win.exe")
		elif sys.platform == "darwin":
			matches = glob.glob(os.path.join(self.executable_folder, "maze*-macos"))
			exe = matches[0] if matches else os.path.join(self.executable_folder, "maze-macos")
		else:
			matches = glob.glob(os.path.join(self.executable_folder, "maze*-linux"))
			exe = matches[0] if matches else os.path.join(self.executable_folder, "maze-linux")
		if os.path.exists(exe) and not os.access(exe, os.X_OK):
			os.chmod(exe, os.stat(exe).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
		return exe

	def _test_version_logging(self, stdout: str, case: OrcraftTestCase) -> None:
		exe_version = self.get_version()
		banner_match = _re.search(r"\(v([^)]+)\)", stdout)
		if exe_version is not None and banner_match:
			banner_version = banner_match.group(1).lstrip("v")
			case.checkpoint(
				banner_version == exe_version,
				f"Version banner is present and matches executable: {exe_version}.",
				f"Version banner mismatch: banner has {banner_version}, executable is {exe_version}.",
			)
		else:
			case.checkpoint(
				banner_match is not None,
				"Version banner is present.",
				"Version banner not found in app output.",
			)

	def _test_path_found_message(self, result: MazeResult, case: OrcraftTestCase) -> None:
		if self.command != "solve" or result.error:
			return
		case.checkpoint(
			result.solved,
			"Path found message is present.",
			"Path found message not found in app output.",
		)
		if not result.solved:
			return
		actual_steps = result.steps
		expected_steps: int | None = case.params.get("expected_steps")
		if expected_steps is not None:
			case.checkpoint(
				actual_steps == expected_steps,
				f"Step count is correct: {actual_steps}.",
				f"Step count mismatch: expected {expected_steps}, got {actual_steps}.",
			)
		arrow_count = sum(result.stdout.count(ch) for ch in "→←↑↓")
		path_count = arrow_count + 2  # +2 for S (start) and E (end)
		case.checkpoint(
			path_count == actual_steps,
			f"Arrow count matches step count: {actual_steps}.",
			f"Arrow count ({arrow_count}) + S/E (2) = {path_count}, does not match reported step count ({actual_steps}).",
		)

	def _test_error_messages(self, stderr: str, case: OrcraftTestCase) -> None:
		expected = self._get_expected_error()
		failure = None if expected in stderr else "Error message is not as expected."
		pass_msg = "Error message matches expected." if stderr else "No error messages as expected."
		fail_msg = failure or ""
		details = f"Expected error message:\n\n{expected}" if failure is not None else None
		case.checkpoint(failure is None, pass_msg, fail_msg, details)

	def _get_expected_error(self) -> str:
		width = self.width or 20
		height = self.height or 10
		_valid_commands = {"generate", "solve", "save", "load"}
		if self.command and self.command not in _valid_commands:
			return f"invalid choice: '{self.command}'"
		if width < 2 or height < 2:
			return "Width and height must each be at least 2"
		if self.start_row is not None and self.start_col is not None:
			if not (0 <= self.start_row < height):
				return f"Start row {self.start_row} is out of bounds (valid: 0 to {height - 1})"
			if not (0 <= self.start_col < width):
				return f"Start col {self.start_col} is out of bounds (valid: 0 to {width - 1})"
		if self.end_row is not None and self.end_col is not None:
			if not (0 <= self.end_row < height):
				return f"End row {self.end_row} is out of bounds (valid: 0 to {height - 1})"
			if not (0 <= self.end_col < width):
				return f"End col {self.end_col} is out of bounds (valid: 0 to {width - 1})"
		if (
			self.start_row is not None and self.start_col is not None
			and self.start_row == self.end_row and self.start_col == self.end_col
		):
			return "Start and end coordinates must be different"
		if self.maze_file is not None:
			return "No such file or directory"
		return ""

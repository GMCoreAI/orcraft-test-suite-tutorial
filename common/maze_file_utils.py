from __future__ import annotations


def wall_off_end(maze_file: str) -> tuple[int, int, int]:
	"""Add walls on all four sides of the E cell in a saved maze JSON file.

	Returns (end_row, end_col, walls_added).
	Raises ValueError if the file has an invalid structure.
	"""
	import json

	with open(maze_file, "r", encoding="utf-8") as f:
		data = json.load(f)

	end = data.get("end")

	if not isinstance(end, list) or len(end) != 2:
		raise ValueError(f"Maze file has invalid 'end' field: {end!r}")

	end_row, end_col = int(end[0]), int(end[1])
	height = int(data.get("height", 0))
	width = int(data.get("width", 0))
	h_walls = data["h_walls"]
	v_walls = data["v_walls"]

	walls_added = 0

	h_walls[end_row][end_col] = 1
	walls_added += 1

	if end_row + 1 <= height:
		h_walls[end_row + 1][end_col] = 1
		walls_added += 1

	v_walls[end_row][end_col] = 1
	walls_added += 1

	if end_col + 1 <= width:
		v_walls[end_row][end_col + 1] = 1
		walls_added += 1

	with open(maze_file, "w", encoding="utf-8") as f:
		json.dump(data, f)

	return end_row, end_col, walls_added


def normalize_long_path(path: object) -> str:
	"""Coerce to str, strip whitespace, and resolve Windows 8.3 short path
	components to their long equivalents.

	On non-Windows platforms the path is returned stripped.
	"""
	import os
	import sys

	path = str(path or "").strip()

	if sys.platform != "win32":
		return path

	import ctypes
	current = path
	trailing: list[str] = []
	while current:
		buf = ctypes.create_unicode_buffer(32768)
		if ctypes.windll.kernel32.GetLongPathNameW(current, buf, 32768):
			result = os.path.join(buf.value, *reversed(trailing)) if trailing else buf.value
			return result.replace("\\", "/")
		parent = os.path.dirname(current)
		if parent == current:
			break
		trailing.append(os.path.basename(current))
		current = parent

	return path


def make_maze_file_path(output_folder: str, width: int, height: int) -> str:
	"""Return a deterministic maze file path for the given parameters."""
	import os
	import tempfile

	folder = normalize_long_path(output_folder) or normalize_long_path(tempfile.gettempdir())

	path = os.path.join(folder, f"maze_{width}x{height}.json")
	return path.replace("\\", "/")


def resolve_workspace_folder(output_folder: str = "", scope: str = "") -> str:
	"""Resolve the folder that holds the generated maze files.

	Falls back to a dedicated sub-folder of the system temp directory when no
	output folder is configured, so teardown can safely remove the whole folder.
	``scope`` adds a per-test-run sub-folder so tests that run concurrently never
	generate, solve and delete the same files.
	"""
	import os
	import tempfile

	folder = normalize_long_path(output_folder)
	if not folder:
		folder = os.path.join(tempfile.gettempdir(), "orcraft_setup_teardown_mazes")

	scope = str(scope or "").strip()
	if scope:
		safe_scope = "".join(char if char.isalnum() or char in "-_" else "_" for char in scope)
		folder = os.path.join(folder, safe_scope)

	return folder.replace("\\", "/")


def maze_file_for_index(workspace_folder: str, index: int) -> str:
	"""Deterministic path of the maze file for a given 1-based case index."""
	import os

	return os.path.join(workspace_folder, f"maze_{int(index):02d}.json").replace("\\", "/")

from __future__ import annotations

import json
import os
import ssl
import subprocess
import sys
import tempfile
import uuid
from urllib.request import Request, urlopen

from orcraft import OrcraftLogger as Logger

MAZE_APP_OWNER = "GMCoreAI"
MAZE_APP_REPO = "orcraft-maze-app"


def _ssl_context() -> ssl.SSLContext:
	"""The context GitHub is reached with.

	Python's default context takes the trust roots from the system; a Python
	installed from python.org on macOS has none until its certificate script
	has been run, and every request then fails to verify GitHub.  Such a
	context is completed from a certifi bundle when one is at hand: the
	``certifi`` package, else the copy pip carries.
	"""
	context = ssl.create_default_context()
	if context.get_ca_certs():
		return context
	for module_name in ("certifi", "pip._vendor.certifi"):
		try:
			module = __import__(module_name, fromlist=["where"])
			context.load_verify_locations(module.where())
			return context
		except Exception:
			continue
	return context


def _open(request: Request, timeout: float):
	return urlopen(request, timeout=timeout, context=_ssl_context())


def _gh_headers() -> dict[str, str]:
	headers = {"User-Agent": "Orcraft/SelectLambda", "Accept": "application/vnd.github+json"}
	try:
		token = subprocess.check_output(["gh", "auth", "token"], text=True, stderr=subprocess.DEVNULL).strip()
		if token:
			headers["Authorization"] = f"Bearer {token}"
	except Exception:
		pass
	return headers


def fetch_github_release_versions(owner: str, repo: str, filter_text: str = "") -> tuple[str, ...]:
	url = f"https://api.github.com/repos/{owner}/{repo}/releases"
	request = Request(url, headers=_gh_headers())
	try:
		with _open(request, timeout=8) as response:
			releases = json.loads(response.read().decode("utf-8"))
	except Exception:
		return tuple()

	versions = [r["tag_name"] for r in releases if not r.get("draft")]
	query = filter_text.strip().lower()
	if query:
		versions = [v for v in versions if query in v.lower()]
	return tuple(versions)


def _resolve_asset_names(tag: str) -> tuple[str, ...]:
	"""Candidate asset names for the current platform, in preference order.

	Windows assets may or may not carry a '.exe' suffix depending on the
	release, so both spellings are accepted (newer releases include '.exe').
	"""
	ver = tag.removeprefix("maze-")
	if sys.platform == "win32":
		return (f"maze-{ver}-win.exe", f"maze-{ver}-win")
	elif sys.platform == "darwin":
		return (f"maze-{ver}-macos",)
	else:
		return (f"maze-{ver}-linux",)


def download_github_release_binary(owner: str, repo: str, tag: str, dest_dir: str, force: bool = False) -> str:
	candidates = _resolve_asset_names(tag)

	cached = next((os.path.join(dest_dir, name) for name in candidates if os.path.isfile(os.path.join(dest_dir, name))), None)
	if cached is not None and not force:
		Logger.log(f"Using cached app {tag} — skipping download.\n", module_tag=False)
		return dest_dir

	url = f"https://api.github.com/repos/{owner}/{repo}/releases/tags/{tag}"
	request = Request(url, headers=_gh_headers())
	with _open(request, timeout=10) as response:
		release = json.loads(response.read().decode("utf-8"))

	assets_by_name = {a["name"]: a for a in release.get("assets", [])}
	asset_name = next((name for name in candidates if name in assets_by_name), None)
	if asset_name is None:
		raise FileNotFoundError(f"None of {candidates} found in release '{tag}'")
	asset = assets_by_name[asset_name]
	dest_path = os.path.join(dest_dir, asset_name)

	# Use the API asset URL with Accept: octet-stream so auth header is respected (works for private repos)
	Logger.log(f"Downloading app {tag}...\n", module_tag=False)
	api_asset_url = asset["url"]
	dl_headers = {**_gh_headers(), "Accept": "application/octet-stream"}
	dl_request = Request(api_asset_url, headers=dl_headers)
	os.makedirs(dest_dir, exist_ok=True)
	# Tests run in parallel and share this cache: the download lands in a file
	# of its own and takes the binary's name in one rename, so a test already
	# running the binary keeps the file it started (writing over a running
	# binary fails on Linux with "Text file busy") and no test ever runs a
	# half-written one.  A cached binary that appeared meanwhile is kept.
	part_path = os.path.join(dest_dir, f".{asset_name}.{uuid.uuid4().hex[:8]}.part")
	try:
		with _open(dl_request, timeout=60) as response, open(part_path, "wb") as f:
			f.write(response.read())
		if sys.platform != "win32":
			os.chmod(part_path, 0o755)
		if not (os.path.isfile(dest_path) and not force):
			try:
				os.replace(part_path, dest_path)
			except OSError:
				if not os.path.isfile(dest_path):
					raise
	finally:
		if os.path.exists(part_path):
			os.remove(part_path)

	return dest_dir


def fetch_maze_app_release_versions(filter_text: str = "") -> tuple[str, ...]:
	return fetch_github_release_versions(MAZE_APP_OWNER, MAZE_APP_REPO, filter_text)


def download_maze_app_release_binary(tag: str, dest_dir: str, force: bool = False) -> str:
	return download_github_release_binary(MAZE_APP_OWNER, MAZE_APP_REPO, tag, dest_dir, force=force)


def get_maze_app_bin_folder(tag: str, force: bool = False) -> str:
	dest_dir = os.path.join(tempfile.gettempdir(), "orcraft-maze-bins", tag)
	return download_maze_app_release_binary(tag, dest_dir, force=force)

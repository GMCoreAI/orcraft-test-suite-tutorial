from __future__ import annotations

from orcraft import (
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)

from common.github_repo_access import fetch_maze_app_release_versions
from common.maze_app import MazeApp


class TestLambdaMultiSelectorParameterConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Lambda Multi-Selector Parameter")

	description = OrcraftConfigField.Text(
		default=(
			"Demonstrates a lambda multi-selector configuration parameter.\n"
			"Fetches available maze app releases from GitHub and lets you pick multiple versions to run."
		)
	)

	maze_app_versions = OrcraftConfigField.MultiSelectLambda(
		default=(),
		label="Maze App Versions",
		input_placeholder="Filter versions (e.g. v3)",
		button_text="Fetch",
		options_lambda=lambda text: fetch_maze_app_release_versions(text),
		required=True,
		layout=OrcraftConfigField.Layout.NewRow,
	)

	force_redownload = OrcraftConfigField.Boolean(
		default=False,
		label="Re-download (ignore cached binary)",
		layout=OrcraftConfigField.Layout.NewRow,
	)
	
	command = OrcraftConfigField.Select(
		default="generate",
		label="Command",
		options=("generate", "solve", "save"),
		layout=OrcraftConfigField.Layout.NewRow,
	)


class TestLambdaMultiSelectorParameter(OrcraftTest):
	def __init__(self, config: TestLambdaMultiSelectorParameterConfig | None = None) -> None:
		super().__init__(config or TestLambdaMultiSelectorParameterConfig())

	def _run_case(self, case: OrcraftTestCase):

		for tag in self.config.maze_app_versions:

			maze_app = MazeApp.from_release(tag, self.config.command, force=self.config.force_redownload)

			maze_app.run()

		return case.result


def main() -> None:
	test = TestLambdaMultiSelectorParameter()
	test.run()


if __name__ == "__main__":
	main()

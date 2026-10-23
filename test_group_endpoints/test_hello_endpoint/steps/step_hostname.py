from __future__ import annotations

import subprocess

from orcraft import (
	OrcraftLogger as Logger,
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftResultField,
	OrcraftConfigField,
)


class StepHostnameConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Hostname")


class StepHostnameResult(OrcraftTestStepResult):
	hostname = OrcraftResultField.Text(default="", label="Hostname")


class StepHostname(OrcraftTestStep):
	def __init__(self, config: StepHostnameConfig | None = None) -> None:
		super().__init__(config or StepHostnameConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepHostnameResult()

		# The step's body runs on the endpoint it was sent to, so the command
		# answers with that machine's name.
		completed = subprocess.run(["hostname"], capture_output=True, text=True)
		hostname = completed.stdout.strip()

		self.checkpoint(
			completed.returncode == 0 and bool(hostname),
			f"hostname answered: {hostname}",
			f"hostname failed with exit code {completed.returncode}: {completed.stderr.strip()}",
		)

		Logger.log(f"Hello from {hostname}", color=Logger.Color.BLUE)

		self.result.hostname = hostname

		return self.result

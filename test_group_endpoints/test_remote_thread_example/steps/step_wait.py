from __future__ import annotations

import time

from orcraft import (
	OrcraftStatus,
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftConfigField,
	OrcraftLogger as Logger,
)


class StepWaitConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Wait")
	wait_sec = OrcraftConfigField.Numeric(default=2.0, label="Wait Sec")


class StepWaitResult(OrcraftTestStepResult):
	pass


class StepWait(OrcraftTestStep):
	def __init__(self, config: StepWaitConfig | None = None) -> None:
		super().__init__(config or StepWaitConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		self.result = StepWaitResult()
		wait_sec = float(self.config.wait_sec)
		Logger.log(
			f"Waiting {wait_sec}s while the background thread continues to run...",
			module_tag=False,
		)
		time.sleep(wait_sec)
		Logger.log("Wait complete.", module_tag=False)
		self.result.status = OrcraftStatus.PASS
		return self.result

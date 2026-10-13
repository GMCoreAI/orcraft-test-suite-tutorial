from __future__ import annotations

from orcraft import (
	OrcraftStatus,
	OrcraftTestStep,
	OrcraftTestStepConfig,
	OrcraftTestStepResult,
	OrcraftConfigField,
	OrcraftLogger as Logger,
)


class StepTriggerRebootConfig(OrcraftTestStepConfig):
	name = OrcraftConfigField.Text(default="Trigger Reboot")
	enable_reboot = OrcraftConfigField.Boolean(default=False, label="Enable Reboot")
	reboot_delay_sec = OrcraftConfigField.Numeric(default=0, label="Reboot Delay Sec")


class StepTriggerRebootResult(OrcraftTestStepResult):
	pass


class StepTriggerReboot(OrcraftTestStep):
	def __init__(self, config: StepTriggerRebootConfig | None = None) -> None:
		super().__init__(config or StepTriggerRebootConfig())

	def _run_step(self) -> OrcraftTestStepResult:
		import os
		import platform

		self.result = StepTriggerRebootResult()

		if self.config.enable_reboot:
			delay = int(self.config.reboot_delay_sec)
			Logger.log(f"Triggering reboot with delay={delay}s", module_tag=False)

			if platform.system() == "Windows":
				os.system(f"shutdown /r /t {delay}")
			else:
				os.system(f"shutdown -r +{max(0, delay // 60)} &")
		else:
			Logger.log(
				"Reboot skipped (enable_reboot=False). Endpoint will not be rebooted.",
				module_tag=False,
			)

		self.result.status = OrcraftStatus.PASS
		return self.result

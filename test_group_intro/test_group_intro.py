from __future__ import annotations

from orcraft import (
	OrcraftTestGroup,
	OrcraftTestGroupConfig,
	OrcraftTestGroupResult,
	OrcraftConfigField,
)

from test_group_intro.test_hello_world.test_hello_world import TestHelloWorld


class TestGroupIntroConfig(OrcraftTestGroupConfig):
	name = OrcraftConfigField.Text(default="Intro")
	description = OrcraftConfigField.Text(
		default="Introductory group covering the simplest Orcraft examples."
	)
	tests = OrcraftConfigField.Tests(
		default_factory=lambda: [
			TestHelloWorld(),
		]
	)

class TestGroupIntroResult(OrcraftTestGroupResult):
	pass


class TestGroupIntro(OrcraftTestGroup):
	def __init__(self) -> None:
		super().__init__(config=TestGroupIntroConfig())
		self.result = TestGroupIntroResult()


def main() -> None:
	group = TestGroupIntro()
	group.run()


if __name__ == "__main__":
	main()

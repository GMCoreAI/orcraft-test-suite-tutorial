from __future__ import annotations

from orcraft import (
	OrcraftLogger as Logger,
	OrcraftTest,
	OrcraftTestConfig,
	OrcraftTestCase,
	OrcraftConfigField,
)


class TestHelloWorldConfig(OrcraftTestConfig):
	name = OrcraftConfigField.Text(default="Hello World")
	
	description = OrcraftConfigField.Text(
		default=(
			"This is a minimal implementation of an Orcraft Test.\n"
			"It demonstrates how to define a test config, inherit from OrcraftTest, and implement a single test case.\n"
			"When executed, the test logs a simple Hello World message and returns a passing test result."
		)
	)


class TestHelloWorld(OrcraftTest):
	def __init__(self, config: TestHelloWorldConfig | None = None) -> None:
		super().__init__(config or TestHelloWorldConfig())

	def _run_case(self, case: OrcraftTestCase):

		Logger.log("Hello World", color=Logger.Color.BLUE)

		return case.result


def main() -> None:
	test = TestHelloWorld()
	test.run()


if __name__ == "__main__":
	main()

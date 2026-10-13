from __future__ import annotations

from orcraft import (
	OrcraftTestGroup,
	OrcraftTestGroupConfig,
	OrcraftTestGroupResult,
	OrcraftConfigField,
)

from test_group_endpoints.test_default_endpoint_and_package_upload.test_default_endpoint_and_package_upload import TestDefaultEndpointAndPackageUpload
from test_group_endpoints.test_package_upload_parameter_types.test_package_upload_parameter_types import TestPackageUploadParameterTypes
from test_group_endpoints.test_multiple_endpoints_and_files_transfer.test_multiple_endpoints_and_files_transfer import TestMultipleEndpointsAndFilesTransfer
from test_group_endpoints.test_multi_select_endpoints.test_multi_select_endpoints import TestMultiSelectEndpoints
from test_group_endpoints.test_endpoint_fanout.test_endpoint_fanout import TestEndpointFanout
from test_group_endpoints.test_endpoint_fanout_queued.test_endpoint_fanout_queued import TestEndpointFanoutQueued
from test_group_endpoints.test_endpoint_fanout_permutations.test_endpoint_fanout_permutations import TestEndpointFanoutPermutations
from test_group_endpoints.test_remote_thread_example.test_remote_thread_example import TestRemoteThreadExample
from test_group_endpoints.test_type_fidelity.test_type_fidelity import TestTypeFidelity
from test_group_endpoints.test_controlled_endpoint_disconnection.test_controlled_endpoint_disconnection import TestControlledEndpointDisconnection
from test_group_endpoints.test_endpoint_restart.test_endpoint_restart import TestEndpointRestart


class TestGroupEndpointsConfig(OrcraftTestGroupConfig):
	name = OrcraftConfigField.Text(default="Endpoints")
	description = OrcraftConfigField.Text(
		default=(
			"Covers endpoint-focused tests: default endpoints, package upload, file "
			"transfer, multi-select and fan-out across endpoints, remote threads, and "
			"endpoint disconnection and restart handling."
		)
	)
	tests = OrcraftConfigField.Tests(
		default_factory=lambda: [
			TestDefaultEndpointAndPackageUpload(),
			TestMultipleEndpointsAndFilesTransfer(),
			TestMultiSelectEndpoints(),
			TestEndpointFanout(),
			TestEndpointFanoutQueued(),
			TestEndpointFanoutPermutations(),
			TestPackageUploadParameterTypes(),
			TestRemoteThreadExample(),
			TestTypeFidelity(),
			TestControlledEndpointDisconnection(),
			TestEndpointRestart(),
		]
	)


class TestGroupEndpointsResult(OrcraftTestGroupResult):
	pass


class TestGroupEndpoints(OrcraftTestGroup):
	def __init__(self) -> None:
		super().__init__(config=TestGroupEndpointsConfig())
		self.result = TestGroupEndpointsResult()


def main() -> None:
	group = TestGroupEndpoints()
	group.run()


if __name__ == "__main__":
	main()

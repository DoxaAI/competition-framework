import os
from typing import List
from urllib.parse import urlparse

from grpclib.client import Channel

from doxa_competition.proto.nodeapi import (
    CaptureOutputRequest,
    NodeApiStub,
    SpawnApplicationRequest,
)


class Node:
    """The DOXA Competition Framework representation of a Hearth node."""

    participant_index: int
    agent_id: int
    agent_metadata: dict
    enrolment_id: int
    endpoint: str
    auth_token: str

    def __init__(
        self,
        participant_index: int,
        agent_id: int,
        agent_metadata: dict,
        enrolment_id: int,
        endpoint: str,
        auth_token: str,
    ) -> None:
        self.participant_index = participant_index
        self.agent_id = agent_id
        self.agent_metadata = agent_metadata
        self.enrolment_id = enrolment_id
        self.endpoint = endpoint
        self.auth_token = auth_token

        endpoint = urlparse(os.environ.get("HEARTH_ENDPOINT_OVERRIDE", self.endpoint))

        self.node_channel = Channel(host=endpoint.hostname, port=endpoint.port)
        self.node_api = NodeApiStub(self.node_channel)

    def fetch_agent(self):
        # TODO: gRPC call to get the agent to fetch the node
        pass

    async def run_command(self, args: List[str], environment: List[str] = None):
        return await self.node_api.spawn_application(
            SpawnApplicationRequest(
                args=args,
                mode=0,
                capture_stdout=True,
                capture_stderr=True,
                working_dir="/app",
                uid=1000,
                gid=1000,
                env_vars=environment if environment is not None else [],
            ),
            metadata={"x-hearth-auth": self.auth_token},
        )

    async def read_stdout(self):
        async for response in self.node_api.capture_output(
            CaptureOutputRequest(stdout=True, stderr=False),
            metadata={"x-hearth-auth": self.auth_token},
        ):
            yield response.line

    def release(self):
        # TODO: gRPC call to release the node
        pass

    # TODO: implement getting files
    # TODO: handle reading from and writing to stdio (possibly implemented as a generator!)

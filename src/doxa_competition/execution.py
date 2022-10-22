import os
from typing import List
from urllib.parse import urlparse

from grpclib.client import Channel

from doxa_competition.proto.nodeapi import (
    CaptureOutputRequest,
    DownloadApplicationRequest,
    FileRequest,
    NodeApiStub,
    ShutdownNodeRequest,
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

    def is_gzip(self) -> bool:
        try:
            return bool(self.agent_metadata.get("gzip", True))
        except:
            return True

    async def fetch_agent(self):
        return await self.node_api.download_application(
            DownloadApplicationRequest(
                endpoint=self.endpoint,
                endpoint_bearer=self.auth_token,
                gzip=self.is_gzip(),
            ),
            metadata={"x-hearth-auth": self.auth_token},
        )

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

    async def get_file(self, path: str):
        async for response in self.node_api.get_file(
            FileRequest(path=path),
            metadata={"x-hearth-auth": self.auth_token},
        ):
            yield response.data

    async def release(self):
        return await self.node_api.shutdown_node(
            ShutdownNodeRequest(), metadata={"x-hearth-auth": self.auth_token}
        )

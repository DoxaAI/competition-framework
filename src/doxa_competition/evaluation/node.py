import os
from typing import AsyncIterable, List, Tuple
from urllib.parse import urlsplit

from doxa_competition.evaluation.errors import AgentError
from doxa_competition.proto.nodeapi import (
    CaptureOutputRequest,
    DownloadApplicationRequest,
    FileRequest,
    NodeApiStub,
    ShutdownNodeRequest,
    SpawnApplicationRequest,
    WriteInputRequest,
)
from doxa_competition.utils import is_valid_filename
from grpclib.client import Channel


class Node:
    """The DOXA Competition Framework representation of a Hearth node."""

    participant_index: int
    agent_id: int
    agent_metadata: dict
    enrolment_id: int
    endpoint: str
    storage_endpoint: str
    upload_id: int
    auth_token: str

    def __init__(
        self,
        participant_index: int,
        agent_id: int,
        agent_metadata: dict,
        enrolment_id: int,
        endpoint: str,
        storage_endpoint: str,
        upload_id: int,
        auth_token: str,
        timeout: float = None,
    ) -> None:
        self.participant_index = participant_index
        self.agent_id = agent_id
        self.agent_metadata = agent_metadata
        self.enrolment_id = enrolment_id
        self.endpoint = os.environ.get("HEARTH_ENDPOINT_OVERRIDE", endpoint)
        self.storage_endpoint = storage_endpoint
        self.upload_id = upload_id
        self.auth_token = auth_token
        self.timeout = timeout

        hostname, port = self.parse_endpoint(self.endpoint)

        self.node_channel = Channel(host=hostname, port=port)
        self.node_api = NodeApiStub(self.node_channel)

    def parse_endpoint(self, endpoint) -> Tuple[str, int]:
        components = urlsplit(endpoint if "//" in endpoint else "//" + endpoint)
        return components.hostname, components.port if components.port else 5050

    def is_gzip(self) -> bool:
        try:
            return bool(self.agent_metadata.get("gzip", True))
        except:
            return True

    async def fetch_agent(self):
        return await self.node_api.download_application(
            DownloadApplicationRequest(
                endpoint=f"{self.storage_endpoint}download/{self.upload_id}",
                endpoint_bearer="",
                gzip=self.is_gzip(),
            ),
            metadata={"x-hearth-auth": self.auth_token},
            timeout=self.timeout,
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
            timeout=self.timeout,
        )

    async def run_python_application(self, args: List[str] = None):
        if not is_valid_filename(self.agent_metadata.get("entrypoint", "")):
            raise AgentError(message="Bad entrypoint filename.", agent_id=self.agent_id)

        return await self.run_command(
            args=[
                "python3",
                self.agent_metadata["entrypoint"],
            ]
            + (args if args else [])
        )

    async def write_to_stdin(self, line: str, end: str = "\n"):
        async def wrapper():
            yield f"{line}{end}"

        return await self.write_lines_to_stdin(wrapper())

    async def write_lines_to_stdin(self, lines: AsyncIterable[str]):
        async def wrapper():
            async for line in lines:
                yield WriteInputRequest(data=line.encode("utf-8"))

        return await self.node_api.write_input(
            wrapper(),
            metadata={"x-hearth-auth": self.auth_token},
            timeout=self.timeout,
        )

    async def read_stdout(self):
        async for response in self.node_api.capture_output(
            CaptureOutputRequest(stdout=True, stderr=False),
            metadata={"x-hearth-auth": self.auth_token},
            timeout=self.timeout,
        ):
            yield response.line

    async def read_stderr(self):
        async for response in self.node_api.capture_output(
            CaptureOutputRequest(stdout=False, stderr=True),
            metadata={"x-hearth-auth": self.auth_token},
            timeout=self.timeout,
        ):
            yield response.line

    async def read_stdout_all(self) -> str:
        return "".join([result async for result in self.read_stdout()])

    async def read_stderr_all(self) -> str:
        return "".join([result async for result in self.read_stderr()])

    async def get_file(self, path: str):
        async for response in self.node_api.get_file(
            FileRequest(path=path),
            metadata={"x-hearth-auth": self.auth_token},
            timeout=self.timeout,
        ):
            yield response.data

    async def release(self):
        try:
            await self.node_api.shutdown_node(
                ShutdownNodeRequest(),
                metadata={"x-hearth-auth": self.auth_token},
                timeout=self.timeout,
            )
        finally:
            self.node_channel.close()

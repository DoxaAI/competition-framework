import asyncio
import os
from typing import AsyncIterable, Dict, List, Optional, Tuple
from urllib.parse import urlsplit

from grpclib.client import Channel

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

DEFAULT_TIMEOUT = 30  # 30 secs


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
    timeouts: Dict[str, float]

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
        timeouts: Optional[Dict[str, float]] = None,
    ) -> None:
        self.participant_index = participant_index
        self.agent_id = agent_id
        self.agent_metadata = agent_metadata
        self.enrolment_id = enrolment_id
        self.endpoint = os.environ.get("HEARTH_ENDPOINT_OVERRIDE", endpoint)
        self.storage_endpoint = storage_endpoint
        self.upload_id = upload_id
        self.auth_token = auth_token

        self.timeouts = {
            "FETCH_AGENT": DEFAULT_TIMEOUT,
            "RUN_COMMAND": DEFAULT_TIMEOUT,
            "WRITE_STDIN": DEFAULT_TIMEOUT,
            "READ_STDOUT": 10 * 60,  # 10 minutes
            "READ_STDERR": 5,  # 5 seconds
            "GET_FILE": DEFAULT_TIMEOUT,
            "RELEASE": DEFAULT_TIMEOUT,
        }

        if timeouts is not None:
            self.timeouts.update(timeouts)

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
            timeout=self.timeouts["FETCH_AGENT"],
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
            timeout=self.timeouts["RUN_COMMAND"],
        )

    async def run_python_application(self, args: List[str] = None):
        if not is_valid_filename(self.agent_metadata.get("entrypoint", "")):
            raise AgentError(
                message="Bad entrypoint filename.", participant=self.participant_index
            )

        return await self.run_command(
            args=[
                "python3",
                self.agent_metadata["entrypoint"],
            ]
            + (args if args else [])
        )

    async def write_to_stdin(
        self, line: str, end: str = "\n", timeout: Optional[float] = None
    ):
        async def wrapper():
            yield f"{line}{end}"

        return await self.write_lines_to_stdin(wrapper(), timeout)

    async def write_lines_to_stdin(
        self, lines: AsyncIterable[str], timeout: Optional[float] = None
    ):
        async def wrapper():
            async for line in lines:
                yield WriteInputRequest(data=line.encode("utf-8"))

        return await self.node_api.write_input(
            wrapper(),
            metadata={"x-hearth-auth": self.auth_token},
            timeout=timeout if timeout is not None else self.timeouts["WRITE_STDIN"],
        )

    async def read_stdout(self, timeout: Optional[float] = None):
        async for response in self.node_api.capture_output(
            CaptureOutputRequest(stdout=True, stderr=False),
            metadata={"x-hearth-auth": self.auth_token},
            timeout=timeout if timeout is not None else self.timeouts["READ_STDOUT"],
        ):
            yield response.line

    async def read_stderr(self, timeout: Optional[float] = None):
        async for response in self.node_api.capture_output(
            CaptureOutputRequest(stdout=False, stderr=True),
            metadata={"x-hearth-auth": self.auth_token},
            timeout=timeout if timeout is not None else self.timeouts["READ_STDERR"],
        ):
            yield response.line

    async def read_stdout_all(self, timeout: Optional[float] = None) -> str:
        return "\n".join([result async for result in self.read_stdout(timeout)])

    async def read_stderr_all(
        self, timeout: Optional[float] = None, error_on_failure: bool = False
    ) -> str:
        try:
            return "\n".join([result async for result in self.read_stderr(timeout)])
        except asyncio.TimeoutError as e:
            if error_on_failure:
                raise e

            return ""

    async def get_file(self, path: str):
        async for response in self.node_api.get_file(
            FileRequest(path=path),
            metadata={"x-hearth-auth": self.auth_token},
            timeout=self.timeouts["GET_FILE"],
        ):
            yield response.data

    async def release(self):
        try:
            await self.node_api.shutdown_node(
                ShutdownNodeRequest(),
                metadata={"x-hearth-auth": self.auth_token},
                timeout=self.timeouts["RELEASE"],
            )
        finally:
            self.node_channel.close()

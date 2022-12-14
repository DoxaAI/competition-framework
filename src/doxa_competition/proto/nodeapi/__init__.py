# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: proto/nodeapi.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    AsyncIterable,
    AsyncIterator,
    Dict,
    Iterable,
    List,
    Optional,
    Union,
)

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase


if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpc.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


class SpawnMode(betterproto.Enum):
    START = 0
    RESTART = 1


@dataclass(eq=False, repr=False)
class ShutdownNodeRequest(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class ShutdownNodeResponse(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class WriteInputRequest(betterproto.Message):
    data: bytes = betterproto.bytes_field(1)


@dataclass(eq=False, repr=False)
class WriteInputResponse(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class DownloadApplicationRequest(betterproto.Message):
    """
    Tells the hearth node to download the application from the specified URL
    (endpoint) optionally providing a bearer auth token to authorize the node.
    """

    endpoint: str = betterproto.string_field(1)
    gzip: bool = betterproto.bool_field(2)
    endpoint_bearer: str = betterproto.string_field(3)
    """optional"""


@dataclass(eq=False, repr=False)
class DownloadApplicationResponse(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class UploadApplicationRequestMetadata(betterproto.Message):
    path: str = betterproto.string_field(1)
    gzip: bool = betterproto.bool_field(2)


@dataclass(eq=False, repr=False)
class UploadApplicationRequest(betterproto.Message):
    """
    Uploads the application to the controller environment. This must be done
    once, before the application can be spawned.
    """

    metadata: "UploadApplicationRequestMetadata" = betterproto.message_field(
        1, group="request"
    )
    tarfile: bytes = betterproto.bytes_field(2, group="request")


@dataclass(eq=False, repr=False)
class UploadApplicationResponse(betterproto.Message):
    """Response from uploading an application."""

    pass


@dataclass(eq=False, repr=False)
class SpawnApplicationRequest(betterproto.Message):
    """A request to spawn the application."""

    args: List[str] = betterproto.string_field(1)
    mode: "SpawnMode" = betterproto.enum_field(2)
    capture_stdout: bool = betterproto.bool_field(3)
    capture_stderr: bool = betterproto.bool_field(4)
    working_dir: str = betterproto.string_field(5)
    uid: int = betterproto.int32_field(6)
    gid: int = betterproto.int32_field(7)
    env_vars: List[str] = betterproto.string_field(8)


@dataclass(eq=False, repr=False)
class SpawnApplicationResponse(betterproto.Message):
    """Response from spawning an application."""

    instance_id: str = betterproto.string_field(1)
    """
    Whenever an application is spawned it is associated with a unique
    instanceid which allows futures calls to
    """


@dataclass(eq=False, repr=False)
class CaptureOutputRequest(betterproto.Message):
    """
    A request to capture the stdout/stderr of an application. An output stream
    (either stdout or stderr) can only be captured once and only if it was
    captured when the application was spawned. The output stream contains all
    the data from the start of the stream, in part this means that any output
    stream captured when the application is spawned should be consumed to avoid
    wasting RAM. If stdout and stderr are both specified then they are
    interlaced as soon as they become available on a best effort basis. You
    should not make any expectations on the order of interlacing particularly
    any output that is buffered before the capture begins.
    """

    stdout: bool = betterproto.bool_field(1)
    stderr: bool = betterproto.bool_field(2)


@dataclass(eq=False, repr=False)
class ApplicationOutput(betterproto.Message):
    """The output stream of an application."""

    line: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class FileRequest(betterproto.Message):
    """Specifies a single path."""

    path: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class FileData(betterproto.Message):
    data: bytes = betterproto.bytes_field(1)


class NodeApiStub(betterproto.ServiceStub):
    async def upload_application(
        self,
        upload_application_request_iterator: Union[
            AsyncIterable["UploadApplicationRequest"],
            Iterable["UploadApplicationRequest"],
        ],
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "UploadApplicationResponse":
        return await self._stream_unary(
            "/nodeapi.NodeAPI/UploadApplication",
            upload_application_request_iterator,
            UploadApplicationRequest,
            UploadApplicationResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def spawn_application(
        self,
        spawn_application_request: "SpawnApplicationRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "SpawnApplicationResponse":
        return await self._unary_unary(
            "/nodeapi.NodeAPI/SpawnApplication",
            spawn_application_request,
            SpawnApplicationResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def get_file(
        self,
        file_request: "FileRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> AsyncIterator["FileData"]:
        async for response in self._unary_stream(
            "/nodeapi.NodeAPI/GetFile",
            file_request,
            FileData,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        ):
            yield response

    async def capture_output(
        self,
        capture_output_request: "CaptureOutputRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> AsyncIterator["ApplicationOutput"]:
        async for response in self._unary_stream(
            "/nodeapi.NodeAPI/CaptureOutput",
            capture_output_request,
            ApplicationOutput,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        ):
            yield response

    async def write_input(
        self,
        write_input_request_iterator: Union[
            AsyncIterable["WriteInputRequest"], Iterable["WriteInputRequest"]
        ],
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "WriteInputResponse":
        return await self._stream_unary(
            "/nodeapi.NodeAPI/WriteInput",
            write_input_request_iterator,
            WriteInputRequest,
            WriteInputResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def shutdown_node(
        self,
        shutdown_node_request: "ShutdownNodeRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "ShutdownNodeResponse":
        return await self._unary_unary(
            "/nodeapi.NodeAPI/ShutdownNode",
            shutdown_node_request,
            ShutdownNodeResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def download_application(
        self,
        download_application_request: "DownloadApplicationRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "DownloadApplicationResponse":
        return await self._unary_unary(
            "/nodeapi.NodeAPI/DownloadApplication",
            download_application_request,
            DownloadApplicationResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class NodeApiBase(ServiceBase):
    async def upload_application(
        self,
        upload_application_request_iterator: AsyncIterator["UploadApplicationRequest"],
    ) -> "UploadApplicationResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def spawn_application(
        self, spawn_application_request: "SpawnApplicationRequest"
    ) -> "SpawnApplicationResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def get_file(self, file_request: "FileRequest") -> AsyncIterator["FileData"]:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def capture_output(
        self, capture_output_request: "CaptureOutputRequest"
    ) -> AsyncIterator["ApplicationOutput"]:
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def write_input(
        self, write_input_request_iterator: AsyncIterator["WriteInputRequest"]
    ) -> "WriteInputResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def shutdown_node(
        self, shutdown_node_request: "ShutdownNodeRequest"
    ) -> "ShutdownNodeResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def download_application(
        self, download_application_request: "DownloadApplicationRequest"
    ) -> "DownloadApplicationResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_upload_application(
        self,
        stream: "grpclib.server.Stream[UploadApplicationRequest, UploadApplicationResponse]",
    ) -> None:
        request = stream.__aiter__()
        response = await self.upload_application(request)
        await stream.send_message(response)

    async def __rpc_spawn_application(
        self,
        stream: "grpclib.server.Stream[SpawnApplicationRequest, SpawnApplicationResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.spawn_application(request)
        await stream.send_message(response)

    async def __rpc_get_file(
        self, stream: "grpclib.server.Stream[FileRequest, FileData]"
    ) -> None:
        request = await stream.recv_message()
        await self._call_rpc_handler_server_stream(
            self.get_file,
            stream,
            request,
        )

    async def __rpc_capture_output(
        self, stream: "grpclib.server.Stream[CaptureOutputRequest, ApplicationOutput]"
    ) -> None:
        request = await stream.recv_message()
        await self._call_rpc_handler_server_stream(
            self.capture_output,
            stream,
            request,
        )

    async def __rpc_write_input(
        self, stream: "grpclib.server.Stream[WriteInputRequest, WriteInputResponse]"
    ) -> None:
        request = stream.__aiter__()
        response = await self.write_input(request)
        await stream.send_message(response)

    async def __rpc_shutdown_node(
        self, stream: "grpclib.server.Stream[ShutdownNodeRequest, ShutdownNodeResponse]"
    ) -> None:
        request = await stream.recv_message()
        response = await self.shutdown_node(request)
        await stream.send_message(response)

    async def __rpc_download_application(
        self,
        stream: "grpclib.server.Stream[DownloadApplicationRequest, DownloadApplicationResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.download_application(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/nodeapi.NodeAPI/UploadApplication": grpclib.const.Handler(
                self.__rpc_upload_application,
                grpclib.const.Cardinality.STREAM_UNARY,
                UploadApplicationRequest,
                UploadApplicationResponse,
            ),
            "/nodeapi.NodeAPI/SpawnApplication": grpclib.const.Handler(
                self.__rpc_spawn_application,
                grpclib.const.Cardinality.UNARY_UNARY,
                SpawnApplicationRequest,
                SpawnApplicationResponse,
            ),
            "/nodeapi.NodeAPI/GetFile": grpclib.const.Handler(
                self.__rpc_get_file,
                grpclib.const.Cardinality.UNARY_STREAM,
                FileRequest,
                FileData,
            ),
            "/nodeapi.NodeAPI/CaptureOutput": grpclib.const.Handler(
                self.__rpc_capture_output,
                grpclib.const.Cardinality.UNARY_STREAM,
                CaptureOutputRequest,
                ApplicationOutput,
            ),
            "/nodeapi.NodeAPI/WriteInput": grpclib.const.Handler(
                self.__rpc_write_input,
                grpclib.const.Cardinality.STREAM_UNARY,
                WriteInputRequest,
                WriteInputResponse,
            ),
            "/nodeapi.NodeAPI/ShutdownNode": grpclib.const.Handler(
                self.__rpc_shutdown_node,
                grpclib.const.Cardinality.UNARY_UNARY,
                ShutdownNodeRequest,
                ShutdownNodeResponse,
            ),
            "/nodeapi.NodeAPI/DownloadApplication": grpclib.const.Handler(
                self.__rpc_download_application,
                grpclib.const.Cardinality.UNARY_UNARY,
                DownloadApplicationRequest,
                DownloadApplicationResponse,
            ),
        }

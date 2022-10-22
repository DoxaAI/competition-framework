# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: proto/agent.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
)

import betterproto
import grpclib
from betterproto.grpc.grpclib_server import ServiceBase


if TYPE_CHECKING:
    import grpclib.server
    from betterproto.grpc.grpclib_client import MetadataLike
    from grpclib.metadata import Deadline


@dataclass(eq=False, repr=False)
class AgentResult(betterproto.Message):
    id: int = betterproto.int32_field(1)
    agent_id: int = betterproto.int32_field(2)
    metric: str = betterproto.string_field(3)
    result: int = betterproto.int64_field(4)
    created_at: str = betterproto.string_field(5)
    updated_at: str = betterproto.string_field(6)


@dataclass(eq=False, repr=False)
class GetAgentResultsRequest(betterproto.Message):
    agent_id: int = betterproto.int32_field(1)


@dataclass(eq=False, repr=False)
class GetAgentResultsResponse(betterproto.Message):
    results: List["AgentResult"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class SetAgentResultRequest(betterproto.Message):
    agent_id: int = betterproto.int32_field(1)
    metric: str = betterproto.string_field(2)
    result: int = betterproto.int64_field(3)


@dataclass(eq=False, repr=False)
class SetAgentResultResponse(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class SetAgentResultsRequest(betterproto.Message):
    results: List["SetAgentResultRequest"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class SetAgentResultsResponse(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class AddToAgentResultRequest(betterproto.Message):
    agent_id: int = betterproto.int32_field(1)
    metric: str = betterproto.string_field(2)
    result: int = betterproto.int64_field(3)


@dataclass(eq=False, repr=False)
class AddToAgentResultResponse(betterproto.Message):
    pass


@dataclass(eq=False, repr=False)
class AddToAgentResultsRequest(betterproto.Message):
    results: List["AddToAgentResultRequest"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class AddToAgentResultsResponse(betterproto.Message):
    pass


class UmpireAgentServiceStub(betterproto.ServiceStub):
    async def get_agent_results(
        self,
        get_agent_results_request: "GetAgentResultsRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetAgentResultsResponse":
        return await self._unary_unary(
            "/umpire.agent.UmpireAgentService/GetAgentResults",
            get_agent_results_request,
            GetAgentResultsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def set_agent_result(
        self,
        set_agent_result_request: "SetAgentResultRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "SetAgentResultResponse":
        return await self._unary_unary(
            "/umpire.agent.UmpireAgentService/SetAgentResult",
            set_agent_result_request,
            SetAgentResultResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def set_agent_results(
        self,
        set_agent_results_request: "SetAgentResultsRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "SetAgentResultsResponse":
        return await self._unary_unary(
            "/umpire.agent.UmpireAgentService/SetAgentResults",
            set_agent_results_request,
            SetAgentResultsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def add_to_agent_result(
        self,
        add_to_agent_result_request: "AddToAgentResultRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "AddToAgentResultResponse":
        return await self._unary_unary(
            "/umpire.agent.UmpireAgentService/AddToAgentResult",
            add_to_agent_result_request,
            AddToAgentResultResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def add_to_agent_results(
        self,
        add_to_agent_results_request: "AddToAgentResultsRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "AddToAgentResultsResponse":
        return await self._unary_unary(
            "/umpire.agent.UmpireAgentService/AddToAgentResults",
            add_to_agent_results_request,
            AddToAgentResultsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class UmpireAgentServiceBase(ServiceBase):
    async def get_agent_results(
        self, get_agent_results_request: "GetAgentResultsRequest"
    ) -> "GetAgentResultsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def set_agent_result(
        self, set_agent_result_request: "SetAgentResultRequest"
    ) -> "SetAgentResultResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def set_agent_results(
        self, set_agent_results_request: "SetAgentResultsRequest"
    ) -> "SetAgentResultsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def add_to_agent_result(
        self, add_to_agent_result_request: "AddToAgentResultRequest"
    ) -> "AddToAgentResultResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def add_to_agent_results(
        self, add_to_agent_results_request: "AddToAgentResultsRequest"
    ) -> "AddToAgentResultsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_get_agent_results(
        self,
        stream: "grpclib.server.Stream[GetAgentResultsRequest, GetAgentResultsResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_agent_results(request)
        await stream.send_message(response)

    async def __rpc_set_agent_result(
        self,
        stream: "grpclib.server.Stream[SetAgentResultRequest, SetAgentResultResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.set_agent_result(request)
        await stream.send_message(response)

    async def __rpc_set_agent_results(
        self,
        stream: "grpclib.server.Stream[SetAgentResultsRequest, SetAgentResultsResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.set_agent_results(request)
        await stream.send_message(response)

    async def __rpc_add_to_agent_result(
        self,
        stream: "grpclib.server.Stream[AddToAgentResultRequest, AddToAgentResultResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.add_to_agent_result(request)
        await stream.send_message(response)

    async def __rpc_add_to_agent_results(
        self,
        stream: "grpclib.server.Stream[AddToAgentResultsRequest, AddToAgentResultsResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.add_to_agent_results(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/umpire.agent.UmpireAgentService/GetAgentResults": grpclib.const.Handler(
                self.__rpc_get_agent_results,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetAgentResultsRequest,
                GetAgentResultsResponse,
            ),
            "/umpire.agent.UmpireAgentService/SetAgentResult": grpclib.const.Handler(
                self.__rpc_set_agent_result,
                grpclib.const.Cardinality.UNARY_UNARY,
                SetAgentResultRequest,
                SetAgentResultResponse,
            ),
            "/umpire.agent.UmpireAgentService/SetAgentResults": grpclib.const.Handler(
                self.__rpc_set_agent_results,
                grpclib.const.Cardinality.UNARY_UNARY,
                SetAgentResultsRequest,
                SetAgentResultsResponse,
            ),
            "/umpire.agent.UmpireAgentService/AddToAgentResult": grpclib.const.Handler(
                self.__rpc_add_to_agent_result,
                grpclib.const.Cardinality.UNARY_UNARY,
                AddToAgentResultRequest,
                AddToAgentResultResponse,
            ),
            "/umpire.agent.UmpireAgentService/AddToAgentResults": grpclib.const.Handler(
                self.__rpc_add_to_agent_results,
                grpclib.const.Cardinality.UNARY_UNARY,
                AddToAgentResultsRequest,
                AddToAgentResultsResponse,
            ),
        }
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: proto/evaluation.proto
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
class EvaluationResult(betterproto.Message):
    id: int = betterproto.int32_field(1)
    agent_id: int = betterproto.int32_field(2)
    metric: str = betterproto.string_field(3)
    result: int = betterproto.int64_field(4)
    created_at: str = betterproto.string_field(5)


@dataclass(eq=False, repr=False)
class GetCompetitionEvaluationResultsRequest(betterproto.Message):
    competition_tag: str = betterproto.string_field(1)


@dataclass(eq=False, repr=False)
class GetCompetitionEvaluationResultsResponse(betterproto.Message):
    results: List["EvaluationResult"] = betterproto.message_field(1)


@dataclass(eq=False, repr=False)
class SetEvaluationResultRequest(betterproto.Message):
    evaluation_id: int = betterproto.int32_field(1)
    agent_id: int = betterproto.int32_field(2)
    metric: str = betterproto.string_field(3)
    result: int = betterproto.int64_field(4)


@dataclass(eq=False, repr=False)
class SetEvaluationResultResponse(betterproto.Message):
    pass


class UmpireEvaluationServiceStub(betterproto.ServiceStub):
    async def get_competition_evaluation_results(
        self,
        get_competition_evaluation_results_request: "GetCompetitionEvaluationResultsRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "GetCompetitionEvaluationResultsResponse":
        return await self._unary_unary(
            "/umpire.evaluation.UmpireEvaluationService/GetCompetitionEvaluationResults",
            get_competition_evaluation_results_request,
            GetCompetitionEvaluationResultsResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )

    async def set_evaluation_result(
        self,
        set_evaluation_result_request: "SetEvaluationResultRequest",
        *,
        timeout: Optional[float] = None,
        deadline: Optional["Deadline"] = None,
        metadata: Optional["MetadataLike"] = None
    ) -> "SetEvaluationResultResponse":
        return await self._unary_unary(
            "/umpire.evaluation.UmpireEvaluationService/SetEvaluationResult",
            set_evaluation_result_request,
            SetEvaluationResultResponse,
            timeout=timeout,
            deadline=deadline,
            metadata=metadata,
        )


class UmpireEvaluationServiceBase(ServiceBase):
    async def get_competition_evaluation_results(
        self,
        get_competition_evaluation_results_request: "GetCompetitionEvaluationResultsRequest",
    ) -> "GetCompetitionEvaluationResultsResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def set_evaluation_result(
        self, set_evaluation_result_request: "SetEvaluationResultRequest"
    ) -> "SetEvaluationResultResponse":
        raise grpclib.GRPCError(grpclib.const.Status.UNIMPLEMENTED)

    async def __rpc_get_competition_evaluation_results(
        self,
        stream: "grpclib.server.Stream[GetCompetitionEvaluationResultsRequest, GetCompetitionEvaluationResultsResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.get_competition_evaluation_results(request)
        await stream.send_message(response)

    async def __rpc_set_evaluation_result(
        self,
        stream: "grpclib.server.Stream[SetEvaluationResultRequest, SetEvaluationResultResponse]",
    ) -> None:
        request = await stream.recv_message()
        response = await self.set_evaluation_result(request)
        await stream.send_message(response)

    def __mapping__(self) -> Dict[str, grpclib.const.Handler]:
        return {
            "/umpire.evaluation.UmpireEvaluationService/GetCompetitionEvaluationResults": grpclib.const.Handler(
                self.__rpc_get_competition_evaluation_results,
                grpclib.const.Cardinality.UNARY_UNARY,
                GetCompetitionEvaluationResultsRequest,
                GetCompetitionEvaluationResultsResponse,
            ),
            "/umpire.evaluation.UmpireEvaluationService/SetEvaluationResult": grpclib.const.Handler(
                self.__rpc_set_evaluation_result,
                grpclib.const.Cardinality.UNARY_UNARY,
                SetEvaluationResultRequest,
                SetEvaluationResultResponse,
            ),
        }

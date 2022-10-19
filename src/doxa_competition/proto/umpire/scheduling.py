# Generated by the protocol buffer compiler.  DO NOT EDIT!
# sources: proto/scheduling.proto
# plugin: python-betterproto
from dataclasses import dataclass
from typing import List

import betterproto
import grpclib


@dataclass
class EvaluationSubmission(betterproto.Message):
    # Agent participants (the same agent may appear multiple times)
    agent_ids: List[int] = betterproto.int32_field(1)
    metadata: str = betterproto.string_field(2)


@dataclass
class ScheduleEvaluationBatchRequest(betterproto.Message):
    competition_tag: str = betterproto.string_field(1)
    evaluations: List["EvaluationSubmission"] = betterproto.message_field(2)


@dataclass
class ScheduleEvaluationBatchResponse(betterproto.Message):
    batch_id: int = betterproto.int32_field(1)


@dataclass
class CompleteEvaluationRequest(betterproto.Message):
    evaluation_id: int = betterproto.int32_field(1)


@dataclass
class CompleteEvaluationResponse(betterproto.Message):
    pass


@dataclass
class RegisterDriverRequest(betterproto.Message):
    runtime_id: str = betterproto.string_field(1)
    competition_tag: str = betterproto.string_field(2)
    endpoint: str = betterproto.string_field(3)
    workers: int = betterproto.int32_field(4)


@dataclass
class RegisterDriverResponse(betterproto.Message):
    pass


@dataclass
class DeregisterDriverRequest(betterproto.Message):
    runtime_id: str = betterproto.string_field(1)


@dataclass
class DeregisterDriverResponse(betterproto.Message):
    pass


class UmpireSchedulingServiceStub(betterproto.ServiceStub):
    async def schedule_evaluation_batch(
        self,
        *,
        competition_tag: str = "",
        evaluations: List["EvaluationSubmission"] = [],
    ) -> ScheduleEvaluationBatchResponse:
        request = ScheduleEvaluationBatchRequest()
        request.competition_tag = competition_tag
        if evaluations is not None:
            request.evaluations = evaluations

        return await self._unary_unary(
            "/umpire.scheduling.UmpireSchedulingService/ScheduleEvaluationBatch",
            request,
            ScheduleEvaluationBatchResponse,
        )

    async def complete_evaluation(
        self, *, evaluation_id: int = 0
    ) -> CompleteEvaluationResponse:
        request = CompleteEvaluationRequest()
        request.evaluation_id = evaluation_id

        return await self._unary_unary(
            "/umpire.scheduling.UmpireSchedulingService/CompleteEvaluation",
            request,
            CompleteEvaluationResponse,
        )

    async def register_driver(
        self,
        *,
        runtime_id: str = "",
        competition_tag: str = "",
        endpoint: str = "",
        workers: int = 0,
    ) -> RegisterDriverResponse:
        request = RegisterDriverRequest()
        request.runtime_id = runtime_id
        request.competition_tag = competition_tag
        request.endpoint = endpoint
        request.workers = workers

        return await self._unary_unary(
            "/umpire.scheduling.UmpireSchedulingService/RegisterDriver",
            request,
            RegisterDriverResponse,
        )

    async def deregister_driver(
        self, *, runtime_id: str = ""
    ) -> DeregisterDriverResponse:
        request = DeregisterDriverRequest()
        request.runtime_id = runtime_id

        return await self._unary_unary(
            "/umpire.scheduling.UmpireSchedulingService/DeregisterDriver",
            request,
            DeregisterDriverResponse,
        )

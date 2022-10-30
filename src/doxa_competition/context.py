import json
from dataclasses import dataclass
from typing import List

import pulsar
from grpclib.client import Channel

from doxa_competition.proto.umpire.agent import (
    AddToAgentResultRequest,
    GetAgentResultsRequest,
    SetAgentResultRequest,
    UmpireAgentServiceStub,
)
from doxa_competition.proto.umpire.scheduling import (
    EvaluationSubmission,
    ScheduleEvaluationBatchRequest,
    UmpireSchedulingServiceStub,
)
from doxa_competition.proto.umpire.scoreboard import (
    GetCompetitionResultsRequest,
    UmpireScoreboardServiceStub,
)
from doxa_competition.utils import send_pulsar_message


@dataclass
class SchedulableEvaluation:
    agent_ids: List[int]
    metadata: dict


class CompetitionContext:
    competition_tag: str
    _pulsar_client: pulsar.Client
    _umpire_channel: Channel

    def __init__(
        self,
        competition_tag: str,
        pulsar_client: pulsar.Client,
        umpire_channel: Channel,
    ) -> None:
        self.competition_tag = competition_tag
        self._pulsar_client = pulsar_client
        self._umpire_channel = umpire_channel

    def emit_event(self, topic: str, body: dict, properties: dict = None) -> None:
        """Sends a Pulsar message.

        Args:
            topic (str): The topic.
            body (dict): The message body to be JSON-encoded.
            properties (dict, optional): Any additional optional properties. Defaults to None.
        """

        send_pulsar_message(
            client=self._pulsar_client,
            topic=f"persistent://public/default/{topic}",
            body=body,
            properties=properties,
        )

    def emit_competition_event(
        self, topic_name: str, body: dict, properties: dict = None
    ) -> None:
        """Emits a competition event.

        Args:
            topic_name (str): The competition topic name.
            body (dict): The message body to be JSON-encoded.
            properties (dict, optional): Any additional optional properties. Defaults to None.
        """

        send_pulsar_message(
            client=self._pulsar_client,
            topic=f"persistent://public/default/competition-{self.competition_tag}-{topic_name}",
            body=body,
            properties=properties if properties is not None else {},
        )

    async def schedule_evaluation(self, agent_ids: List[int], metadata: dict = None):
        return await self.schedule_evaluation_batch(
            [SchedulableEvaluation(agent_ids, metadata if metadata is not None else {})]
        )

    async def schedule_evaluation_batch(self, evaluations: List[SchedulableEvaluation]):
        return await UmpireSchedulingServiceStub(
            self._umpire_channel
        ).schedule_evaluation_batch(
            ScheduleEvaluationBatchRequest(
                competition_tag=self.competition_tag,
                evaluations=[
                    EvaluationSubmission(
                        evaluation.agent_ids, json.dumps(evaluation.metadata)
                    )
                    for evaluation in evaluations
                ],
            )
        )

    async def get_competition_results(self):
        return await UmpireScoreboardServiceStub(
            self._umpire_channel
        ).get_competition_results(GetCompetitionResultsRequest(self.competition_tag))

    async def get_agent_results(self, agent_id: int):
        return await UmpireAgentServiceStub(self._umpire_channel).get_agent_results(
            GetAgentResultsRequest(agent_id)
        )

    async def set_agent_result(self, agent_id: int, metric: str, result: int):
        return await UmpireAgentServiceStub(self._umpire_channel).set_agent_result(
            SetAgentResultRequest(agent_id, metric, result)
        )

    async def add_to_agent_result(self, agent_id: int, metric: str, result: int):
        return await UmpireAgentServiceStub(self._umpire_channel).add_to_agent_result(
            AddToAgentResultRequest(agent_id, metric, result)
        )

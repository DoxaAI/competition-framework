import json
import traceback
from datetime import datetime
from typing import List

import pulsar
from grpclib.client import Channel

from doxa_competition.events import EvaluationEvent
from doxa_competition.execution import Node
from doxa_competition.proto.umpire.agent import (
    GetAgentResultsRequest,
    SetAgentResultRequest,
    UmpireAgentServiceStub,
)
from doxa_competition.proto.umpire.scheduling import (
    CompleteEvaluationRequest,
    UmpireSchedulingServiceStub,
)
from doxa_competition.proto.umpire.scoreboard import (
    GetCompetitionResultsRequest,
    UmpireScoreboardServiceStub,
)
from doxa_competition.utils import send_pulsar_message


class EvaluationContext:
    """The evaluation context used in evaluation driver implementations."""

    id: int
    batch_id: int
    queued_at: datetime
    nodes: List[Node]
    extra: dict

    def __init__(
        self,
        id: int,
        batch_id: int,
        queued_at: datetime,
        participants: List[dict],
        extra: dict = None,
    ) -> None:
        self.id = id
        self.batch_id = batch_id
        self.queued_at = queued_at
        self.nodes = [
            Node(
                participant_index=participant["participant_index"],
                agent_id=participant["agent_id"],
                agent_metadata=participant["agent_metadata"],
                enrolment_id=participant["enrolment_id"],
                endpoint=participant["endpoint"],
                auth_token=participant["auth_token"],
            )
            for participant in participants
        ]
        self.extra = extra if extra is not None else {}

    async def fetch_agents(self) -> None:
        """Makes each node download its associated agent from the relevant storage node."""

        for node in self.nodes:
            await node.fetch_agent()

    async def release_nodes(self) -> None:
        """Releases Hearth nodes once evaluation terminates."""

        for node in self.nodes:
            await node.release()


class EvaluationDriver:
    """A base driver for evaluations to be extended by competition implementers."""

    competition_tag: str
    _pulsar_client: pulsar.Client
    _event_producer: pulsar.Producer
    _umpire_channel: Channel

    autofetch: bool = True
    autoshutdown: bool = True

    def __init__(
        self,
        competition_tag: str,
        pulsar_client: pulsar.Client,
    ) -> None:
        self.competition_tag = competition_tag
        self._pulsar_client = pulsar_client

        self._event_producer = self._pulsar_client.create_producer(
            f"persistent://public/default/competition-{self.competition_tag}-evaluation-events"
        )

    async def startup(self, umpire_channel: Channel):
        self._umpire_channel = umpire_channel

    async def handle(self, context: EvaluationContext) -> None:
        """Handles the evaluation process according to the specific competition
        once Hearth nodes are properly set up.

        Args:
            event (EvaluationEvent): The evaluation request event.
            context (EvaluationContext): The evaluation context giving access to the nodes.
        """

        raise NotImplementedError()

    def _make_context(self, event: EvaluationEvent) -> EvaluationContext:
        return EvaluationContext(
            id=event.evaluation_id,
            batch_id=event.batch_id,
            queued_at=datetime.fromisoformat(event.queued_at),
            participants=event.participants,
            extra=event.extra,
        )

    async def _handle(self, event: EvaluationEvent) -> None:
        """The internal handler for evaluation requests, running in a separate process.

        This wraps the handle() method to be provided by the competition implementer,
        abstracting away the process of requesting Hearth nodes, etc.

        Args:
            event (Event): The evaluation request event
        """

        # create the evaluation context
        self._context = self._make_context(event)

        # emit _START event
        self.emit_evaluation_event(event_type="_START", body={})

        if self.autofetch:
            # fetch agents from their respective storage nodes
            await self._context.fetch_agents()

        # call userland code to handle the evaluation
        try:
            await self.handle(self._context)
        except Exception as e:
            self.emit_evaluation_event(
                event_type="_ERROR",
                body={
                    "exception": {
                        "type": e.__class__.__name__,
                        "traceback": "".join(
                            traceback.format_exception(None, e, e.__traceback__)
                        ),
                    }
                },
            )

        if self.autoshutdown:
            # clean up Hearth node instances
            await self._context.release_nodes()

        # emit _END event
        self.emit_evaluation_event(event_type="_END", body={})

    def emit_evaluation_event(
        self, event_type: str, body: dict, properties: dict = None
    ) -> None:
        """Emits an evaluation event specific to the competition using
        the internal evaluation event producer available throughout the
        lifetime of the evaluation driver.

        Args:
            body (dict): The event body.
            properties (dict, optional): Any optional properties in addition. Defaults to {}.
        """

        self._event_producer.send(
            json.dumps(
                {
                    "evaluation_id": self._context.id,
                    "event_type": event_type,
                    "body": body,
                }
            ).encode("utf-8"),
            properties if properties is not None else {},
        )

    def emit_event(self, topic_name: str, body: dict, properties: dict = None) -> None:
        """Sends a Pulsar message. This should only be used for events other than
        evaluation events for which emit_evaluation_event() should be used.

        Args:
            topic_name (str): The topic name
            body (dict): _description_
            properties (dict, optional): _description_. Defaults to None.
        """

        send_pulsar_message(
            client=self._pulsar_client,
            topic=f"persistent://public/default/competition-{self.competition_tag}-{topic_name}",
            body=body,
            properties=properties if properties is not None else {},
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

    async def teardown(self) -> None:
        """Tears down the evaluation driver."""

        self._event_producer.close()

        try:
            await UmpireSchedulingServiceStub(self._umpire_channel).complete_evaluation(
                CompleteEvaluationRequest(evaluation_id=self._context.id)
            )
        finally:
            self._umpire_channel.close()

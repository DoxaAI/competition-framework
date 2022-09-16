import json
import queue
from datetime import datetime
from typing import Dict, List

import pulsar

from doxa_competition.events import EvaluationEvent
from doxa_competition.execution import Node
from doxa_competition.utils import send_pulsar_message


class EvaluationContext:
    """The evaluation context used in evaluation driver implementations."""

    id: int
    batch_id: int
    queued_at: datetime
    agents: List[str]
    nodes: Dict[str, Node]
    extra: dict

    def __init__(
        self,
        id: int,
        batch_id: int,
        queued_at: datetime,
        agents: List[str],
        nodes: Dict[str, Node],
        extra: dict = None,
    ) -> None:
        self.id = id
        self.batch_id = batch_id
        self.queued_at = queued_at
        self.agents = agents
        self.nodes = nodes
        self.extra = extra if extra is not None else {}

    def connect_to_nodes(self) -> None:
        """Connects to Hearth nodes required for the evaluation as set up by Umpire."""

        for node in self.nodes.values():
            node.connect()

    def release_nodes(self) -> None:
        """Releases Hearth nodes once evaluation terminates."""

        for node in self.nodes.values():
            node.release()


class EvaluationDriver:
    """A base driver for evaluations to be extended by competition implementers."""

    competition_tag: str
    _pulsar_client: pulsar.Client
    _event_producer: pulsar.Producer

    def __init__(self, competition_tag: str, pulsar_client: pulsar.Client) -> None:
        self.competition_tag = competition_tag
        self._pulsar_client = pulsar_client

        self._event_producer = self._pulsar_client.create_producer(
            f"persistent://public/default/competition-{self.competition_tag}-evaluation-events"
        )

    def handle(self, context: EvaluationContext) -> None:
        """Handles the evaluation process according to the specific competition
        once Hearth nodes are properly set up.

        Args:
            event (EvaluationEvent): The evaluation request event.
            context (EvaluationContext): The evaluation context giving access to the nodes.
        """

        raise NotImplementedError()

    def _make_context(self, event) -> EvaluationContext:
        return EvaluationContext(
            id=event.body["evaluation"]["id"],
            batch_id=event.body["evaluation"]["batch_id"],
            queued_at=datetime.fromisoformat(event.body["evaluation"]["queued_at"]),
            agents=event.body["evaluation"]["agents"],
            nodes={
                agent: Node(endpoint=node["endpoint"], auth_token=node["auth_token"])
                for agent, node in event.body["nodes"].items()
            },
            extra=event.body["evaluation"].get("extra", {}),
        )

    def _handle(self, event: EvaluationEvent) -> None:
        """The internal handler for evaluation requests, running in a separate process.

        This wraps the handle() method to be provided by the competition implementer,
        abstracting away the process of requesting Hearth nodes, etc.

        Args:
            event (Event): The evaluation request event
        """

        # create the evaluation context
        self._context = self._make_context(event)

        # connect to the Hearth nodes
        self._context.connect_to_nodes()

        # emit _START event
        self.emit_evaluation_event(event_type="_START", body={})

        # call userland code to handle the evaluation
        self.handle(self._context)

        # clean up Hearth node instances
        self._context.release_nodes()

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
                    body: body,
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

    def teardown(self) -> None:
        """Tears down the evaluation driver."""

        self._event_producer.close()

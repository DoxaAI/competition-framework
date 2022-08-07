import json
from typing import List, Type

import pulsar

from doxa_competition.event import Event
from doxa_competition.execution import EvaluationContext, Node
from doxa_competition.utils import make_pulsar_client, send_pulsar_message


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

    def handle(self, event: Event, context: EvaluationContext):
        """Handles the evaluation process according to the specific competition
        once Hearth nodes are properly set up.

        Args:
            event (Event): The evaluation request event
            context (EvaluationContext): The evaluation context giving access to the nodes.

        Raises:
            NotImplementedError: _description_
        """

        raise NotImplementedError()

    def _handle(self, event: Event):
        """The internal handler for evaluation requests, running in a separate process.

        This wraps the handle() method to be provided by the competition implementer,
        abstracting away the process of requesting Hearth nodes, etc.

        Args:
            event (Event): The evaluation request event
        """

        # TODO: Use the information contained with the event
        #       to request the creation of any number of Hearth nodes.
        #       Place code in `execution.py`.

        # TODO: Eventually, we may wish to support multiple bases.
        nodes = self._setup_nodes()

        context = EvaluationContext()  # TODO: create this context properly

        self.handle(event, context)

        # clean up Hearth node instances
        self._release_nodes(nodes)

    def _setup_nodes(self) -> List[Node]:
        """Sets up Hearth nodes as required to fulfil the requirements of the evaluation request.

        Returns:
            List[Node]: A list of newly initialised Hearth nodes.
        """

        # TODO: gRPC call(s) to setup Hearth nodes (eventually for some base and environment)

        return []

    def _release_nodes(self, nodes: List[Node]) -> None:
        """Releases Hearth nodes once evaluation terminates.

        Args:
            nodes (List[Node]): A list of Hearth nodes.
        """

        # TODO: gRPC call(s) to clean up used nodes

        pass

    def emit_evaluation_event(self, body: dict, properties: dict = None):
        """Emits an evaluation event specific to the competition using
        the internal evaluation event producer available throughout the
        lifetime of the evaluation driver.

        Args:
            body (dict): The event body.
            properties (dict, optional): Any optional properties in addition. Defaults to {}.
        """

        self._event_producer.send(
            json.dumps(body).encode("utf-8"),
            properties if properties is not None else {},
        )

    def emit_event(self, topic_name: str, body: dict, properties: dict = None):
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

    def teardown(self):
        self._event_producer.close()


def launch_driver(
    driver: Type[EvaluationDriver], competition_tag: str, event: Event
) -> None:
    """Launches a competition evaluation driver to process an evaluation.

    Args:
        driver (Type[EvaluationDriver]): The competition evaluation driver to launch.
        competition_tag (str): The competition tag.
        event (Event): The evaluation request event.
    """

    d = driver(
        competition_tag=competition_tag,
        pulsar_client=make_pulsar_client(),
    )

    d._handle(event)
    d.teardown()

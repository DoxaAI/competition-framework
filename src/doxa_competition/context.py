import pulsar

from doxa_competition.pool import EvaluationPool
from doxa_competition.utils import send_pulsar_message


class CompetitionContext:
    competition_tag: str
    _pulsar_client: pulsar.Client
    _pool: EvaluationPool

    def __init__(
        self, competition_tag: str, pulsar_client: pulsar.Client, pool: EvaluationPool
    ) -> None:
        self.competition_tag = competition_tag
        self._pulsar_client = pulsar_client
        self._pool = pool

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
        """Sends a competition event.

        Args:
            topic_name (str): The competition topic name.
            body (dict): The message body to be JSON-encoded.
            properties (dict, optional): Any additional optional properties. Defaults to None.
        """

        send_pulsar_message(
            client=self._pulsar_client,
            topic=f"persistent://public/default/competition-{self.competition_tag}-{topic_name}",
            body=body,
            properties=properties,
        )

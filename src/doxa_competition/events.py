from pulsar import MessageId

from doxa_competition.event import Event


class EvaluationEvent(Event):
    def __init__(self, body: dict) -> None:
        super().__init__(body, None, None)

        self.evaluation_id = body["id"]
        self.batch_id = body["batch_id"]
        self.queued_at = body["queued_at"]
        self.participants = body["participants"]
        self.extra = body.get("extra", {})


class PulsarEvent(Event):
    """A DOXA event generated via a Pulsar topic."""

    message_id: bytes

    def __init__(
        self, message_id: bytes, body: dict, properties: dict, timestamp: int
    ) -> None:
        self.message_id = message_id  # serialised as bytes so as to be picklable
        self.body = body
        self.properties = properties
        self.timestamp = timestamp

    def get_message_id(self) -> MessageId:
        """Deserialises message ID bytes into a Pulsar MessageId object.

        Returns:
            MessageId: The deserialised Pulsar MessageId object.
        """
        return MessageId.deserialize(self.message_id)


class AgentEvent(PulsarEvent):
    id: int
    tag: str
    enrolment_id: int
    upload_id: int
    created_at: str
    activated_at: str

    def __init__(
        self,
        message_id: bytes,
        body: dict,
        properties: dict = None,
        timestamp: int = None,
    ) -> None:
        super().__init__(message_id, body, properties, timestamp)

        self.agent_id = body["id"]
        self.agent_tag = body["tag"]
        self.enrolment_id = body["enrolment_id"]
        self.upload_id = body["upload_id"]
        self.created_at = body["created_at"]
        self.activated_at = body["activated_at"]

from typing import Callable, Dict

from pulsar import MessageId

from doxa_competition.context import CompetitionContext


class Event:
    """A DOXA event.

    Many event handlers may wish to wrap these event objects internally
    so as to be more useful to competition implementers.
    """

    body: dict
    properties: dict
    timestamp: int

    def __init__(
        self, body: dict, properties: dict = None, timestamp: int = None
    ) -> None:
        self.body = body
        self.properties = properties if properties is not None else {}
        self.timestamp = timestamp


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


TopicHandler = Callable[[Event], None]


class EventHandler:
    """A generic DOXA competition event handler."""

    context: CompetitionContext

    def get_context(self) -> CompetitionContext:
        """Returns the competition context.

        Returns:
            CompetitionContext: The competition context.
        """

        return self.context

    def set_context(self, context: CompetitionContext) -> None:
        """Sets the competition context.

        Args:
            context (CompetitionContext): The competition context.
        """

        self.context = context

    def extract_routes(self) -> Dict[str, TopicHandler]:
        """Extracts routes handled by the event handler.

        Concrete event handler implementations should return handled events
        and their respective topic handlers.

        Returns:
            Dict[str, TopicHandler]: The route mappings.
        """

        raise NotImplementedError()

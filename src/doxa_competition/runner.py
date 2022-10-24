import json
from typing import Dict

import pulsar
from _pulsar import ConsumerType
from grpclib.client import Channel

from doxa_competition.competition import Competition
from doxa_competition.context import CompetitionContext
from doxa_competition.event import Event, PulsarEvent
from doxa_competition.event_router import EventRouter
from doxa_competition.umpire import make_umpire_channel
from doxa_competition.utils import make_pulsar_client


class CompetitionRunner:
    """Handles the running of any number of registered competitions."""

    _competitions: Dict[str, Competition]
    _router: EventRouter
    _pulsar_client: pulsar.Client
    _umpire_channel: Channel

    def __init__(
        self,
        pulsar_path: str = None,
        umpire_host: str = "umpire",
        umpire_port: int = 80,
    ) -> None:
        self._router = EventRouter()
        self._pulsar_client = make_pulsar_client(pulsar_path=pulsar_path)
        self._umpire_channel = make_umpire_channel(host=umpire_host, port=umpire_port)
        self._competitions = {}

    def register(self, competition: Competition) -> None:
        """Registers a competition with the competition runner.

        Args:
            competition (Competition): The competition being registered.
        """

        tag = competition.get_tag()

        if tag in self._competitions:
            raise RuntimeError(f"The competition {tag} has already been registered.")

        # construct competition context
        context = CompetitionContext(tag, self._pulsar_client, self._umpire_channel)

        # register competition event handlers, e.g. the agent event handler,
        # the evaluation event handler or handlers related to extensions
        competition.register_event_handlers(self._router, context)

        self._competitions[tag] = competition

    def _setup(self) -> None:
        """Sets up the competition runner."""

        # TODO: registration with Umpire, declaring competitions
        # and their supported extensions

        pass

    def _get_event(self, message: pulsar.Message) -> Event:
        """Forms a DOXA competition service framework Event object
        from the received Pulsar message.

        Some event handlers may want to wrap this event before passing it
        onto user-implementable methods.

        Args:
            message (pulsar.Message): The received pulsar message.

        Returns:
            Event: An event to be handled.
        """
        return PulsarEvent(
            message_id=message.message_id().serialize(),
            body=json.loads(message.value()),
            properties=message.properties(),
            timestamp=message.publish_timestamp(),
        )

    async def run(self):
        """Subscribes to Pulsar topics corresponding to the registered event
        handlers and routes events accordingly."""

        self._setup()

        # start listening to the various Pulsar sources
        consumer = self._pulsar_client.subscribe(
            topic=self._router.get_topics(),
            subscription_name="competition-service",
            consumer_type=ConsumerType.Shared,
            schema=pulsar.schema.BytesSchema(),
        )

        try:
            while True:
                message = consumer.receive()
                consumer.acknowledge(message)

                try:
                    # remove the "persistent://public/default/" prefix
                    _, topic_name = message.topic_name().rsplit("/", 1)

                    # resolve the topic handler
                    topic_handler = self._router.resolve(topic_name)

                    # call the topic handler
                    await topic_handler(self._get_event(message))
                except KeyboardInterrupt:
                    break

                    # TODO: determine whether we should break or
                    # attempt to keep processing other events
                    # for other exceptions
        finally:
            self._pulsar_client.close()
            self._umpire_channel.close()

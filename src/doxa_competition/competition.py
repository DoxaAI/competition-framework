from typing import List

from doxa_competition.context import CompetitionContext
from doxa_competition.event.handler import EventHandler, Extension
from doxa_competition.event.handlers import AgentEventHandler, EvaluationEventHandler
from doxa_competition.event.router import EventRouter


class Competition:
    """The base class for competitions."""

    event_handlers: List[EventHandler]
    extensions: List[Extension]

    def __init__(
        self,
        agent_event_handler: AgentEventHandler,
        evaluation_event_handler: EvaluationEventHandler,
        extensions: List[Extension] = None,
    ) -> None:
        self.extensions = extensions if extensions else []
        self.event_handlers = [
            agent_event_handler,
            evaluation_event_handler,
        ] + self.extensions

    def get_tag(self) -> str:
        """Returns the identifying tag of the competition as registered with Umpire.

        Returns:
            str: The competition tag.
        """
        raise NotImplementedError()

    def get_extensions(self) -> List[str]:
        """Returns the extensions supported by the competiton.

        Returns:
            List[str]: A list of supported extensions' tags.
        """
        return []

    def register_event_handlers(self, router: EventRouter, context: CompetitionContext):
        """Registers an event handler for a competition.

        Args:
            router (EventRouter): The event router.
            context (CompetitionContext): The competition context.
        """

        tag = self.get_tag()

        for handler in self.event_handlers:
            handler.set_context(context)

            routes = handler.extract_routes()
            for topic, topic_handler in routes.items():
                router.add_route(f"competition-{tag}-{topic}", topic_handler)

from typing import Callable, Dict

from doxa_competition.context import CompetitionContext
from doxa_competition.event import Event

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


class Extension(EventHandler):
    """Competitions may implement "extensions" that allow competition services
    to handle additional events (either those emitted by the competition service
    itself or by other services in the DOXA ecosystem).

    Extensions must provide an identifying tag so that Umpire can track what
    extensions are currently supported.
    """

    def get_extension_name() -> str:
        """Returns the extension tag for identification with Umpire.

        Returns:
            str: The extension tag.
        """
        raise NotImplementedError()

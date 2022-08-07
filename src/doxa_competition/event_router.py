from typing import Dict, List, Pattern, Union

from doxa_competition.event import TopicHandler


class EventRouter:
    """Routes DOXA events to their respective registered handlers."""

    routes: Dict[str, TopicHandler]

    def __init__(self) -> None:
        self.routes = {}

    def add_route(self, topic: str, handler: TopicHandler) -> None:
        """Registers a new route.

        Args:
            topic (str): The topic to handle.
            handler (TopicHandler): The handler callable.

        Raises:
            ValueError: Topics cannot have multiple registered handlers.
        """

        if topic in self.routes:
            raise ValueError(
                f"The topic '{topic}' already has an associated topic handler."
            )

        self.routes[topic] = handler

    def resolve(self, topic: str) -> TopicHandler:
        """Resolves a topic to a callable.

        Args:
            topic (str): The topic to resolve (stripped of the "persistent://public/default/" prefix).

        Raises:
            RuntimeError: Raised when there is no handler for the topic.

        Returns:
            TopicHandler: The resolved handler.
        """
        if topic not in self.routes:
            raise RuntimeError(
                f"No route handler is registered for the topic '{topic}'."
            )

        return self.routes[topic]

    def get_topics(self) -> Union[List[str], Pattern]:
        """Returns a list of topics with registered handlers.

        Returns:
            Union[List[str], Pattern]: A list of topic names.
        """

        return list(self.routes.keys())

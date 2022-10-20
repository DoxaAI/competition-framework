from typing import Dict

from doxa_competition.event import AgentEvent, Event, EventHandler, TopicHandler


class AgentEventHandler(EventHandler):
    """A handler for agent activation and deactivation events."""

    async def on_activation(self, event: Event) -> None:
        """Handles agent activation events.

        Competition developers should implement this method.

        Args:
            event (Event): An activation event to be handled.
        """
        raise NotImplementedError()

    async def _on_activation(self, event: Event) -> None:
        """Handles agent activation events, as well as
        agent deactivations where a user already has an active agent.

        Args:
            event (Event): An activation event to be handled.
        """

        # TODO: update this to use the proper event format.

        assert "activating_agent" in event.body

        if "deactivating_agent" in event.body:
            await self.on_deactivation(
                AgentEvent(
                    event.message_id,
                    event.body["deactivating_agent"],
                    event.properties,
                    event.timestamp,
                )
            )

        await self.on_activation(
            AgentEvent(
                event.message_id,
                event.body["activating_agent"],
                event.properties,
                event.timestamp,
            )
        )

    async def _on_deactivation(self, event: Event) -> None:
        await self.on_deactivation(
            AgentEvent(
                event.message_id,
                event.body["deactivating_agent"],
                event.properties,
                event.timestamp,
            )
        )

    async def on_deactivation(self, event: Event) -> None:
        """Handles agent deactivation events.

        Competition developers should implement this method.

        Args:
            event (Event): a DOXA event to be handled
        """
        pass

    def extract_routes(self) -> Dict[str, TopicHandler]:
        return {
            "activation-events": self._on_activation,
            "deactivation-events": self._on_deactivation,
        }


class EvaluationEventHandler(EventHandler):
    """A handler for evaluation events."""

    async def handle(self, event: Event) -> None:
        """Handles (competition-specific) evaluation events.

        Competition developers should implement this method.

        Args:
            event (Event): A DOXA event to be handled.
        """
        raise NotImplementedError()

    def extract_routes(self) -> Dict[str, TopicHandler]:
        return {"evaluation-events": self.handle}

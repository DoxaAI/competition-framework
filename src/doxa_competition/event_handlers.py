from typing import Dict

from doxa_competition.event import Event, EventHandler, PulsarEvent, TopicHandler


class AgentEventHandler(EventHandler):
    """A handler for agent activation and deactivation events."""

    def on_activation(self, event: Event) -> None:
        """Handles agent activation events.

        Competition developers should implement this method.

        Args:
            event (Event): An activation event to be handled.
        """
        raise NotImplementedError()

    def _on_activation(self, event: Event) -> None:
        """Handles agent activation events, as well as
        agent deactivations where a user already has an active agent.

        Args:
            event (Event): An activation event to be handled.
        """

        # TODO: update this to use the proper event format.

        assert "activate_agent" in event.body

        if "deactivate_agent" in event.body:
            self.on_deactivation(
                PulsarEvent(  # TODO: we may want to wrap this Event
                    event.message_id,
                    event.body["deactivate_agent"],
                    event.properties,
                    event.timestamp,
                )
            )

        self.on_activation(
            PulsarEvent(
                event.message_id,
                event.body["activate_agent"],
                event.properties,
                event.timestamp,
            )
        )  # TODO: we may want to wrap this event too

    def on_deactivation(self, event: Event) -> None:
        """Handles agent deactivation events.

        Competition developers should implement this method.

        Args:
            event (Event): a DOXA event to be handled
        """
        raise NotImplementedError()

    def submit_evaluation_request(self, body: dict, properties: dict = None):
        """Submits an evaluation request to Umpire.

        Args:
            body (dict): The event body.
            properties (dict, optional): Additional event properties. Defaults to None.
        """

        self.context.emit_competition_event(
            "evaluation-requests",
            body,
            properties,
        )

    def extract_routes(self) -> Dict[str, TopicHandler]:
        return {
            "activation-events": self._on_activation,
            "deactivation-events": self.on_deactivation,
        }


class EvaluationEventHandler(EventHandler):
    """A handler for evaluation events."""

    def handle(self, event: Event) -> None:
        """Handles (competition-specific) evaluation events.

        Competition developers should implement this method.

        Args:
            event (Event): A DOXA event to be handled.
        """
        raise NotImplementedError()

    def extract_routes(self) -> Dict[str, TopicHandler]:
        return {"evaluation-events": self.handle}

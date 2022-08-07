import multiprocessing
from typing import Dict, Type

from doxa_competition.evaluation import EvaluationDriver, launch_driver
from doxa_competition.event import Event, EventHandler, TopicHandler


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
                Event(  # TODO: we may want to wrap this Event
                    event.message_id,
                    event.body["deactivate_agent"],
                    event.properties,
                    event.timestamp,
                )
            )

        self.on_activation(
            Event(
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


class EvaluationRequestOutcomeHandler(EventHandler):
    """An event handler for evaluation request outcomes.

    Competition services emit evaluation requests, which get granted or refused by Umpire.
    """

    def __init__(self, competition_tag: str, driver: Type[EvaluationDriver]) -> None:
        super().__init__()

        self.competition_tag = competition_tag
        self.driver = driver

    def on_grant(self, event: Event) -> None:
        """Launches the evaluation process by submitting the evaluation
        to a process pool after Umpire grants the evaluation request.

        Args:
            event (Event): The evaluation request approval event.
        """
        self.context._pool.submit(
            function=launch_driver, args=(self.driver, self.competition_tag, event)
        )

    def on_refusal(self, event: Event) -> None:
        """Handles evaluation request refusals.

        Evaluation requests may be refused, for example, if a competition
        has reached its allocated compute quota.

        Args:
            event (Event): The evaluation request refusal event.
        """
        pass

    def extract_routes(self) -> Dict[str, TopicHandler]:
        return {
            "evaluation-request-grants": self.on_grant,
            "evaluation-request-refusals": self.on_refusal,
        }

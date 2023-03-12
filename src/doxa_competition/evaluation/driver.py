import asyncio
import json
import traceback
from datetime import datetime
from typing import Dict

import pulsar
from grpclib.client import Channel

from doxa_competition.context import CompetitionContext
from doxa_competition.evaluation.context import EvaluationContext
from doxa_competition.evaluation.errors import AgentError, AgentTimeoutError
from doxa_competition.events import EvaluationEvent
from doxa_competition.proto.umpire.scheduling import (
    CompleteEvaluationRequest,
    UmpireSchedulingServiceStub,
)


class EvaluationDriver(CompetitionContext):
    """A base driver for evaluations to be extended by competition implementers."""

    competition_tag: str
    _pulsar_client: pulsar.Client
    _event_producer: pulsar.Producer
    _umpire_channel: Channel

    autofetch: bool = True
    autoshutdown: bool = True

    timeouts: Dict[str, float] = {}

    def __init__(
        self,
        competition_tag: str,
        pulsar_client: pulsar.Client,
    ) -> None:
        self.competition_tag = competition_tag
        self._pulsar_client = pulsar_client

        self._event_producer = self._pulsar_client.create_producer(
            f"persistent://public/default/competition-{self.competition_tag}-evaluation-events"
        )

    async def startup(self, umpire_channel: Channel):
        self._umpire_channel = umpire_channel

    async def handle(self, context: EvaluationContext) -> None:
        """Handles the evaluation process according to the specific competition
        once Hearth nodes are properly set up.

        Args:
            event (EvaluationEvent): The evaluation request event.
            context (EvaluationContext): The evaluation context giving access to the nodes.
        """

        raise NotImplementedError

    def _make_evaluation_context(self, event: EvaluationEvent) -> EvaluationContext:
        return EvaluationContext(
            id=event.evaluation_id,
            batch_id=event.batch_id,
            queued_at=datetime.fromisoformat(event.queued_at),
            participants=event.participants,
            extra=event.extra,
            timeouts=self.timeouts,
        )

    def _handle_error(
        self, exception: Exception, error_type: str = None, extra: dict = None
    ) -> None:
        event_type = "_ERROR"
        if error_type:
            event_type += f"_{error_type.upper()}"

        body = extra if extra else {}

        try:
            self.emit_evaluation_event(
                event_type=event_type,
                body={
                    **body,
                    "exception": {
                        "type": exception.__class__.__name__,
                        "message": str(exception),
                        "traceback": "".join(
                            traceback.format_exception(
                                None, exception, exception.__traceback__
                            )
                        ),
                    },
                },
            )
        except:
            print(
                f"Unable to gracefully handle an Exception of type {exception.__class__.__name__}."
            )

    async def _handle_agent_error(self, error: AgentError):
        if error.participant_index is None:
            if len(self._context.nodes) > 1:
                self._handle_error(
                    error,
                    error_type="AGENT_UNKNOWN",
                    extra={},
                )
                return

            error.participant_index = 0

        node = self._context.nodes[error.participant_index]

        try:
            self._handle_error(
                error,
                error_type="AGENT",
                extra={
                    "agent_id": node.agent_id,
                    "enrolment_id": node.enrolment_id,
                    "participant_index": node.participant_index,
                    "stderr": await node.read_stderr_all(
                        error_on_failure=True, line_limit=50
                    ),
                },
            )
        except:
            self._handle_error(
                error,
                error_type="AGENT",
                extra={
                    "agent_id": node.agent_id,
                    "enrolment_id": node.enrolment_id,
                    "participant_index": node.participant_index,
                },
            )

    def _handle_agent_timeout_error(self, error: Exception) -> None:
        extra = {}
        if len(self._context.nodes) == 1:
            node = self._context.nodes[0]
            extra = {
                "agent_id": node.agent_id,
                "enrolment_id": node.enrolment_id,
                "participant_index": node.participant_index,
            }

        self._handle_error(error, error_type="AGENT_TIMEOUT", extra=extra)

    async def _handle(self, event: EvaluationEvent) -> None:
        """The internal handler for evaluation requests, running in a separate process.

        This wraps the handle() method to be provided by the competition implementer,
        abstracting away the process of requesting Hearth nodes, etc.

        Args:
            event (Event): The evaluation request event
        """

        # create the evaluation context
        self._context = self._make_evaluation_context(event)

        # emit _START event
        self.emit_evaluation_event(event_type="_START", body={})

        if self.autofetch:
            # fetch agents from their respective storage nodes
            await self._context.fetch_agents()

        # call userland code to handle the evaluation
        try:
            await self.handle(self._context)
        except asyncio.TimeoutError as e:
            self._handle_agent_timeout_error(e)
        except AgentTimeoutError as e:
            self._handle_agent_timeout_error(e)
        except AgentError as e:
            await self._handle_agent_error(e)
        except Exception as e:
            self._handle_error(e)

        # emit _END event
        self.emit_evaluation_event(event_type="_END", body={})

    def emit_evaluation_event(
        self, event_type: str, body: dict, properties: dict = None
    ) -> None:
        """Emits an evaluation event specific to the competition using
        the internal evaluation event producer available throughout the
        lifetime of the evaluation driver.

        Args:
            body (dict): The event body.
            properties (dict, optional): Any optional properties in addition. Defaults to {}.
        """

        self._event_producer.send(
            json.dumps(
                {
                    "evaluation_id": self._context.id,
                    "event_type": event_type,
                    "body": body,
                }
            ).encode("utf-8"),
            properties if properties is not None else {},
        )

    async def set_result(self, agent_id: int, metric: str, result: int):
        return await self.set_evaluation_result(
            self._context.id, agent_id, metric, result
        )

    async def teardown(self) -> None:
        """Tears down the evaluation driver."""

        if self.autoshutdown:
            # clean up Hearth node instances
            await self._context.release_nodes()

        try:
            self._event_producer.close()
        except:
            print("[ERROR] Unable to close event producer.")

        try:
            await UmpireSchedulingServiceStub(self._umpire_channel).complete_evaluation(
                CompleteEvaluationRequest(evaluation_id=self._context.id)
            )
        except Exception as e:
            print(
                f"[ERROR] An error occurred while notifying Umpire of the completion of evaluation {self._context.id}: {str(e)}"
            )
        finally:
            self._umpire_channel.close()

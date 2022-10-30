import asyncio
import json
import traceback
from datetime import datetime

import pulsar
from doxa_competition.context import CompetitionContext
from doxa_competition.evaluation.context import EvaluationContext
from doxa_competition.evaluation.errors import AgentError
from doxa_competition.events import EvaluationEvent
from doxa_competition.proto.umpire.scheduling import (
    CompleteEvaluationRequest,
    UmpireSchedulingServiceStub,
)
from grpclib.client import Channel


class EvaluationDriver(CompetitionContext):
    """A base driver for evaluations to be extended by competition implementers."""

    competition_tag: str
    _pulsar_client: pulsar.Client
    _event_producer: pulsar.Producer
    _umpire_channel: Channel

    autofetch: bool = True
    autoshutdown: bool = True

    # gRPC request timeout
    timeout: float = 10 * 60

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

        raise NotImplementedError()

    def _make_evaluation_context(self, event: EvaluationEvent) -> EvaluationContext:
        return EvaluationContext(
            id=event.evaluation_id,
            batch_id=event.batch_id,
            queued_at=datetime.fromisoformat(event.queued_at),
            participants=event.participants,
            extra=event.extra,
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
        node = next(
            (node for node in self._context.nodes if node.agent_id == error.agent_id),
            None,
        )
        try:
            if not node:
                raise RuntimeError("Oops, a node has disappeared!")

            self._handle_error(
                error,
                error_type="AGENT",
                extra={
                    "agent_id": error.agent_id,
                    "stderr": await node.read_stderr_all(),
                },
            )
        except:
            self._handle_error(
                error, error_type="AGENT", extra={"agent_id": error.agent_id}
            )

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
            self._handle_error(e, error_type="AGENT_TIMEOUT")
        except AgentError as e:
            await self._handle_agent_error(e)
        except Exception as e:
            self._handle_error(e)

        if self.autoshutdown:
            # clean up Hearth node instances
            await self._context.release_nodes()

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

    async def teardown(self) -> None:
        """Tears down the evaluation driver."""

        try:
            self._event_producer.close()
        except:
            print("Unable to close event producer.")

        try:
            await UmpireSchedulingServiceStub(self._umpire_channel).complete_evaluation(
                CompleteEvaluationRequest(evaluation_id=self._context.id)
            )
        finally:
            self._umpire_channel.close()

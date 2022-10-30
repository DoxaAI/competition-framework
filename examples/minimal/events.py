from doxa_competition.competition import Competition
from doxa_competition.event import Event
from doxa_competition.event.handlers import AgentEventHandler, EvaluationEventHandler
from doxa_competition.events import AgentEvent


class MinimalAgentEventHandler(AgentEventHandler):
    async def on_activation(self, event: AgentEvent) -> None:
        await self.context.schedule_evaluation([event.agent_id])

    async def on_deactivation(self, event: Event) -> None:
        pass


class MinimalEvaluationEventHandler(EvaluationEventHandler):
    async def handle(self, event: Event) -> None:
        pass


class MinimalCompetition(Competition):
    def __init__(self) -> None:
        super().__init__(
            agent_event_handler=MinimalAgentEventHandler(),
            evaluation_event_handler=MinimalEvaluationEventHandler(),
        )

    def get_tag(self) -> str:
        return "minimal"

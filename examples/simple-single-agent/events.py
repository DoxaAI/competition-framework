from doxa_competition.competition import Competition
from doxa_competition.event.handlers import (
    ApatheticEvaluationEventHandler,
    SimpleAgentEventHandler,
)


class SimpleSingleAgentCompetition(Competition):
    def __init__(self) -> None:
        super().__init__(
            agent_event_handler=SimpleAgentEventHandler(),
            evaluation_event_handler=ApatheticEvaluationEventHandler(),
        )

    def get_tag(self) -> str:
        return "simple-single-agent"

from typing import Optional


class AgentError(Exception):
    def __init__(
        self,
        message: str,
        participant: int = Optional[None],
        agent_id: int = Optional[None],
        *args: object,
    ) -> None:
        super().__init__(message, *args)
        self.participant_index = participant
        self.agent_id = agent_id

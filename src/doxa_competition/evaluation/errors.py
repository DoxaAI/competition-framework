from typing import Optional


class AgentError(Exception):
    def __init__(
        self,
        message: str,
        participant: int = Optional[None],
        *args: object,
    ) -> None:
        super().__init__(message, *args)
        self.participant_index = participant


class AgentTimeoutError(AgentError):
    def __init__(
        self,
        message: str = "Agent timed out.",
        participant: int = Optional[None],
        *args: object,
    ) -> None:
        super().__init__(message, participant, *args)

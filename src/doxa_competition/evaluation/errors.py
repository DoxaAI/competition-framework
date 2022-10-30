class AgentError(Exception):
    def __init__(
        self,
        message: str,
        agent_id: int = None,
        *args: object,
    ) -> None:
        super().__init__(message, *args)
        self.agent_id = agent_id

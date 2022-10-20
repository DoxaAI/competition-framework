class Node:
    """The DOXA Competition Framework representation of a Hearth node."""

    participant_index: int
    agent_id: int
    endpoint: str
    auth_token: str

    def __init__(
        self, participant_index: int, agent_id: int, endpoint: str, auth_token: str
    ) -> None:
        self.participant_index = participant_index
        self.agent_id = agent_id
        self.endpoint = endpoint
        self.auth_token = auth_token

    def connect(self):
        # TODO: gRPC call to connect to the node
        pass

    def download_agent(self):
        pass

    def spawn_application(self):
        # TODO: implement spawning an application
        pass

    def release(self):
        # TODO: gRPC call to release the node
        pass

    # TODO: implement getting files
    # TODO: handle reading from and writing to stdio (possibly implemented as a generator!)

class Node:
    """The DOXA Competition Framework representation of a Hearth node."""

    endpoint: str
    auth_token: str

    def __init__(self, endpoint: str, auth_token: str) -> None:
        self.endpoint = endpoint
        self.auth_token = auth_token

    def connect(self):
        # TODO: gRPC call to connect to the node
        pass

    def spawn_application(self):
        # TODO: implement spawning an application
        pass

    def release(self):
        # TODO: gRPC call to release the node
        pass

    # TODO: implement getting files
    # TODO: handle reading from and writing to stdio (possibly implemented as a generator!)

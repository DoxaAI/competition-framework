class Event:
    """A DOXA event.

    Many event handlers may wish to wrap these event objects internally
    so as to be more useful to competition implementers.
    """

    body: dict
    properties: dict
    timestamp: int

    def __init__(
        self, body: dict, properties: dict = None, timestamp: int = None
    ) -> None:
        self.body = body
        self.properties = properties if properties is not None else {}
        self.timestamp = timestamp

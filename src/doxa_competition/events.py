from doxa_competition.event import Event


class EvaluationEvent(Event):
    def __init__(self, body: dict) -> None:
        super().__init__(body, None, None)

        self.evaluation_id = body["id"]
        self.batch_id = body["batch_id"]
        self.queued_at = body["queued_at"]
        self.participants = body["participants"]
        self.extra = body.get("extra", {})

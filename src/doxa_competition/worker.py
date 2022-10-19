from datetime import datetime
from pydoc import locate
from uuid import uuid4

import click
from sanic import Sanic
from sanic.request import Request
from sanic.response import json

from doxa_competition.evaluation import EvaluationDriver
from doxa_competition.events import EvaluationEvent
from doxa_competition.utils import make_pulsar_client


def make_evaluation_event(request: Request) -> EvaluationEvent:
    """Validates and creates an evaluation event from the evaluation request.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        EvaluationEvent: The resulting event.
    """

    # {
    #     "id": ...,
    #     "batch_id": ...,
    #     "queued_at": ...,
    #     "participants": [{
    #         "participant_index": ...,
    #         "agent_id": ...,
    #         "endpoint": ...,
    #         "auth_token": ...,
    #     }, ...],
    # }

    assert "id" in request.json
    assert "batch_id" in request.json
    assert "queued_at" in request.json
    assert "participants" in request.json
    assert isinstance(request.json["participants"], list)
    assert len(request.json["participants"]) > 0

    for participant in request.json["participants"]:
        assert isinstance(participant, dict)
        assert "participant_index" in participant
        assert "agent_id" in participant
        assert "endpoint" in participant
        assert "auth_token" in participant

    return EvaluationEvent(body=request.json)


async def process_evaluation(driver: EvaluationDriver, event: EvaluationEvent):
    driver._handle(event)
    driver.teardown()


@click.command()
@click.option(
    "--competition_tag", "-t", type=str, required=True, help="The competition tag."
)
@click.option(
    "--driver",
    "-d",
    type=str,
    required=True,
    help="The fully qualified class name of the competition driver.",
)
@click.option("--host", "-h", type=str, default="0.0.0.0", help="The host to bind to.")
@click.option("--port", "-p", type=int, default=8000, help="The port to run on.")
@click.option(
    "--workers", "-w", type=int, default=4, help="Number of worker processes."
)
def competition_worker(
    competition_tag: str, driver: str, host: str, port: int, workers: int
):
    """A CLI tool for spinning up DOXA competition driver worker instances."""

    driver_uuid = uuid4()
    start_time = datetime.now()

    Driver: EvaluationDriver = locate(driver)

    app = Sanic("doxa-competition-worker")

    app.ctx.pulsar_client = make_pulsar_client()

    # TODO: register with Umpire

    @app.get("/status")
    async def status_handler(request: Request):
        return json(
            {
                "uuid": str(driver_uuid),
                "competitions": [competition_tag],
                "started_at": start_time.isoformat(),
                "workers": workers,
            }
        )

    @app.post("/evaluation")
    async def evaluation_handler(request: Request):
        try:
            event = make_evaluation_event(request)
        except:
            return json({"success": False})

        request.app.add_task(
            process_evaluation(
                driver=Driver(competition_tag, request.app.ctx.pulsar_client),
                event=event,
            )
        )

        return json({"success": True})

    app.run(host=host, port=port, workers=workers, access_log=False)


if __name__ == "__main__":
    competition_worker()

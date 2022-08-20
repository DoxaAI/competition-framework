from pydoc import locate

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

    assert "evaluation" in request.json
    assert "id" in request.json["evaluation"]
    assert "batch_id" in request.json["evaluation"]
    assert "queued_at" in request.json["evaluation"]
    assert "agents" in request.json["evaluation"]
    assert isinstance(request.json["evaluation"]["agents"], list)
    assert len(request.json["evaluation"]["agents"]) > 0

    assert "nodes" in request.json
    for agent_tag in request.json["evaluation"]["agents"]:
        assert agent_tag in request.json["nodes"]
        assert "endpoint" in request.json["nodes"][agent_tag]
        assert "auth_token" in request.json["nodes"][agent_tag]

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

    Driver: EvaluationDriver = locate(driver)

    app = Sanic("doxa-competition-worker")

    app.ctx.pulsar_client = make_pulsar_client()

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

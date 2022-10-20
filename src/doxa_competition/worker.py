from datetime import datetime
from pydoc import locate
from uuid import uuid4

import click
from sanic import Sanic
from sanic.log import logger
from sanic.request import Request
from sanic.response import json

from doxa_competition.evaluation import EvaluationDriver
from doxa_competition.events import EvaluationEvent
from doxa_competition.proto.umpire.scheduling import UmpireSchedulingServiceStub
from doxa_competition.umpire import make_umpire_channel
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


async def process_evaluation(
    driver: EvaluationDriver, event: EvaluationEvent, umpire_channel_connection: dict
):
    await driver.startup(make_umpire_channel(**umpire_channel_connection))
    await driver._handle(event)
    await driver.teardown()


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
    "--endpoint",
    "-e",
    type=str,
    default=None,
    help="The endpoint with which to register with Umpire if it cannot be formed from the host and port.",
)
@click.option(
    "--workers", "-w", type=int, default=4, help="Number of worker processes."
)
@click.option(
    "--pulsar-path",
    type=str,
    default="pulsar://pulsar:6650",
    help="The path to a running Pulsar instance.",
)
@click.option(
    "--umpire-host",
    type=str,
    default="umpire",
    help="The host on which Umpire is running.",
)
@click.option(
    "--umpire-port", type=int, default=80, help="The port on which Umpire is running."
)
def competition_worker(
    competition_tag: str,
    driver: str,
    host: str,
    port: int,
    endpoint: str,
    workers: int,
    pulsar_path: str,
    umpire_host: str,
    umpire_port: int,
):
    """A CLI tool for spinning up DOXA competition driver worker instances."""

    driver_uuid = uuid4()
    start_time = datetime.now()
    driver_endpoint = endpoint if endpoint is not None else f"http://{host}:{port}/"

    Driver: EvaluationDriver = locate(driver)

    app = Sanic("doxa-competition-worker")
    app.ctx.pulsar_client = make_pulsar_client(pulsar_path=pulsar_path)
    app.ctx.umpire_channel_connection = {"host": umpire_host, "port": umpire_port}

    logger.info(f"Driver {str(driver_uuid)} is starting with {workers} workers.")

    @app.main_process_start
    async def startup_handler(app, loop):
        app.ctx.umpire_channel = make_umpire_channel(host=umpire_host, port=umpire_port)
        app.ctx.umpire_scheduling = UmpireSchedulingServiceStub(app.ctx.umpire_channel)
        await app.ctx.umpire_scheduling.register_driver(
            runtime_id=str(driver_uuid),
            competition_tag=competition_tag,
            endpoint=driver_endpoint,
            workers=workers,
        )
        logger.info("Registered with Umpire.")

    @app.main_process_stop
    async def shutdown_handler(app, loop):
        try:
            await app.ctx.umpire_scheduling.deregister_driver(
                runtime_id=str(driver_uuid),
            )
            logger.info("Successfully deregistered from Umpire.")
        except:
            logger.error("Failed to deregister from Umpire.")

        app.ctx.umpire_channel.close()

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

        logger.info(f"Handling evaluation {event.evaluation_id}")
        request.app.add_task(
            process_evaluation(
                driver=Driver(
                    competition_tag,
                    request.app.ctx.pulsar_client,
                ),
                event=event,
                umpire_channel_connection=app.ctx.umpire_channel_connection,
            )
        )

        return json({"success": True})

    app.run(host=host, port=port, workers=workers, access_log=False)


if __name__ == "__main__":
    competition_worker()

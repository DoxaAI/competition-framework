from datetime import datetime
from uuid import uuid4

from doxa_competition.evaluation import EvaluationDriver
from doxa_competition.events import EvaluationEvent
from doxa_competition.proto.umpire.scheduling import (
    DeregisterDriverRequest,
    RegisterDriverRequest,
    UmpireSchedulingServiceStub,
)
from doxa_competition.utils import make_pulsar_client, make_umpire_channel
from sanic import Sanic
from sanic.log import logger
from sanic.request import Request
from sanic.response import json


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
    #         "agent_metadata": {...},
    #         "enrolment_id": ...,
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
        assert "agent_metadata" in participant
        assert isinstance(participant["agent_metadata"], dict)
        assert "enrolment_id" in participant
        assert "endpoint" in participant
        assert "storage_endpoint" in participant
        assert "upload_id" in participant
        assert "auth_token" in participant

    return EvaluationEvent(body=request.json)


async def process_evaluation(
    driver: EvaluationDriver, event: EvaluationEvent, umpire_channel_connection: dict
):
    try:
        await driver.startup(make_umpire_channel(**umpire_channel_connection))
        await driver._handle(event)
    except Exception as e:
        driver._handle_error(e, "INTERNAL")
    finally:
        await driver.teardown()


def make_server(
    competition_tag: str,
    driver_endpoint: str,
    Driver: EvaluationDriver,
    workers: int,
    pulsar_path: str,
    umpire_host: str,
    umpire_port: int,
):
    driver_uuid = uuid4()
    start_time = datetime.now()

    app = Sanic("doxa-competition-worker")
    app.ctx.pulsar_client = make_pulsar_client(pulsar_path=pulsar_path)
    app.ctx.umpire_channel_connection = {"host": umpire_host, "port": umpire_port}

    logger.info(f"Driver {str(driver_uuid)} is starting with {workers} workers.")

    @app.main_process_start
    async def startup_handler(app, loop):
        app.ctx.umpire_channel = make_umpire_channel(host=umpire_host, port=umpire_port)
        app.ctx.umpire_scheduling = UmpireSchedulingServiceStub(app.ctx.umpire_channel)
        await app.ctx.umpire_scheduling.register_driver(
            RegisterDriverRequest(
                runtime_id=str(driver_uuid),
                competition_tag=competition_tag,
                endpoint=driver_endpoint,
                workers=workers,
            )
        )
        logger.info("Registered with Umpire.")

    @app.main_process_stop
    async def shutdown_handler(app, loop):
        try:
            await app.ctx.umpire_scheduling.deregister_driver(
                DeregisterDriverRequest(
                    runtime_id=str(driver_uuid),
                )
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
            return json({"success": False}, status=400)

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

    return app

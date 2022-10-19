from grpclib.client import Channel

from doxa_competition.proto.umpire.scheduling import UmpireSchedulingServiceStub


async def make_umpire_scheduling_service(
    host: str = "umpire", port: int = 80
) -> UmpireSchedulingServiceStub:
    return UmpireSchedulingServiceStub(Channel(host=host, port=port))

from grpclib.client import Channel


def make_umpire_channel(host: str = "umpire", port: int = 80) -> Channel:
    return Channel(host=host, port=port)

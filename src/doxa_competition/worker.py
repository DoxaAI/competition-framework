from pydoc import locate

import click

from doxa_competition.evaluation.server import make_server


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
def serve(
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

    driver_endpoint = endpoint if endpoint is not None else f"http://{host}:{port}/"

    Driver = locate(driver)

    if Driver is None:
        raise RuntimeError("The driver class {driver} cannot be found.")

    app = make_server(
        competition_tag=competition_tag,
        driver_endpoint=driver_endpoint,
        Driver=Driver,
        workers=workers,
        pulsar_path=pulsar_path,
        umpire_host=umpire_host,
        umpire_port=umpire_port,
    )

    app.run(host=host, port=port, workers=workers, access_log=False)


if __name__ == "__main__":
    serve()

import json
import logging
import os

import pulsar

PULSAR_PATH = "pulsar://pulsar:6650"


def make_pulsar_client(pulsar_path: str = None) -> pulsar.Client:
    """Creates a new Pulsar client instance.

    In development, it may be helpful to modify the DOXA_PULSAR_PATH
    environment variable instead of relying on Kubernetes auto-discovery
    as in the DOXA production environment.

    Returns:
        pulsar.Client: The instantiated Pulsar client object.
    """

    # TODO: We should probably have a proper logger instance for the Pulsar client.
    #       It produces so many superfluous messages, this is temporary code for
    #       keeping them to a minimum.

    return pulsar.Client(
        pulsar_path
        if pulsar_path is not None
        else os.environ.get("DOXA_PULSAR_PATH", PULSAR_PATH),
        logger=logging.Logger(name="pulsar_client_logger", level=0),
    )


def send_pulsar_message(
    client: pulsar.Client, topic: str, body: dict, properties: dict
) -> None:
    """Sends a pulsar message for a given topic.

    Args:
        client (pulsar.Client): The Pulsar client.
        topic (str): The full topic name.
        body (dict): The JSON message to be encoded.
        properties (dict): Any additional message properties.
    """

    producer = client.create_producer(topic)
    producer.send(json.dumps(body).encode("utf-8"), properties)
    producer.close()


def is_valid_filename(filename: str) -> bool:
    return bool(
        filename
        and filename.isprintable()
        and not any(
            character in filename
            for character in ["/", "<", ">", ":", '"', "\\", "|", "?", "*"]
        )
    )

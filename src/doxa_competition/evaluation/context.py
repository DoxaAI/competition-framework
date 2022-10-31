from datetime import datetime
from typing import List

from doxa_competition.evaluation.node import Node


class EvaluationContext:
    """The evaluation context used in evaluation driver implementations."""

    id: int
    batch_id: int
    queued_at: datetime
    nodes: List[Node]
    extra: dict

    def __init__(
        self,
        id: int,
        batch_id: int,
        queued_at: datetime,
        participants: List[dict],
        extra: dict = None,
        timeout: float = None,
    ) -> None:
        self.id = id
        self.batch_id = batch_id
        self.queued_at = queued_at
        self.nodes = [
            Node(
                participant_index=participant["participant_index"],
                agent_id=participant["agent_id"],
                agent_metadata=participant["agent_metadata"],
                enrolment_id=participant["enrolment_id"],
                endpoint=participant["endpoint"],
                storage_endpoint=participant["storage_endpoint"],
                upload_id=participant["upload_id"],
                auth_token=participant["auth_token"],
                timeout=timeout,
            )
            for participant in participants
        ]
        self.extra = extra if extra is not None else {}

    async def fetch_agents(self) -> None:
        """Makes each node download its associated agent from the relevant storage node."""

        for node in self.nodes:
            await node.fetch_agent()

    async def release_nodes(self) -> None:
        """Releases Hearth nodes once evaluation terminates."""

        for node in self.nodes:
            # the try-block is inside the loop because we still want
            # to try releasing the other nodes even if we fail on one!
            try:
                await node.release()
            except:
                print(f"[ERROR] Could not release node with token: {node.auth_token}")

class Node:
    base: str

    def __init__(self, base: str) -> None:
        self.base = base


class EvaluationContext:
    # TODO: we might want to consider a generator interface
    # to the node's stdio, or something fun along those lines!

    pass

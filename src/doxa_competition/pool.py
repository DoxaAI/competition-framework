import multiprocessing


class EvaluationPool:
    """An abstraction encapsulating the multiprocessing pool responsible for
    handling queued evaluation requests picked up by the competition service instance
    in separate processes."""

    _pool: multiprocessing.Pool

    def __init__(self, pool: multiprocessing.Pool) -> None:
        self._pool = pool
        self._evaluations = []

    def submit(self, function: callable, args: tuple, keyword_args: dict = {}) -> None:
        """Submits a function for execution by a pool worker process.

        Args:
            function (callable): The function to execute.
            args (tuple): Function arguments.
            keyword_args (dict, optional): Optional keyword arguments. Defaults to {}.
        """
        self._evaluations.append(
            self._pool.apply_async(
                func=function,
                args=args,
                kwds=keyword_args,
                callback=self._callback,
                error_callback=self._error_callback,
            )
        )

    def _callback(self, result):
        """This method is run on the completition of any (non-crashing) evaluation.

        Args:
            result (None): The result of the task (which does not return anything).
        """

        # We probably won't need anything here, but perhaps there's a use case!

        pass

    def _error_callback(self, exception: BaseException):
        """This method gets called whenever a user-implemented
        competition evaluation driver running in an isolated process crashes.

        Args:
            exception (BaseException): The exception generated in the driver code.
        """

        # TODO: gracefully handle driver exceptions

        print("The competition driver generated an error:", exception, flush=True)

    def close(self):
        """Closes the pool."""

        self._pool.close()

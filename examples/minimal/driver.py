from random import randint

from doxa_competition.evaluation import AgentError, EvaluationContext, EvaluationDriver


class MinimalEvaluationDriver(EvaluationDriver):
    async def handle(self, context: EvaluationContext) -> None:
        # run some competition stuff, setup game engines, etc
        node = context.nodes[0]

        # spawn application
        await node.run_python_application()

        # try to emit a fun event
        try:
            out = (await node.read_stdout_all()).strip()
            self.emit_evaluation_event("OUT", {"stdout": out})
        except:
            raise AgentError("Bad user output.")

        # set an agent result
        await self.set_agent_result(node.agent_id, "result", randint(0, 1000))

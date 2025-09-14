from google.adk.agents import BaseAgent, LlmAgent
from pydantic import Field
from typing import Callable, Any
#  条件付きでLLMを実行するカスタムエージェント
class ConditionalLlmAgent(BaseAgent):
    """条件を満たす場合のみLLMを実行し、満たさない場合は空の結果を返すエージェント"""
    
    # Pydanticフィールドとして定義
    llm_agent: LlmAgent = Field(...)
    condition_check_fn: Callable[[Any], bool] = Field(...)
    output_key: str = Field(...)
    
    def __init__(self, llm_agent, condition_check_fn, output_key, **kwargs):
        # BaseAgentの初期化
        super().__init__(
            name=llm_agent.name,
            description=llm_agent.description,
            llm_agent=llm_agent,
            condition_check_fn=condition_check_fn,
            output_key=output_key,
            **kwargs
        )
    
    # ref) https://google.github.io/adk-docs/agents/custom-agents/#implementing-custom-logic
    async def _run_async_impl(self, ctx):
        # 条件をチェック
        if self.condition_check_fn(ctx):
            # 条件を満たす場合、LLMエージェントを実行
            async for event in self.llm_agent.run_async(ctx):
                yield event
        else:
            # 条件を満たさない場合、空の結果を返す
            from google.adk.models.llm_response import LlmResponse
            yield LlmResponse(
                content="",
                turn_complete=True,
                custom_metadata={self.output_key: ""}
            )
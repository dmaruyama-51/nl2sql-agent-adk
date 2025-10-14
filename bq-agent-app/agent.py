from google.adk.agents import SequentialAgent, LlmAgent, BaseAgent
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.runners import Runner
from typing import Callable, Any
from pydantic import Field

from .question_router_agent.agent import question_router_agent
from .general_response_agent.agent import general_response_agent
from .data_analysis_agent.agent import data_analysis_flow
from .knowledge_search_agent.agent import knowledge_search_agent

# 質問タイプに基づいて適切なエージェントを実行するルーターエージェント
class QuestionTypeRouter(BaseAgent):
    """質問の種類を判定し、適切なエージェントのみを実行するルーターエージェント"""
    
    # Pydanticフィールドとして定義
    question_router_agent: LlmAgent = Field(...)
    general_response_agent: LlmAgent = Field(...)
    knowledge_search_agent: LlmAgent = Field(...)
    data_analysis_agent: SequentialAgent = Field(...)
    
    def __init__(self, question_router_agent, general_response_agent, knowledge_search_agent, data_analysis_agent, **kwargs):
        super().__init__(
            name="質問タイプルーター",
            description="質問の種類を判定し、適切なエージェントのみを実行する",
            question_router_agent=question_router_agent,
            general_response_agent=general_response_agent,
            knowledge_search_agent=knowledge_search_agent,
            data_analysis_agent=data_analysis_agent,
            **kwargs
        )
    
    async def _run_async_impl(self, ctx):
        # まず質問のルーティングを実行
        async for event in self.question_router_agent.run_async(ctx):
            yield event
        
        # ルーティング結果を取得
        routing_decision = ctx.session.state.get("routing_decision", "") if ctx.session.state else ""
        
        # ルーティング結果に基づいて適切なエージェントを実行
        if "CATEGORY: GENERAL" in routing_decision:
            # 一般質問の場合は一般回答エージェントのみ実行
            async for event in self.general_response_agent.run_async(ctx):
                yield event
        elif "CATEGORY: DATA_ANALYSIS" in routing_decision:
            # データ分析質問の場合は、まず知識検索を実行してからデータ分析フローを実行
            async for event in self.knowledge_search_agent.run_async(ctx):
                yield event
            async for event in self.data_analysis_agent.run_async(ctx):
                yield event
        else:
            # 判定できない場合のフォールバック
            from google.adk.models.llm_response import LlmResponse
            yield LlmResponse(
                content="申し訳ございませんが、質問の種類を判定できませんでした。もう少し詳細にご要望をお聞かせください。",
                turn_complete=True,
                custom_metadata={"error": "routing_failed"}
            )

# メインのルーターエージェント
root_agent = QuestionTypeRouter(
    question_router_agent=question_router_agent,
    general_response_agent=general_response_agent,
    knowledge_search_agent=knowledge_search_agent,
    data_analysis_agent=data_analysis_flow
)
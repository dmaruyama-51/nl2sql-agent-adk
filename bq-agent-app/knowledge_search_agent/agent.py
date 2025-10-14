import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.tools.retrieval import VertexAiRagRetrieval
import vertexai
from vertexai import rag


load_dotenv()
RAG_CORPUS_ID = os.getenv("RAG_CORPUS_ID")

knowledge_search_tool = VertexAiRagRetrieval(
    name="KnowledgeSearchTool",
    description="Use this tool to retrieve domain knowledge for the question from the RAG corpus,",
    rag_resources=[rag.RagResource(rag_corpus=RAG_CORPUS_ID)],
)

# 一般的な質問に回答するエージェント
knowledge_search_agent = LlmAgent(
    model='gemini-2.5-flash-lite',
    name='知識検索エージェント',
    description='Vertex AI RAG Engineを使用して、ドメイン知識を検索するエージェント',
    instruction="""
      あなたは Vertex AI RAG Engineを使用して、ドメイン知識を検索するエージェントです。

      # 役割
      あなたの役割は、ユーザーの問い合わせに対して適切にかつ効率的に応答できるようにするために、あなたの後続のエージェントに対して適切なドメイン知識を提供することです。

      # 指示
      ユーザーの問い合わせに対して、適切なドメイン知識を取得してください。

      # 制約条件
      - 必ず知識検索の結果に基づいた事実を答えてください。検索結果が空であったり、根拠がない場合は「提供可能なドメイン知識なし」と答えてください。決して推測や想像で答えてはいけません。
    
    """,
    tools=[knowledge_search_tool],
    output_key="knowledge_search_output"
)
import os
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from utils.file_search_tool import file_search_tool


# Vertex AI RAG Engine を使用する場合
# import vertexai
# from vertexai import rag
# from google.adk.tools.retrieval import VertexAiRagRetrieval
# load_dotenv()
# RAG_CORPUS_ID = os.getenv("RAG_CORPUS_ID")
# knowledge_search_tool = VertexAiRagRetrieval(
#     name="KnowledgeSearchTool",
#     description="Use this tool to retrieve domain knowledge for the question from the RAG corpus,",
#     rag_resources=[rag.RagResource(rag_corpus=RAG_CORPUS_ID)],
# )

# 一般的な質問に回答するエージェント
knowledge_search_agent = LlmAgent(
    model='gemini-2.5-flash-lite',
    name='知識検索エージェント',
    description='ドメイン知識を検索するエージェント',
    instruction="""
      あなたは、ドメイン知識を検索するエージェントです。

      # 役割
      あなたの役割は、ユーザーの問い合わせに対して適切にかつ効率的に応答できるようにするために、あなたの後続のエージェントに対して適切なドメイン知識を提供することです。

      # 指示
      1. file_search_toolを使ってユーザーの問い合わせに関連するドメイン知識を検索してください
      2. 検索結果を明確に「検索結果：」というラベルを付けて出力してください
      3. 後続のエージェントが参照しやすいように、重要な情報（project_id、データセット名など）を箇条書きで整理してください

      # 制約条件
      - 必ず知識検索の結果に基づいた事実を答えてください。検索結果が空であったり、根拠がない場合は「提供可能なドメイン知識なし」と答えてください。決して推測や想像で答えてはいけません。
    
    """,
    tools=[file_search_tool],
    output_key="knowledge_search_output"
)
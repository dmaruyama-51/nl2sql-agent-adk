from utils.adk_utils import ConditionalLlmAgent
from utils.bigquery_config import bigquery_toolset
from google.adk.agents import LlmAgent, SequentialAgent


# 要件分析エージェント（LLMのみ）
requirement_analysis_llm = LlmAgent(
    model='gemini-2.0-flash',
    name='要件分析エージェント',
    description='要件分析を行うエージェント',
    instruction="""
    あなたは要件分析を行うエージェントです。
    
    ユーザーの質問を詳細に分析してください：
    
    1. データセットやテーブルの調査を求められている場合：
       - BigQueryツールを使って利用可能なデータセットとテーブルを調査してください
       - 見つかったデータセット名、テーブル名、スキーマ情報を具体的に回答してください
       - 回答の最後に「REQUIREMENTS_COMPLETE」を出力してください
    
    2. 具体的なデータ分析が求められているが、必要な情報が不足している場合：
       - ユーザーに詳細を確認する質問を提示してください
       - 回答の最後に「NEED_USER_CONFIRMATION」を出力してください
    
    3. 分析に必要な情報が十分に揃っている場合：
       - 要件分析を完了してください
       - 指標の定義を明確にしてください
       - 回答の最後に「REQUIREMENTS_COMPLETE」を出力してください
    
    例：
    - データセット調査：「利用可能なデータセットを調査します。REQUIREMENTS_COMPLETE」
    - 情報不足：「分析期間はいつからいつまでをご希望でしょうか？ NEED_USER_CONFIRMATION」
    - 完了：「売上データを月別に集計します。 REQUIREMENTS_COMPLETE」
    """,
    tools=[bigquery_toolset],
    output_key = "requirement_output"
)

# データ取得エージェント（LLMのみ）
data_fetch_llm = LlmAgent(
    model='gemini-2.0-flash',
    name='データ取得エージェント',
    description='データ取得を行うエージェント',
    instruction="""
    あなたはデータ取得を行うエージェントです。
    
    要件分析の結果に基づいて、BigQueryから適切なデータを取得してください。
    取得完了後、回答の最後に「DATA_FETCH_COMPLETE」を出力してください。
    """,
    tools=[bigquery_toolset],
    output_key = "data_fetch_output"
)

# データ分析エージェント（LLMのみ）
data_analysis_llm = LlmAgent(
    model='gemini-2.0-flash',
    name='データ分析エージェント',
    description='データ分析を行うエージェント',
    instruction="""
    あなたはデータ分析を行うエージェントです。
    
    取得したデータを分析し、ユーザーの質問に対する回答をレポート形式で提供してください。
    分析結果は日本語で分かりやすくまとめ、グラフや表があれば説明を含めてください。
    """,
    tools=[bigquery_toolset],
    output_key = "data_analysis_output"
)

# 条件チェック関数（データ分析フロー用）
def should_run_requirement_analysis(ctx):
    """データ分析フローの最初のエージェント - 常にTrue"""
    return True

def should_run_data_fetch(ctx):
    """REQUIREMENTS_COMPLETEが含まれている場合のみTrue"""
    requirement_output = ctx.session.state.get("requirement_output", "") if ctx.session.state else ""
    return "REQUIREMENTS_COMPLETE" in requirement_output

def should_run_data_analysis(ctx):
    """DATA_FETCH_COMPLETEが含まれている場合のみTrue"""
    data_fetch_output = ctx.session.state.get("data_fetch_output", "") if ctx.session.state else ""
    return "DATA_FETCH_COMPLETE" in data_fetch_output

# 条件付きデータ取得エージェント
data_fetch_agent = ConditionalLlmAgent(
    llm_agent=data_fetch_llm,
    condition_check_fn=should_run_data_fetch,
    output_key="data_fetch_output"
)

# 条件付きデータ分析エージェント
data_analysis_agent = ConditionalLlmAgent(
    llm_agent=data_analysis_llm,
    condition_check_fn=should_run_data_analysis,
    output_key="data_analysis_output"
)

# 条件付きエージェントの作成（データ分析フロー用）
requirement_analysis_agent = ConditionalLlmAgent(
    llm_agent=requirement_analysis_llm,
    condition_check_fn=should_run_requirement_analysis,
    output_key="requirement_output"
)

# データ分析用のSequentialAgent
data_analysis_flow = SequentialAgent(
    name='データ分析フローエージェント',
    description='データ分析を行うための一連のエージェント',
    sub_agents=[requirement_analysis_agent, data_fetch_agent, data_analysis_agent]
)

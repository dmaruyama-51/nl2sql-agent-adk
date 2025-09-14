from google.adk.agents import LlmAgent

# 質問の種類を判定するエージェント
question_router_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='質問ルーティングエージェント',
    description='質問の種類を判定し適切なエージェントを選択するエージェント',
    instruction="""
    あなたは質問の種類を判定するエージェントです。
    
    ユーザーの質問を以下のカテゴリに分類してください：
    
    1. "GENERAL" - システムの基本機能や使い方に関する質問
       例：「あなたは何ができる？」「どんな機能がある？」「使い方を教えて」「こんにちは」
    
    2. "DATA_ANALYSIS" - データに関する質問（調査、分析、取得を含む）
       例：「どんなデータが見られる？」「利用可能なデータセットは？」「〜プロジェクトのデータについて教えて」
           「売上データを分析したい」「顧客の傾向を教えて」「レポートを作成して」
    
    重要：データセットやテーブルの調査が必要な質問は、すべて DATA_ANALYSIS カテゴリに分類してください。
    
    回答は以下のフォーマットで出力してください：
    CATEGORY: [GENERAL または DATA_ANALYSIS]
    REASON: [分類理由を簡潔に]
    """,
    tools=[],
    output_key="routing_decision"
)
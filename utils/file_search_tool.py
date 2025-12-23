import os
from dotenv import load_dotenv

from google import genai
from google.genai import types


load_dotenv()
GOOGLE_AI_STUDIO_API_KEY = os.getenv("GOOGLE_API_KEY")
FILE_SEARCH_STORE_NAME = os.getenv("FILE_SEARCH_STORE_NAME")

genai_client = genai.Client(
    api_key=GOOGLE_AI_STUDIO_API_KEY,
    vertexai=False
)

file_search_store = genai_client.file_search_stores.get(
    name=f"fileSearchStores/{FILE_SEARCH_STORE_NAME}"
)

def file_search_tool(query: str) -> str:
    try:
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"""
            問い合わせに対して、関連する適切なドメイン知識を取得してください。

            # 問い合わせ内容
            {query}
            """,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        file_search=types.FileSearch(
                            file_search_store_names=[file_search_store.name]
                        )
                    )
                ]
            )
        )

        if hasattr(response, 'text') and response.text:
            return {"result": response.text}
        else:
            return {"result": "検索結果が見つかりませんでした。提供可能なドメイン知識はありません。"}
    except Exception as e:
        return {"result": f"検索中にエラーが発生しました: {str(e)}\n提供可能なドメイン知識はありません。"}
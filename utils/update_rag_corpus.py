"""RAG Corpus のファイルを更新するユーティリティスクリプト"""

import os
import sys
from dotenv import load_dotenv
from vertexai import rag
import vertexai


def delete_all_files(corpus_name: str, location: str):
    """RAG Corpus 内のすべてのファイルを削除"""
    try:
        # ファイル一覧を取得
        files = rag.list_files(corpus_name=corpus_name)
        
        file_count = 0
        for file in files:
            print(f"  削除: {file.name}")
            rag.delete_file(name=file.name)
            file_count += 1
        
        if file_count == 0:
            print("削除対象のファイルはありません")
        else:
            print(f"✓ {file_count} 件のファイルを削除しました")
        
        return True
    except Exception as e:
        print(f"エラー: ファイル削除中に問題が発生しました: {e}")
        return False


def import_files(corpus_name: str, source_uri: str, location: str):
    """GCS から RAG Corpus にファイルをインポート"""
    try:
        print(f"インポート元: {source_uri}")
        
        # ファイルをインポート
        response = rag.import_files(
            corpus_name=corpus_name,
            paths=[source_uri],
        )
        
        print(f"✓ インポート完了")
        print(f"  インポートされたファイル数: {response.imported_rag_files_count}")
        
        return True
    except Exception as e:
        print(f"エラー: ファイルインポート中に問題が発生しました: {e}")
        return False


def list_files(corpus_name: str, location: str):
    """RAG Corpus 内のファイル一覧を表示"""
    try:
        files = rag.list_files(corpus_name=corpus_name)
        
        print("\n現在の RAG Corpus ファイル一覧:")
        print("-" * 80)
        
        file_count = 0
        for file in files:
            print(f"  {file.name}")
            if hasattr(file, 'display_name') and file.display_name:
                print(f"    表示名: {file.display_name}")
            print()
            file_count += 1
        
        if file_count == 0:
            print("  ファイルがありません")
        else:
            print(f"合計: {file_count} 件のファイル")
        
        return True
    except Exception as e:
        print(f"エラー: ファイル一覧取得中に問題が発生しました: {e}")
        return False


def main():
    # 環境変数の読み込み
    load_dotenv()
    
    rag_corpus_id = os.getenv("RAG_CORPUS_ID")
    gcs_bucket_name = os.getenv("GCS_BUCKET_NAME")
    gcs_path = os.getenv("GCS_PATH", "")
    
    if not rag_corpus_id:
        print("エラー: RAG_CORPUS_ID 環境変数が設定されていません")
        sys.exit(1)
    
    if not gcs_bucket_name:
        print("エラー: GCS_BUCKET_NAME 環境変数が設定されていません")
        sys.exit(1)
    
    # RAG_CORPUS_ID からプロジェクトIDとロケーションを抽出
    parts = rag_corpus_id.split('/')
    project_id = parts[1]
    location = parts[3]
    
    # Vertex AI の初期化
    vertexai.init(project=project_id, location=location)
    
    # GCS URI の構築
    if gcs_path:
        source_uri = f"gs://{gcs_bucket_name}/{gcs_path}"
    else:
        source_uri = f"gs://{gcs_bucket_name}/"
    
    print("=" * 80)
    print("RAG Corpus 更新スクリプト (Python)")
    print("=" * 80)
    print(f"プロジェクトID: {project_id}")
    print(f"ロケーション: {location}")
    print(f"RAG Corpus ID: {rag_corpus_id}")
    print(f"GCS ソース: {source_uri}")
    print()
    
    # Step 1: 既存ファイルの削除
    print("Step 1: 既存ファイルを削除中...")
    if not delete_all_files(rag_corpus_id, location):
        sys.exit(1)
    print()
    
    # Step 2: 新しいファイルのインポート
    print("Step 2: 新しいファイルをインポート中...")
    if not import_files(rag_corpus_id, source_uri, location):
        sys.exit(1)
    print()
    
    # Step 3: 結果の確認
    print("Step 3: インポート結果を確認中...")
    if not list_files(rag_corpus_id, location):
        sys.exit(1)
    
    print()
    print("=" * 80)
    print("✓ RAG Corpus の更新が完了しました")
    print("=" * 80)


if __name__ == "__main__":
    main()


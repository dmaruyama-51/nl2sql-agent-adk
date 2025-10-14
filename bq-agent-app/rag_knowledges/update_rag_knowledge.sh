#!/bin/bash

# RAG Engine のナレッジベースを更新するスクリプト
# GCS へのアップロードと RAG Engine の再インポートを実行します

set -e

# カラー出力の設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# スクリプトのディレクトリとプロジェクトルートを特定
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 環境変数の読み込み（プロジェクトルートの.envを読み込む）
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
fi

# 必須の環境変数チェック
if [ -z "$RAG_CORPUS_ID" ]; then
    echo -e "${RED}エラー: RAG_CORPUS_ID 環境変数が設定されていません${NC}"
    echo "例: export RAG_CORPUS_ID=projects/YOUR_PROJECT/locations/LOCATION/ragCorpora/CORPUS_ID"
    exit 1
fi

if [ -z "$GCS_BUCKET_NAME" ]; then
    echo -e "${RED}エラー: GCS_BUCKET_NAME 環境変数が設定されていません${NC}"
    echo "例: export GCS_BUCKET_NAME=your-rag-knowledge-bucket"
    exit 1
fi

# オプション: GCS上のパス（デフォルトは空＝バケット直下）
GCS_PATH="${GCS_PATH:-}"

# プロジェクトIDとロケーションをRAG_CORPUS_IDから抽出
PROJECT_ID=$(echo $RAG_CORPUS_ID | sed -n 's/.*projects\/\([^\/]*\).*/\1/p')
LOCATION=$(echo $RAG_CORPUS_ID | sed -n 's/.*locations\/\([^\/]*\).*/\1/p')

echo -e "${GREEN}=== RAG Engine ナレッジベース更新スクリプト ===${NC}"
echo "プロジェクトID: $PROJECT_ID"
echo "ロケーション: $LOCATION"
echo "RAG Corpus ID: $RAG_CORPUS_ID"
if [ -z "$GCS_PATH" ]; then
    echo "GCS バケット: gs://$GCS_BUCKET_NAME/ (バケット直下)"
else
    echo "GCS バケット: gs://$GCS_BUCKET_NAME/$GCS_PATH"
fi
echo ""

# rag_knowledges ディレクトリの存在確認
KNOWLEDGE_DIR="$SCRIPT_DIR"
if [ ! -d "$KNOWLEDGE_DIR" ]; then
    echo -e "${RED}エラー: $KNOWLEDGE_DIR ディレクトリが見つかりません${NC}"
    exit 1
fi

# Step 1: GCS へのアップロード
echo -e "${YELLOW}Step 1: GCS へファイルをアップロード中...${NC}"
# .sh ファイルを除外してアップロード
if [ -z "$GCS_PATH" ]; then
    gsutil -m rsync -r -x ".*\.sh$" "$KNOWLEDGE_DIR/" "gs://$GCS_BUCKET_NAME/"
else
    gsutil -m rsync -r -x ".*\.sh$" "$KNOWLEDGE_DIR/" "gs://$GCS_BUCKET_NAME/$GCS_PATH/"
fi
echo -e "${GREEN}✓ アップロード完了${NC}"
echo ""

# Step 2: RAG Engine の更新
echo -e "${YELLOW}Step 2: RAG Engine を更新中...${NC}"
cd "$PROJECT_ROOT"
uv run python utils/update_rag_corpus.py

echo ""
echo -e "${GREEN}=== 更新完了 ===${NC}"
echo "RAG Engine のナレッジベースが正常に更新されました。"


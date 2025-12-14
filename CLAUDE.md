# CLAUDE.md

## プロジェクト概要

DCE（離散選択実験）用の看護師ペルソナを生成するPythonツール。
OpenAI/Anthropic APIを使用して合成データを生成する。

## 主要コマンド

```bash
# 依存関係インストール
uv sync

# 実行
uv run python main.py -n 10

# リンティング・フォーマット
uv run ruff check .
uv run ruff format .
```

## コードスタイル

- ruff使用（Black互換）
- 行の長さ: 128文字
- ダブルクォート、スペースインデント、LF改行
- 日本語コメント可

## アーキテクチャ

- `lib/llm/`: LLMクライアント（Strategyパターン）
- `lib/config.py`: 設定読み込み
- `lib/generator.py`: ペルソナ生成（1人ずつ処理）
- `lib/sampling.py`: 統計的サンプリング
- `configs/`: バージョン別プロンプト・設定

## 環境変数

- `OPENAI_API_KEY`: OpenAI APIキー
- `ANTHROPIC_API_KEY`: Anthropic APIキー

# 推奨コマンド

## 開発環境セットアップ
```bash
# 依存関係のインストール
uv sync
```

## 実行
```bash
# 基本実行（10人生成）
uv run python main.py

# オプション指定
uv run python main.py -n 20 -s 123 -o output/result.xlsx

# Anthropic使用
uv run python main.py --provider anthropic --model claude-sonnet-4-20250514

# 設定確認（dry-run）
uv run python main.py --dry-run

# 設定一覧表示
uv run python main.py --list-configs

# 追記モード
uv run python main.py --append
```

## CLI オプション
| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `-c, --config` | 設定ディレクトリ | `configs/v1_nurse` |
| `-n, --count` | 生成人数 | 10 |
| `-s, --seed` | 乱数シード | 設定ファイルの値 |
| `-o, --output` | 出力ファイル | `output/result.xlsx` |
| `--append` | 既存ファイルに追記 | False |
| `--provider` | LLMプロバイダー (openai/anthropic) | 設定ファイルの値 |
| `--model` | モデル名 | 設定ファイルの値 |
| `--dry-run` | 設定確認のみ | - |
| `--list-configs` | 設定一覧表示 | - |

## コード品質
```bash
# リンティング（自動修正付き）
uv run ruff check .

# フォーマット
uv run ruff format .
```

## 環境変数
`.env`ファイルに以下を設定:
- `OPENAI_API_KEY` または `OPENAI_API_KEY_PERSONA`: OpenAI APIキー
- `ANTHROPIC_API_KEY`: Anthropic APIキー

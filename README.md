# DCEPersona

DCE（離散選択実験）用の看護師ペルソナを生成するツールです。
OpenAI または Anthropic の LLM API を使用して、統計的に妥当な看護師の合成データを生成します。

## セットアップ

### 1. 依存関係のインストール

```bash
uv sync
```

### 2. 環境変数の設定

`.env` ファイルを作成し、APIキーを設定します。

```env
# OpenAI を使う場合
OPENAI_API_KEY=sk-xxxxx

# Anthropic を使う場合
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

## 使い方

### 基本的な使い方

```bash
# 10人分のペルソナを生成（デフォルト）
uv run python main.py generate

# 人数を指定
uv run python main.py generate -n 20

# 出力ファイルを指定
uv run python main.py generate -o output/nurses.xlsx
```

### LLMプロバイダーの切り替え

```bash
# OpenAI（デフォルト）
uv run python main.py generate

# Anthropic
uv run python main.py generate --provider anthropic
```

### その他のオプション

```bash
# 設定確認（実際にAPIを呼び出さない）
uv run python main.py generate --dry-run

# 利用可能な設定一覧
uv run python main.py list

# 既存ファイルに追記
uv run python main.py generate --append

# 乱数シードを指定（再現性のため）
uv run python main.py generate -s 123
```

### コマンド一覧

| コマンド | 説明 |
|---------|------|
| `generate` | ペルソナを生成する |
| `list` | 利用可能な設定一覧を表示 |

### generate オプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `-n, --count` | 生成する人数 | 10 |
| `-o, --output` | 出力ファイルパス | `output/result.xlsx` |
| `-c, --config` | 設定ディレクトリ | `configs/v1_nurse` |
| `-s, --seed` | 乱数シード | 42 |
| `--provider` | LLMプロバイダー (`openai` / `anthropic`) | 設定ファイルの値 |
| `--model` | モデル名 | 設定ファイルの値 |
| `--append` | 既存ファイルに追記 | - |
| `--dry-run` | 設定確認のみ | - |

## プロンプトのカスタマイズ

`configs/` ディレクトリに新しいバージョンを作成することで、プロンプトをカスタマイズできます。

```
configs/
└── v1_nurse/
    ├── config.yaml        # LLM設定、出力カラム
    ├── system_prompt.txt  # システムプロンプト
    └── user_prompt.txt    # ユーザープロンプト
```

新しいバージョンを使う場合:

```bash
uv run python main.py generate -c configs/v2_nurse
```

## 出力形式

生成されたペルソナは Excel ファイル（`.xlsx`）として出力されます。
以下のような属性が含まれます:

- 基本属性: 性別、年齢、都道府県、婚姻状況、子供の人数など
- 職業属性: 看護師経験年数、病院種類、診療科、夜勤形態など
- その他: 年収、昇進意欲、看護資格など

## 開発

```bash
# リンティング
uv run ruff check .

# フォーマット
uv run ruff format .
```

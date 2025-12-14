# DCEPersona プロジェクト概要

## 目的
DCE（Discrete Choice Experiment）のための看護師ペルソナを生成するツール。
OpenAI/Anthropic APIを使用して、日本の看護師の合成データ（シンセティックデータ）を生成する。

## 技術スタック
- **Python**: 3.13+
- **パッケージ管理**: uv
- **主要ライブラリ**:
  - `openai`: OpenAI API クライアント
  - `anthropic`: Anthropic API クライアント
  - `pandas`: データ操作
  - `openpyxl`: Excel ファイル操作
  - `python-dotenv`: 環境変数管理
  - `pyyaml`: YAML設定ファイル読み込み
  - `ruff`: リンター・フォーマッター

## プロジェクト構造
```
DCEPersona/
├── main.py                    # メインエントリポイント（CLI）
├── configs/                   # 設定ファイル群
│   └── v1_nurse/              # バージョン別ディレクトリ
│       ├── config.yaml        # 設定（出力カラム、モデル等）
│       ├── system_prompt.txt  # システムプロンプト
│       └── user_prompt.txt    # ユーザープロンプト
│
├── lib/
│   ├── __init__.py
│   ├── llm/                   # LLM関連（Strategyパターン）
│   │   ├── __init__.py
│   │   ├── base.py            # LLMClient (ABC)
│   │   ├── openai_client.py   # OpenAI実装
│   │   └── anthropic_client.py # Anthropic実装
│   │
│   ├── config.py              # 設定読み込み（ConfigLoader）
│   ├── sampling.py            # サンプリングロジック（統計データ）
│   ├── generator.py           # PersonaGenerator（1人ずつ処理）
│   ├── output.py              # 出力処理（Excel/CSV）
│   └── log.py                 # ロギング
│
├── data/                      # 参照データ
├── output/                    # 出力ファイル
├── logs/                      # ログファイル
├── .env                       # 環境変数（APIキー等）
├── pyproject.toml             # プロジェクト設定
└── uv.lock                    # 依存関係ロックファイル
```

## アーキテクチャ
- **Strategyパターン**: LLMClient基底クラスを継承してOpenAI/Anthropicを切り替え
- **1人ずつ処理**: sampling.pyで生成した属性を元に、LLMで1件ずつペルソナを生成
- **設定ファイル分離**: configs/にバージョン別のプロンプト・設定を管理

## 出力
- `output/result.xlsx`: 生成されたペルソナのExcelファイル
- 各ペルソナには性別、年齢、都道府県、看護師経験年数、婚姻状況、子供の人数、年収などの属性が含まれる

# コードスタイル・規約

## フォーマッター・リンター
- **ruff** を使用（Black互換）
- 行の長さ: 128文字
- ターゲットバージョン: Python 3.12+

## ruff設定 (pyproject.toml)
```toml
[tool.ruff]
line-length = 128
target-version = "py312"
fix = true

lint.ignore = ["E501"]  # line length
lint.select = ["E", "F", "W", "B", "C90"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "lf"
```

## 命名規約
- 変数・関数: snake_case
- 定数: UPPER_SNAKE_CASE
- クラス: PascalCase

## その他の規約
- ダブルクォートを使用
- スペースインデント
- LF改行
- 日本語コメント可

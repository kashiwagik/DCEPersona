"""出力処理（Excel/CSV）"""

from pathlib import Path
from typing import Any

import pandas as pd

from lib.config import Config
from lib.log import logger


class OutputWriter:
    """ペルソナデータを出力するクラス"""

    def __init__(self, config: Config):
        """
        OutputWriterを初期化

        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.columns = config.output.columns
        self.format = config.output.format

    def write(
        self,
        personas: list[dict[str, Any]],
        output_path: str | Path,
        append: bool = False,
    ) -> Path:
        """
        ペルソナデータをファイルに出力

        Args:
            personas: ペルソナデータのリスト
            output_path: 出力ファイルパス
            append: Trueの場合、既存ファイルに追記

        Returns:
            Path: 出力されたファイルのパス
        """
        output_path = Path(output_path)

        # DataFrameを作成
        df = pd.DataFrame(personas)

        # カラム順を設定
        if self.columns:
            # 設定にあるカラムのみを、指定順で並べる
            existing_columns = [col for col in self.columns if col in df.columns]
            # 設定にないカラムも末尾に追加（デバッグ用）
            extra_columns = [col for col in df.columns if col not in self.columns]
            df = df.reindex(columns=existing_columns + extra_columns)

        # 追記モードの場合、既存データを読み込んで結合
        if append and output_path.exists():
            df = self._append_to_existing(df, output_path)

        # 出力
        if self.format == "xlsx" or output_path.suffix == ".xlsx":
            self._write_excel(df, output_path)
        elif self.format == "csv" or output_path.suffix == ".csv":
            self._write_csv(df, output_path)
        else:
            # デフォルトはExcel
            self._write_excel(df, output_path)

        logger.info("Output written: %s (%d records)", output_path, len(df))

        return output_path

    def _append_to_existing(self, df: pd.DataFrame, output_path: Path) -> pd.DataFrame:
        """既存ファイルにデータを追記"""
        try:
            if output_path.suffix == ".xlsx":
                df_existing = pd.read_excel(output_path, sheet_name="Sheet1")
            else:
                df_existing = pd.read_csv(output_path, encoding="utf-8-sig")

            df = pd.concat([df_existing, df], ignore_index=True)
            logger.info("Appending to existing file: %d existing + %d new", len(df_existing), len(df) - len(df_existing))

        except Exception as e:
            logger.warning("Failed to read existing file for append: %s", e)

        return df

    def _write_excel(self, df: pd.DataFrame, output_path: Path) -> None:
        """Excelファイルとして出力"""
        # 親ディレクトリを作成
        output_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_excel(output_path, sheet_name="Sheet1", index=False)

    def _write_csv(self, df: pd.DataFrame, output_path: Path) -> None:
        """CSVファイルとして出力"""
        # 親ディレクトリを作成
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # BOM付きUTF-8でExcelでの文字化けを防ぐ
        df.to_csv(output_path, index=False, encoding="utf-8-sig")


def can_write(path: str | Path) -> bool:
    """
    指定したパスに書き込み可能かチェック

    Args:
        path: チェックするパス

    Returns:
        bool: 書き込み可能ならTrue
    """
    path = Path(path)

    if not path.is_file():
        return True

    try:
        with open(path, "r+"):
            return True
    except PermissionError:
        return False

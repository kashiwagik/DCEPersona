import logging
from datetime import datetime
from pathlib import Path


def setup_logger(name: str = __name__, log_dir: str = "logs") -> logging.Logger:
    """
    日付付きログファイルに出力するロガーを設定する

    Args:
        name: ロガー名
        log_dir: ログファイルを保存するディレクトリ

    Returns:
        設定済みのロガー
    """
    # ログディレクトリを作成
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)

    # 日付付きファイル名を生成（例: 2025-10-30.log）
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"{today}.log"

    # ロガーを取得
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 既存のハンドラーをクリア（重複を防ぐ）
    if logger.handlers:
        logger.handlers.clear()

    # ファイルハンドラーを設定
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # コンソールハンドラーを設定
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # フォーマッターを設定（日付・時刻、レベル、メッセージ）
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # ハンドラーをロガーに追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# デフォルトのロガーを作成
logger = setup_logger()


if __name__ == "__main__":
    # 使用例
    logger.debug("デバッグメッセージ")  # デフォルトでは表示されません
    logger.info("情報メッセージ")
    logger.warning("警告メッセージ")
    logger.error("エラーメッセージ")

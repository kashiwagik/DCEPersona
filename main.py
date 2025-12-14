"""DCEPersona - 看護師ペルソナ生成ツール"""

import json
from enum import Enum
from typing import Annotated, Optional

import typer
from dotenv import load_dotenv

from lib.config import ConfigLoader, create_llm_client
from lib.generator import PersonaGenerator
from lib.log import logger
from lib.output import OutputWriter, can_write

load_dotenv()

app = typer.Typer(help="DCE用の看護師ペルソナを生成するツール")


class Provider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"


def print_progress(current: int, total: int, persona: dict):
    """進捗を表示するコールバック"""
    name = persona.get("診療科", "生成中")
    error = persona.get("_error", "")
    status = f"[ERROR: {error}]" if error else ""
    typer.echo(f"  [{current}/{total}] id={persona.get('id', '?')} {name} {status}")


@app.command()
def generate(
    count: Annotated[int, typer.Option("-n", "--count", help="生成する人数")] = 10,
    output: Annotated[str, typer.Option("-o", "--output", help="出力ファイルパス")] = "output/result.xlsx",
    config_path: Annotated[str, typer.Option("-c", "--config", help="設定ディレクトリ")] = "configs/v1_nurse",
    seed: Annotated[Optional[int], typer.Option("-s", "--seed", help="乱数シード")] = None,
    provider: Annotated[Optional[Provider], typer.Option(help="LLMプロバイダー")] = None,
    model: Annotated[Optional[str], typer.Option(help="モデル名")] = None,
    append: Annotated[bool, typer.Option(help="既存ファイルに追記")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="設定確認のみ")] = False,
):
    """ペルソナを生成する"""
    # 設定読み込み
    try:
        config = ConfigLoader.load(config_path)
        logger.info("Loaded config: %s", config.name)
    except FileNotFoundError as e:
        typer.echo(f"エラー: {e}", err=True)
        raise typer.Exit(1) from None

    # コマンドライン引数で上書き
    if provider:
        config.llm.provider = provider.value
    if model:
        config.llm.model = model

    # ドライランモード
    if dry_run:
        typer.echo("=== Dry Run Mode ===")
        typer.echo(f"Config: {config.name}")
        typer.echo(f"Description: {config.description}")
        typer.echo(f"LLM Provider: {config.llm.provider}")
        typer.echo(f"LLM Model: {config.llm.model}")
        typer.echo(f"Temperature: {config.llm.temperature}")
        typer.echo(f"Count: {count}")
        typer.echo(f"Seed: {seed or config.sampling.seed}")
        typer.echo(f"Output: {output}")
        typer.echo(f"Append: {append}")
        typer.echo(f"Output Columns: {len(config.output.columns)} columns")
        raise typer.Exit(0)

    # 出力ファイルの書き込みチェック
    if not can_write(output):
        typer.echo(f"エラー: {output} を閉じてください", err=True)
        raise typer.Exit(1)

    # LLMクライアント作成
    try:
        llm_client = create_llm_client(config.llm)
        logger.info("Using LLM: %s (%s)", config.llm.provider, config.llm.model)
    except ValueError as e:
        typer.echo(f"エラー: {e}", err=True)
        raise typer.Exit(1) from None

    # ペルソナ生成
    typer.echo(f"ペルソナを生成中... (n={count}, provider={config.llm.provider})")
    generator = PersonaGenerator(config, llm_client)

    personas = generator.generate_batch(
        n=count,
        seed=seed,
        on_progress=print_progress,
    )

    # 結果を表示
    typer.echo(f"\n生成完了: {len(personas)}件")
    for persona in personas[:3]:
        typer.echo(json.dumps(persona, ensure_ascii=False, indent=2))
    if len(personas) > 3:
        typer.echo(f"... 他 {len(personas) - 3}件")

    # 出力
    writer = OutputWriter(config)
    output_path = writer.write(personas, output, append=append)
    typer.echo(f"\n出力: {output_path}")


@app.command("list")
def list_configs():
    """利用可能な設定一覧を表示"""
    configs = ConfigLoader.list_configs()
    if configs:
        typer.echo("利用可能な設定:")
        for name in configs:
            typer.echo(f"  - {name}")
    else:
        typer.echo("設定が見つかりません。configs/ ディレクトリを確認してください。")


if __name__ == "__main__":
    app()

"""DCEPersona - 看護師ペルソナ生成ツール"""

import json
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import typer
from dotenv import load_dotenv

from lib.config import ConfigLoader, create_llm_client
from lib.generator import PersonaGenerator
from lib.log import logger
from lib.output import OutputWriter, can_write

load_dotenv()

app = typer.Typer(help="DCE用の看護師ペルソナを生成するツール", pretty_exceptions_enable=False)


class Provider(str, Enum):
    openai = "openai"
    anthropic = "anthropic"


def print_progress(current: int, total: int, persona: dict):
    """進捗を表示するコールバック"""
    name = persona.get("診療科", "生成中")
    error = persona.get("_error", "")
    status = f"[ERROR: {error}]" if error else ""
    typer.echo(f"  [{current}/{total}] id={persona.get('id', '?')} {name} {status}")


def get_unique_filepath(filepath: str) -> str:
    """既存ファイルと重複しないファイルパスを返す

    ファイルが存在しない場合はそのまま返す。
    存在する場合は result(1).xlsx, result(2).xlsx のように連番を付ける。
    """
    path = Path(filepath)
    if not path.exists():
        return filepath

    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    counter = 1
    while True:
        new_path = parent / f"{stem}({counter}){suffix}"
        if not new_path.exists():
            return str(new_path)
        counter += 1


@app.command()
def generate(
    count: Annotated[int, typer.Option("-n", "--count", help="生成する人数")] = 10,
    output: Annotated[str, typer.Option("-o", "--output", help="出力ファイルパス")] = None,
    config_name: Annotated[str, typer.Option("-c", "--config", help="設定ディレクトリ")] = "v1_nurse",
    seed: Annotated[Optional[int], typer.Option("-s", "--seed", help="乱数シード")] = None,
    provider: Annotated[Optional[Provider], typer.Option(help="LLMプロバイダー")] = None,
    model: Annotated[Optional[str], typer.Option(help="モデル名")] = None,
    append: Annotated[bool, typer.Option(help="既存ファイルに追記")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="設定確認のみ")] = False,
    generate_excel_path: Annotated[
        str, typer.Option("--generate-excel-path", help="Excelファイルパス（指定されるとgenerateしない）")
    ] = None,
):
    """ペルソナを生成する"""
    """
    gpt-5.2-pro-2025-12-11  Input:$21   Output:$168
    gpt-5.2-2025-12-11      Input:$1.75 Output:$14
    gpt-5-mini-2025-08-07   Input:$0.25 Output:$2
    gpt-5-nano-2025-08-07   Input:$0.05 Output:$0.4
    gpt-4.1-2025-04-14      Input:$2    Output:$8
    gpt-4o-mini             Input:$0.15 Output:$0.6

    claude Opus 4.5         Input:$2.50 Output:$12.50
    claude Sonnet 4.5       Input:$1.50 Output:$7.50

    Gemini-2.5-Pro          Input:$1.25   Output:$5
    Gemini-2.0-Flash        Input:$0.10   Output:$0.40
    Gemini-1.5-Flash        Input:$0.10   Output:$0.40
    """
    # 設定読み込み
    try:
        config = ConfigLoader.load("configs/" + config_name)
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

    # 出力ファイルパスの決定（追記モードでない場合、既存ファイルがあれば連番を付ける）
    output_name = output or config_name
    if not append:
        output = get_unique_filepath(f"output/{output_name}.xlsx")

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

    if generate_excel_path:
        personas = generator.generate_batch_from_excel(
            file_path=generate_excel_path,
            sheet_name="Sheet1",
            n=count,
        )
    else:
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
    settings = config.to_json()
    writer = OutputWriter(config)
    output_path = writer.write(personas, output, settings=settings, append=append)
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

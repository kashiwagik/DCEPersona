"""設定ファイルの読み込みと管理"""

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml


@dataclass
class LLMConfig:
    """LLM設定"""

    provider: str = "openai"
    model: str = "gpt-4o-mini"
    temperature: float = 1.0
    max_tokens: int = 2000
    extra_params: dict = field(default_factory=dict)


@dataclass
class SamplingConfig:
    """サンプリング設定"""

    seed: int = 42
    attributes: list[str] = field(default_factory=list)


@dataclass
class OutputConfig:
    """出力設定"""

    format: str = "xlsx"
    columns: list[str] = field(default_factory=list)


@dataclass
class Config:
    """設定全体を保持するクラス"""

    name: str
    description: str
    llm: LLMConfig
    sampling: SamplingConfig
    output: OutputConfig
    system_prompt: str
    user_prompt: str
    config_dir: Path
    generate_excel_path: str | None = None

    def to_json(self, indent: int | None = 2) -> str:
        """設定をJSON文字列として返す"""
        return json.dumps(asdict(self), ensure_ascii=False, indent=indent, default=str)


class ConfigLoader:
    """設定ファイルを読み込むクラス"""

    @staticmethod
    def load(config_path: str | Path) -> Config:
        """
        設定ディレクトリから設定を読み込む

        Args:
            config_path: 設定ディレクトリのパス（例: "configs/v1_nurse"）

        Returns:
            Config: 設定オブジェクト
        """
        config_dir = Path(config_path)

        if not config_dir.exists():
            raise FileNotFoundError(f"設定ディレクトリが見つかりません: {config_dir}")

        # config.yaml を読み込み
        config_file = config_dir / "config.yaml"
        if not config_file.exists():
            raise FileNotFoundError(f"config.yaml が見つかりません: {config_file}")

        with open(config_file, encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        # プロンプトファイルを読み込み
        system_prompt = ConfigLoader._load_prompt(config_dir / "system_prompt.txt")
        user_prompt = ConfigLoader._load_prompt(config_dir / "user_prompt.txt")

        # LLM設定
        llm_raw = raw_config.get("llm", {})
        llm_config = LLMConfig(
            provider=llm_raw.get("provider", "openai"),
            model=llm_raw.get("model", "gpt-4o-mini"),
            temperature=llm_raw.get("temperature", 1.0),
            max_tokens=llm_raw.get("max_tokens", 2000),
            extra_params=llm_raw.get("extra_params", {}),
        )

        # サンプリング設定
        sampling_raw = raw_config.get("sampling", {})
        sampling_config = SamplingConfig(
            seed=sampling_raw.get("seed", 42),
            attributes=sampling_raw.get("attributes", []),
        )

        # 出力設定
        output_raw = raw_config.get("output", {})
        output_config = OutputConfig(
            format=output_raw.get("format", "xlsx"),
            columns=output_raw.get("columns", []),
        )

        return Config(
            name=raw_config.get("name", "unnamed"),
            description=raw_config.get("description", ""),
            llm=llm_config,
            sampling=sampling_config,
            output=output_config,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            config_dir=config_dir,
        )

    @staticmethod
    def _load_prompt(path: Path) -> str:
        """プロンプトファイルを読み込む"""
        if not path.exists():
            return ""
        with open(path, encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def list_configs(configs_dir: str | Path = "configs") -> list[str]:
        """
        利用可能な設定一覧を取得

        Args:
            configs_dir: 設定ディレクトリのルート

        Returns:
            list[str]: 設定名のリスト
        """
        configs_path = Path(configs_dir)
        if not configs_path.exists():
            return []

        return [d.name for d in configs_path.iterdir() if d.is_dir() and (d / "config.yaml").exists()]


def create_llm_client(llm_config: LLMConfig):
    """
    LLM設定からクライアントを作成する（ファクトリ関数）

    Args:
        llm_config: LLM設定

    Returns:
        LLMClient: 対応するLLMクライアント
    """
    from lib.llm import AnthropicClient, OpenAIClient

    provider = llm_config.provider.lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY が設定されていません")
        return OpenAIClient(api_key=api_key, model=llm_config.model)

    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY が設定されていません")
        return AnthropicClient(api_key=api_key, model=llm_config.model)

    else:
        raise ValueError(f"未対応のプロバイダー: {provider}")

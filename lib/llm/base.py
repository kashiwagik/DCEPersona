"""LLMクライアントの基底クラス定義"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLMからのレスポンス"""

    content: str
    model: str
    usage: dict


class LLMClient(ABC):
    """LLMクライアントの抽象基底クラス（Strategyパターン）"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """プロバイダー名を返す"""
        pass

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        max_tokens: int = 2000,
        extra_params: dict | None = None,
    ) -> LLMResponse:
        """
        LLMにリクエストを送信してレスポンスを取得する

        Args:
            system_prompt: システムプロンプト
            user_prompt: ユーザープロンプト
            temperature: 生成の多様性（0.0-2.0）
            max_tokens: 最大トークン数
            extra_params: モデル固有の追加パラメータ

        Returns:
            LLMResponse: レスポンスオブジェクト
        """
        pass

    @abstractmethod
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        max_tokens: int = 2000,
        extra_params: dict | None = None,
    ) -> LLMResponse:
        """
        JSON形式での出力を強制してリクエストを送信

        Args:
            system_prompt: システムプロンプト
            user_prompt: ユーザープロンプト
            temperature: 生成の多様性（0.0-2.0）
            max_tokens: 最大トークン数
            extra_params: モデル固有の追加パラメータ

        Returns:
            LLMResponse: レスポンスオブジェクト（contentはJSON文字列）
        """
        pass

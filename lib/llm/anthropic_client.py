"""Anthropic APIクライアント実装"""

from anthropic import Anthropic

from lib.log import logger

from .base import LLMClient, LLMResponse


class AnthropicClient(LLMClient):
    """Anthropic APIを使用するLLMクライアント"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        """
        Anthropicクライアントを初期化

        Args:
            api_key: Anthropic APIキー
            model: 使用するモデル名
        """
        self._client = Anthropic(api_key=api_key)
        self._model = model

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        logger.info("Anthropic generate: model=%s", self._model)

        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )

        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        }

        logger.info("Anthropic response received: tokens=%d", usage["total_tokens"])

        return LLMResponse(content=content, model=self._model, usage=usage)

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """
        JSON形式での出力を要求してリクエストを送信

        Note:
            Anthropicには response_format がないため、
            システムプロンプトにJSON出力を指示する形で対応
        """
        logger.info("Anthropic generate_json: model=%s", self._model)

        # JSON出力を強制するための指示を追加
        json_instruction = "\n\n重要: 出力は必ず有効なJSONオブジェクトのみを返してください。説明文や前後のテキストは不要です。"
        enhanced_system_prompt = system_prompt + json_instruction

        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=enhanced_system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )

        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        }

        logger.info("Anthropic JSON response received: tokens=%d", usage["total_tokens"])

        return LLMResponse(content=content, model=self._model, usage=usage)

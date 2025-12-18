"""Anthropic APIクライアント実装"""

import re

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
        extra_params: dict | None = None,
    ) -> LLMResponse:
        logger.info("Anthropic generate: model=%s", self._model)

        # extra_params にトークン制限がなければ max_tokens を使用
        params = extra_params.copy() if extra_params else {}
        if "max_tokens" not in params:
            params["max_tokens"] = max_tokens

        response = self._client.messages.create(
            model=self._model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            **params,
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
        extra_params: dict | None = None,
    ) -> LLMResponse:
        """
        JSON形式での出力を要求してリクエストを送信

        Note:
            Anthropicには response_format がないため、
            システムプロンプトにJSON出力を指示する形で対応
        """
        logger.info("Anthropic generate_json: model=%s", self._model)

        # JSON出力を強制するための指示を追加
        json_instruction = "\n\n重要: 出力は必ず有効なJSONオブジェクトのみを返してください。説明文や前後のテキストは不要です。** 先頭にjsonをつけるな。 **"
        enhanced_system_prompt = system_prompt + json_instruction

        # extra_params にトークン制限がなければ max_tokens を使用
        params = extra_params.copy() if extra_params else {}
        if "max_tokens" not in params:
            params["max_tokens"] = max_tokens

        logger.info("Anthropic JSON SYSTEM: %s", enhanced_system_prompt)
        logger.info("Anthropic JSON USER: %s", user_prompt)

        response = self._client.messages.create(
            model=self._model,
            system=enhanced_system_prompt,
            messages=[
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            **params,
        )

        content = ""
        for block in response.content:
            if block.type == "text":
                content += block.text

        # anthropicは、なぜかjson{}と返す
        print(f"# 1 #########\n{content}$$$$$$$$$$$$\n")
        content = re.sub(r"^```(.*)```", r"\1", content, flags=re.DOTALL)
        print(f"# 2 #########\n{content}$$$$$$$$$$$$\n")
        if content.startswith("json"):
            print("json start")
            content = re.sub(r"json\n?", "", content, flags=re.DOTALL)
        print(f"# 3 #########\n{content}$$$$$$$$$$$$\n")

        usage = {
            "prompt_tokens": response.usage.input_tokens,
            "completion_tokens": response.usage.output_tokens,
            "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
        }

        logger.info("Anthropic JSON response: %s", response)
        logger.info("Anthropic JSON response received: tokens=%d", usage["total_tokens"])

        return LLMResponse(content=content, model=self._model, usage=usage)

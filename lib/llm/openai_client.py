"""OpenAI APIクライアント実装"""

from openai import OpenAI

from lib.log import logger

from .base import LLMClient, LLMResponse


class OpenAIClient(LLMClient):
    """OpenAI APIを使用するLLMクライアント"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        OpenAIクライアントを初期化

        Args:
            api_key: OpenAI APIキー
            model: 使用するモデル名
        """
        self._client = OpenAI(api_key=api_key)
        self._model = model

    @property
    def provider_name(self) -> str:
        return "openai"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        logger.info("OpenAI generate: model=%s", self._model)

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content or ""
        usage = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0,
        }

        logger.info("OpenAI response received: tokens=%d", usage["total_tokens"])

        return LLMResponse(content=content, model=self._model, usage=usage)

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        logger.info("OpenAI generate_json: model=%s", self._model)

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
            max_tokens=max_tokens,
        )

        content = response.choices[0].message.content or ""
        usage = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0,
        }

        logger.info("OpenAI JSON response received: tokens=%d", usage["total_tokens"])

        return LLMResponse(content=content, model=self._model, usage=usage)

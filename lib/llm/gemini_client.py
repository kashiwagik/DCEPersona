"""Google Gemini APIを使用するLLMクライアント"""

from google import genai
from google.genai import types

from lib.log import logger

from .base import LLMClient, LLMResponse


class GeminiClient(LLMClient):
    """Google Gemini APIを使用するLLMクライアント"""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        """
        Geminiクライアントを初期化

        Args:
            api_key: Gemini APIキー
            model: 使用するモデル名
        """
        self._client = genai.Client(api_key=api_key)
        # モデル名を小文字に変換し、models/ プレフィックスがなければ追加
        model = model.lower()
        if not model.startswith("models/"):
            model = f"models/{model}"
        self._model = model

    @property
    def provider_name(self) -> str:
        return "gemini"

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        max_tokens: int = 8192,
        extra_params: dict | None = None,
    ) -> LLMResponse:
        logger.info("Gemini generate: model=%s", self._model)

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        logger.debug("Gemini SYSTEM_PROMPT", system_prompt)
        logger.debug("Gemini USER_PROMPT", user_prompt)
        response = self._client.models.generate_content(
            model=self._model,
            contents=user_prompt,
            config=config,
        )

        logger.debug("Gemini RESPONSE", response)
        content = response.text or ""
        usage = {
            "prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
            "completion_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
            "total_tokens": response.usage_metadata.total_token_count if response.usage_metadata else 0,
        }

        logger.info("Gemini response received: tokens=%d", usage["total_tokens"])

        return LLMResponse(content=content, model=self._model, usage=usage)

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 1.0,
        max_tokens: int = 8192,
        extra_params: dict | None = None,
    ) -> LLMResponse:
        logger.info("Gemini generate_json: model=%s, max_tokens=%d", self._model, max_tokens)

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            include_thoughts=True,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
                        
        )

        logger.debug("Gemini SYSTEM: %s", system_prompt)
        logger.debug("Gemini USER: %s", user_prompt)

        response = self._client.models.generate_content(
            model=self._model,
            contents=user_prompt,
            config=config,
        )
        logger.debug("Gemini RESPONSE: %s", response)

        # finish_reasonを確認
        if response.candidates and response.candidates[0].finish_reason:
            finish_reason = response.candidates[0].finish_reason
            if finish_reason.name == "MAX_TOKENS":
                raise ValueError(
                    f"Gemini response was truncated due to max_tokens limit ({max_tokens}). "
                    "Please increase max_tokens in config."
                )

        content = response.text or ""
        usage = {
            "prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
            "completion_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
            "total_tokens": response.usage_metadata.total_token_count if response.usage_metadata else 0,
        }

        logger.info("Gemini usage: %s", usage)

        return LLMResponse(content=content, model=self._model, usage=usage)

"""ペルソナ生成ロジック"""

import json
from collections.abc import Callable
from typing import Any

from lib.config import Config
from lib.llm.base import LLMClient
from lib.log import logger
from lib.sampling import generate_synthetic_nurse_data


class PersonaGenerator:
    """ペルソナを1人ずつ生成するクラス"""

    def __init__(self, config: Config, llm_client: LLMClient):
        """
        PersonaGeneratorを初期化

        Args:
            config: 設定オブジェクト
            llm_client: LLMクライアント
        """
        self.config = config
        self.llm = llm_client

    def generate_one(self, persona_id: int, base_attributes: dict[str, Any]) -> dict[str, Any]:
        """
        1人分のペルソナを生成

        Args:
            persona_id: ペルソナID
            base_attributes: sampling.pyで生成した基本属性

        Returns:
            dict: 完成したペルソナデータ
        """
        # ユーザープロンプトを構築
        user_prompt = self._build_user_prompt(persona_id, base_attributes)

        logger.info("Generating persona id=%d", persona_id)

        # LLMにリクエスト
        response = self.llm.generate_json(
            system_prompt=self.config.system_prompt,
            user_prompt=user_prompt,
            temperature=self.config.llm.temperature,
            max_tokens=self.config.llm.max_tokens,
        )

        # レスポンスをパース
        persona = self._parse_response(response.content, persona_id, base_attributes)

        logger.info("Generated persona id=%d: %s", persona_id, persona.get("診療科", "N/A"))

        return persona

    def generate_batch(
        self,
        n: int,
        seed: int | None = None,
        start_id: int = 1,
        on_progress: Callable[[int, int, dict], None] | None = None,
    ) -> list[dict[str, Any]]:
        """
        n人分のペルソナを1人ずつ生成

        Args:
            n: 生成する人数
            seed: 乱数シード（Noneの場合は設定から取得）
            start_id: 開始ID
            on_progress: 進捗コールバック (current, total, persona) -> None

        Returns:
            list[dict]: ペルソナのリスト
        """
        if seed is None:
            seed = self.config.sampling.seed

        # サンプリングデータを生成
        logger.info("Generating base data: n=%d, seed=%d", n, seed)
        base_data = generate_synthetic_nurse_data(n=n, seed=seed)

        results = []
        for i, row in base_data.iterrows():
            persona_id = start_id + i
            base_attrs = row.to_dict()

            try:
                persona = self.generate_one(persona_id, base_attrs)
                results.append(persona)

                if on_progress:
                    on_progress(i + 1, n, persona)

            except Exception as e:
                logger.error("Failed to generate persona id=%d: %s", persona_id, e)
                # エラー時は基本属性のみで記録
                error_persona = {"id": persona_id, **base_attrs, "_error": str(e)}
                results.append(error_persona)

                if on_progress:
                    on_progress(i + 1, n, error_persona)

        return results

    def _build_user_prompt(self, persona_id: int, base_attributes: dict[str, Any]) -> str:
        """ユーザープロンプトを構築"""
        # 基本属性を文字列化
        attrs_str = "\n".join(f"- {k}: {v}" for k, v in base_attributes.items())

        # テンプレートに埋め込み
        prompt = self.config.user_prompt
        prompt = prompt.replace("{base_attributes}", attrs_str)
        prompt = prompt.replace("{id}", str(persona_id))

        # 各属性を個別に埋め込み
        for key, value in base_attributes.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))

        return prompt

    def _parse_response(
        self,
        content: str,
        persona_id: int,
        base_attributes: dict[str, Any],
    ) -> dict[str, Any]:
        """
        LLMのレスポンスをパースしてペルソナデータを抽出

        Args:
            content: LLMからのレスポンス（JSON文字列）
            persona_id: ペルソナID
            base_attributes: 基本属性（フォールバック用）

        Returns:
            dict: パースされたペルソナデータ
        """
        try:
            parsed = json.loads(content)

            # {"persona": {...}} 形式の場合
            if isinstance(parsed, dict) and "persona" in parsed:
                parsed = parsed["persona"]

            # IDを確実に設定
            parsed["id"] = persona_id

            return parsed

        except json.JSONDecodeError as e:
            logger.warning("JSON parse error for persona id=%d: %s", persona_id, e)
            # パースに失敗した場合は基本属性を返す
            return {
                "id": persona_id,
                **base_attributes,
                "_raw_response": content,
                "_parse_error": str(e),
            }

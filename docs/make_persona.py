import json

from openai import OpenAI

from data.prompt import SYSTEM_PROMPT, USER_PROMPT
from lib.log import logger


def make_persona(client: OpenAI, n: int = 5):
    system_prompt = SYSTEM_PROMPT.format(n=n)

    logger.info("make_persona: query")
    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # 例: コスト重視。より高性能が必要なら "gpt-5" に変更可
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": USER_PROMPT},
        ],
        # JSONで強制出力（Chat Completions の response_format）
        response_format={"type": "json_object"},  # ※JSON配列全体を1つのJSONとして返す
        temperature=1,
        seed=0,
        max_tokens=8000,  # 必要に応じて増減
    )

    logger.info("make_persona: response received\n%s", resp)
    # モデル出力（JSON文字列）をパース
    content = resp.choices[0].message.content

    # もし response_format が "json_object" の都合で { "data": [...] } のように返ってきた場合も考慮
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "data" in parsed:
            personas = parsed["data"]
        elif isinstance(parsed, list):
            personas = parsed
        else:
            # 想定外のJSON形状はそのまま保持
            personas = parsed
    except json.JSONDecodeError:
        # 万一JSONで返らなかった場合のフォールバック（整形を試みる or そのまま保存）
        personas = content

    return personas

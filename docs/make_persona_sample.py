import json

from openai import OpenAI

from .log import logger


def make_persona(client: OpenAI, n: int = 5):
    SYSTEM_PROMPT = """あなたは医療の現場理解に長けたプロダクトリサーチャーです。
    出力は必ずJSON配列のみ（前後に説明文なし）。各要素はコンパクトに。"""

    USER_PROMPT = f"""
    「現場で働く看護師のペルソナ」を{n}種類作成してください。
    日本の100床以上の病院を想定して、年代・経験年数・勤務形態・専門領域・地域・価値観・課題・目標にバリエーションを持たせてください。

    出力は次の辞書の配列に１人ずつ作成してください。
    {{
        "personas": [ ... ]
    }}

    1人分の各要素のスキーマは以下の通り
    {{
        "id": "N###",                // 連番 N001..N100
        "department": "ICU/ER/整形/小児/在宅 など",
        "years_experience": 8,       // 数値（年）
        "age": 30,     // 数値（年齢）
        "license_types": ["正看護師", "認定看護師 など"],   // 配列
        "shift_pattern": "日勤専従/2交替/3交替/オンコール など",
        "location": "都道府県 or 地域特性",
        "skills": ["急変対応", "褥瘡管理", "ME機器 など"],
        "interests": ["研究", "教育", "マネジメント", "ワークライフバランス", "給与 など"],
        "challenges": ["人的リソース不足", "多重課題 など"],
        "goals": ["専門認定取得", "業務改善 など"],
    }}

    制約：
    - {n}件ちょうど。
    - 各要素は200〜320文字程度（日本語ベース、用語は簡潔）。
    - 同じパターンの繰り返しを避け、実在しそうなバリエーションを担保。
    """

    logger.info("make_persona: query")
    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # 例: コスト重視。より高性能が必要なら "gpt-5" に変更可
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT},
        ],
        # JSONで強制出力（Chat Completions の response_format）
        response_format={"type": "json_object"},  # ※JSON配列全体を1つのJSONとして返す
        temperature=0.7,
        max_tokens=6000,  # 必要に応じて増減
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

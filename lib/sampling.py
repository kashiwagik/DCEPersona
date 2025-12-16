import numpy as np
import pandas as pd

# -----------------------------
# 設定（ここを調整すると分布が変わります）
# -----------------------------
SEED = 42
N = 1000  # 生成件数

# 看護師の性別比（例：女性90%、男性10%）
P_FEMALE = 0.90

# 年齢分布（20-29, 30-39, 40-49, 50-59, 60-69）
AGE_BANDS = ["20代", "30代", "40代", "50代", "60代"]
AGE_BAND_WEIGHTS = np.array([0.28, 0.27, 0.22, 0.18, 0.05])  # それっぽい例

# 都市サイズカテゴリ
CITY_SIZES = ["大都市", "中都市", "小都市", "町村"]

# 都道府県（47）
PREFS = [
    "北海道",
    "青森県",
    "岩手県",
    "宮城県",
    "秋田県",
    "山形県",
    "福島県",
    "茨城県",
    "栃木県",
    "群馬県",
    "埼玉県",
    "千葉県",
    "東京都",
    "神奈川県",
    "新潟県",
    "富山県",
    "石川県",
    "福井県",
    "山梨県",
    "長野県",
    "岐阜県",
    "静岡県",
    "愛知県",
    "三重県",
    "滋賀県",
    "京都府",
    "大阪府",
    "兵庫県",
    "奈良県",
    "和歌山県",
    "鳥取県",
    "島根県",
    "岡山県",
    "広島県",
    "山口県",
    "徳島県",
    "香川県",
    "愛媛県",
    "高知県",
    "福岡県",
    "佐賀県",
    "長崎県",
    "熊本県",
    "大分県",
    "宮崎県",
    "鹿児島県",
    "沖縄県",
]

# 都道府県の出やすさ（超ざっくり：人口多いところをやや増やす例）
# ※実データではない「それっぽい偏り」です
BIG_PREF_WEIGHT = {
    "東京都": 3.0,
    "神奈川県": 2.0,
    "大阪府": 2.0,
    "愛知県": 1.8,
    "埼玉県": 1.6,
    "千葉県": 1.6,
    "兵庫県": 1.4,
    "福岡県": 1.4,
    "北海道": 1.3,
    "静岡県": 1.2,
    "京都府": 1.1,
    "広島県": 1.1,
    "宮城県": 1.1,
    "沖縄県": 1.0,
}
BASE_W = np.array([BIG_PREF_WEIGHT.get(p, 1.0) for p in PREFS], dtype=float)
PREF_WEIGHTS = BASE_W / BASE_W.sum()

# 都道府県→都市サイズの偏り（ざっくり）
METRO_PREFS = {"東京都", "神奈川県", "大阪府", "愛知県", "埼玉県", "千葉県", "兵庫県", "福岡県", "京都府"}


def sample_city_size(rng, pref):
    if pref in METRO_PREFS:
        # 都市部多め
        w = np.array([0.55, 0.30, 0.12, 0.03])
    else:
        # 地方寄り
        w = np.array([0.15, 0.35, 0.35, 0.15])
    return rng.choice(CITY_SIZES, p=w)


# 年代→実年齢サンプリング
def sample_age(rng, band):
    if band == "20代":
        return int(rng.integers(20, 30))
    if band == "30代":
        return int(rng.integers(30, 40))
    if band == "40代":
        return int(rng.integers(40, 50))
    if band == "50代":
        return int(rng.integers(50, 60))
    if band == "60代":
        return int(rng.integers(60, 70))
    raise ValueError(band)


# 婚姻確率（年齢×都市サイズでそれっぽく）
def married_prob(age, city_size):
    # 年齢で上がる（ただし100%にはしない）
    # 都市部ほどやや低めに補正
    if age < 25:
        base = 0.15
    elif age < 30:
        base = 0.30
    elif age < 35:
        base = 0.55
    elif age < 40:
        base = 0.65
    elif age < 45:
        base = 0.70
    elif age < 50:
        base = 0.72
    elif age < 55:
        base = 0.74
    elif age < 60:
        base = 0.75
    else:
        base = 0.72

    city_adj = {"大都市": -0.10, "中都市": -0.05, "小都市": 0.00, "町村": 0.02}[city_size]
    p = np.clip(base + city_adj, 0.05, 0.95)
    return float(p)


# 子ども数（婚姻×年齢×都市サイズ）
def sample_children_count(rng, age, married, city_size):
    if not married:
        # 未婚は0がほとんど、少数の例外を入れない（必要なら調整）
        return 0

    # 既婚でも年齢が低いほど子ども少なめ
    if age < 27:
        w = np.array([0.80, 0.18, 0.02, 0.00])  # 0,1,2,3+
    elif age < 32:
        w = np.array([0.40, 0.40, 0.18, 0.02])
    elif age < 37:
        w = np.array([0.20, 0.40, 0.33, 0.07])
    elif age < 45:
        w = np.array([0.18, 0.32, 0.38, 0.12])
    else:
        w = np.array([0.22, 0.30, 0.34, 0.14])

    # 都市部は子ども数が少し少なめに補正
    if city_size == "大都市":
        w = w * np.array([1.30, 1.00, 0.80, 0.60])
    elif city_size == "町村":
        w = w * np.array([0.92, 1.00, 1.06, 1.12])

    w = w / w.sum()
    cat = rng.choice([0, 1, 2, 3], p=w)  # 3は「3人以上」扱い
    if cat == 3:
        # 3〜5に散らす（それっぽく）
        return int(rng.choice([3, 4, 5], p=[0.75, 0.20, 0.05]))
    return int(cat)


# 末子年齢（子ども数>0のときのみ、年齢と整合）
def sample_youngest_age(rng, age, children_count):
    if children_count <= 0:
        return np.nan

    # 親の年齢から見て、末子が成人しない範囲に寄せる
    # max_youngest は「親が18歳で出産した」仮定の上限
    max_youngest = max(0, age - 18)

    # 年齢が若い親ほど末子は小さい傾向
    if age < 30:
        a, b = 1.5, 6.0  # 小さめに寄る
    elif age < 40:
        a, b = 2.0, 3.5
    elif age < 50:
        a, b = 2.2, 2.2
    else:
        a, b = 2.8, 1.8  # やや大きめも出る

    # 0〜max_youngest の範囲にベータ分布で生成
    x = rng.beta(a, b)
    y = int(np.floor(x * (max_youngest + 1)))

    # 子どもが多いほど末子は若くなりやすい（軽い補正）
    if children_count >= 3:
        y = max(0, y - int(rng.integers(0, 3)))

    return float(min(y, max_youngest))


# 居住形態（賃貸/持ち家/実家）：年齢で遷移
def sample_housing(rng, age, married, city_size):
    # 実家は若年に寄せる
    if age < 25:
        w = np.array([0.70, 0.00, 0.30])  # 賃貸, 持ち家, 実家
    elif age < 30:
        w = np.array([0.65, 0.10, 0.25])
    elif age < 40:
        w = np.array([0.50, 0.40, 0.10])
    elif age < 50:
        w = np.array([0.30, 0.65, 0.05])
    else:
        w = np.array([0.25, 0.70, 0.05])

    # 都市部は賃貸寄り
    if city_size == "大都市":
        w = w * np.array([1.20, 0.80, 1.00])

    # 既婚は持ち家寄り
    if married:
        w = w * np.array([0.92, 1.10, 0.85])

    w = w / w.sum()
    return rng.choice(["賃貸", "持ち家", "実家"], p=w)


# 住宅ローン有無：持ち家の一部（年齢で変化）
def sample_mortgage(rng, housing, age):
    if housing != "持ち家":
        return False
    # 30-40代はローンありが多め、60代は完済が増える想定
    if age < 30:
        p = 0.70
    elif age < 40:
        p = 0.80
    elif age < 50:
        p = 0.70
    elif age < 60:
        p = 0.50
    else:
        p = 0.25
    return bool(rng.random() < p)


# -----------------------------
# 生成本体
# -----------------------------
def generate_synthetic_nurse_data(n=N, seed=SEED):
    rng = np.random.default_rng(seed)

    # 性別
    sex = rng.choice(["女性", "男性"], size=n, p=[P_FEMALE, 1 - P_FEMALE])

    # 年代→年齢
    age_band = rng.choice(AGE_BANDS, size=n, p=AGE_BAND_WEIGHTS)
    age = np.array([sample_age(rng, b) for b in age_band], dtype=int)

    # 都道府県
    pref = rng.choice(PREFS, size=n, p=PREF_WEIGHTS)

    # 都市サイズ（pref依存）
    city_size = np.array([sample_city_size(rng, p) for p in pref], dtype=object)

    # 婚姻
    married = np.array([rng.random() < married_prob(a, c) for a, c in zip(age, city_size, strict=True)], dtype=bool)

    # 子ども数
    children = np.array(
        [sample_children_count(rng, a, m, c) for a, m, c in zip(age, married, city_size, strict=True)], dtype=int
    )

    # 末子年齢
    youngest = np.array([sample_youngest_age(rng, a, k) for a, k in zip(age, children, strict=True)], dtype=float)

    # 居住形態
    housing = np.array([sample_housing(rng, a, m, c) for a, m, c in zip(age, married, city_size, strict=True)], dtype=object)

    # 住宅ローン
    mortgage = np.array([sample_mortgage(rng, h, a) for h, a in zip(housing, age, strict=True)], dtype=bool)

    df = pd.DataFrame(
        {
            "性別": sex,
            "年齢": age,
            "都道府県": pref,
            "都市サイズ": city_size,
            "居住形態": housing,  # 賃貸/持ち家/実家
            "住宅ローン有無": mortgage,  # True/False
            "婚姻": np.where(married, "既婚", "未婚"),
            "子ども数": children,
            "末子年齢": youngest,
        }
    )

    # 末子年齢がNaNのときは見た目を空欄にしたい場合（任意）
    # df["末子年齢"] = df["末子年齢"].astype("Int64")

    return df


def load_nurse_data_from_excel(
    file_path: str,
    sheet_name: str | int = 0,
    n: int | None = None,
    skip_rows: int = 0,
) -> pd.DataFrame:
    """
    Excelファイルから看護師属性データを読み込む

    Args:
        file_path: Excelファイルのパス
        sheet_name: シート名またはインデックス（デフォルト: 0 = 最初のシート）
        n: 読み込む行数（Noneの場合は全行）
        skip_rows: スキップする先頭行数（ヘッダー行は自動認識）

    Returns:
        pd.DataFrame: 看護師属性データ
            generate_synthetic_nurse_dataと同じカラム形式を想定:
            - 性別, 年齢, 都道府県, 都市サイズ, 居住形態,
            - 住宅ローン有無, 婚姻, 子ども数, 末子年齢

    Raises:
        FileNotFoundError: ファイルが見つからない場合
        ValueError: 必要なカラムが不足している場合
    """
    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        skiprows=skip_rows,
        nrows=n,
    )

    return df


# 実行例
if __name__ == "__main__":
    df = generate_synthetic_nurse_data(n=1000, seed=42)
    print(df.head(10))

    # CSV保存（Excelで文字化けしにくい）
    # df.to_csv("synthetic_nurses.csv", index=False, encoding="utf-8-sig")

    # Excel保存（推奨）
    df.to_excel("synthetic_nurses.xlsx", index=False)

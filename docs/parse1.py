import json

import pandas as pd


def get_choices(path):
    with open(path, "r", encoding="utf-8") as fh:
        result = json.load(fh)
    return result


def get_pairs(path):
    df = pd.read_csv(path, encoding="utf-8-sig")
    return df


def get_code(kv, val):
    for row in kv:
        k = row["id"]
        v = row["val"]
        if v == val:
            return k
    print("ERROR: not found.", kv, val)
    return None


def pairs_code(choices, df):
    choice_items = choices.keys()
    for item in choice_items:
        print(item)
        df[item] = [get_code(choices[item], k) for k in df[item]]
    print(df)


choices = get_choices("choices.json")
print(choices)
pairs = get_pairs("pairs.csv")
print(pairs)
pairs_code(choices, pairs)

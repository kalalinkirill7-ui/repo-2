"""Независимая проверка daily_by_sku.csv через pandas (нужен: pip install pandas)."""
import pandas as pd

raw = pd.read_csv("sales.csv", dtype=str, keep_default_na=False)
res = pd.read_csv("daily_by_sku.csv")

df = raw.drop_duplicates("order_id").copy()
df["status"] = df["status"].str.strip().str.lower().replace({"canceled": "cancelled"})
df["rev"] = 0
d = df["status"] == "delivered"
df.loc[d, "rev"] = df.loc[d, "quantity"].astype(int) * df.loc[d, "price"].astype(int)
exp = (df.groupby(["sku", "order_date"]).agg(orders=("order_id", "count"), revenue=("rev", "sum"))
         .reset_index())

assert exp.equals(res), "результат не совпал с pandas"
assert res["orders"].sum() == raw["order_id"].nunique(), "сумма orders != числу уникальных заказов"
assert res.equals(res.sort_values(["sku", "order_date"]).reset_index(drop=True)), "неверная сортировка"
print("OK: orders =", res["orders"].sum(), "revenue =", res["revenue"].sum())

"""Считает orders и revenue по паре «артикул - день» из sales.csv.

Запуск: python calc.py [входной_файл] [выходной_файл]
По умолчанию: sales.csv -> daily_by_sku.csv
"""
import csv
import sys
from collections import defaultdict

SRC = sys.argv[1] if len(sys.argv) > 1 else "sales.csv"
DST = sys.argv[2] if len(sys.argv) > 2 else "daily_by_sku.csv"


def normalize_status(raw):
    """Приводит статус к 'delivered' / 'cancelled' (регистр, пробелы, 'canceled')."""
    s = raw.strip().lower()
    if s == "canceled":
        s = "cancelled"
    if s not in ("delivered", "cancelled"):
        raise ValueError(f"неизвестный статус: {raw!r}")
    return s


def main():
    seen = {}  # order_id -> строка, для удаления дублей
    stats = defaultdict(lambda: {"orders": 0, "revenue": 0})
    dup_count = 0

    with open(SRC, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            order_id = row["order_id"].strip()
            sku = row["sku"].strip()
            date = row["order_date"].strip()
            status = normalize_status(row["status"])
            key_data = (sku, date, row["quantity"].strip(), row["price"].strip(), status)

            if order_id in seen:
                dup_count += 1
                if seen[order_id] != key_data:
                    print(f"ВНИМАНИЕ: заказ {order_id} дублируется с разными данными", file=sys.stderr)
                continue
            seen[order_id] = key_data

            item = stats[(sku, date)]
            item["orders"] += 1
            if status == "delivered":
                # quantity пустой только у отменённых, но здесь он обязателен
                item["revenue"] += int(row["quantity"]) * int(row["price"])

    with open(DST, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["sku", "order_date", "orders", "revenue"])
        for (sku, date) in sorted(stats):
            w.writerow([sku, date, stats[(sku, date)]["orders"], stats[(sku, date)]["revenue"]])

    print(f"Строк в выгрузке: {len(seen) + dup_count}, дублей убрано: {dup_count}, "
          f"уникальных заказов: {len(seen)}, строк в результате: {len(stats)}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def load_data(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() in {".parquet", ".pq"}:
        df = pd.read_parquet(path)
    else:
        raise ValueError("仅支持 .csv 或 .parquet/.pq")

    df["trade_date"] = pd.to_datetime(df["trade_date"])
    return df.sort_values("trade_date").reset_index(drop=True)


def build_report_row(df: pd.DataFrame) -> dict:
    last = df.iloc[-1]
    state = "站上MA200" if bool(last.get("above_ma200", False)) else "跌破MA200"

    return {
        "date": last["trade_date"].date().isoformat(),
        "symbol": last.get("symbol", "UNKNOWN"),
        "close": round(float(last["close"]), 4),
        "ma200": round(float(last.get("ma200", float("nan"))), 4),
        "state": state,
        "streak_days": int(last.get("streak", 0)),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="输出最近一天的趋势状态摘要")
    p.add_argument("--input", default="data/etf_daily_with_indicators.csv")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    df = load_data(Path(args.input))
    summary = build_report_row(df)
    print("ETF 趋势摘要:")
    for k, v in summary.items():
        print(f"- {k}: {v}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
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


def add_moving_averages(df: pd.DataFrame, windows: tuple[int, ...] = (20, 60, 120, 200)) -> pd.DataFrame:
    out = df.copy()
    for w in windows:
        out[f"ma{w}"] = out["close"].rolling(window=w).mean()
    return out


def add_trend_state(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["above_ma200"] = out["close"] > out["ma200"]
    out["signal"] = np.where(out["above_ma200"], 1, 0)
    groups = (out["signal"] != out["signal"].shift()).cumsum()
    out["streak"] = out.groupby(groups).cumcount() + 1
    return out


def save_data(df: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.suffix.lower() == ".csv":
        df.to_csv(output, index=False)
    elif output.suffix.lower() in {".parquet", ".pq"}:
        df.to_parquet(output, index=False)
    else:
        raise ValueError("仅支持 .csv 或 .parquet/.pq")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="计算 ETF MA20/60/120/200 与趋势状态")
    p.add_argument("--input", default="data/etf_daily.csv")
    p.add_argument("--output", default="data/etf_daily_with_indicators.csv")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    df = load_data(Path(args.input))
    df = add_moving_averages(df)
    df = add_trend_state(df)
    save_data(df, Path(args.output))
    print(df.tail(5)[["trade_date", "close", "ma200", "above_ma200", "streak"]])


if __name__ == "__main__":
    main()

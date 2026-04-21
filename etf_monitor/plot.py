from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
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


def draw_chart(df: pd.DataFrame, output: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(df["trade_date"], df["close"], label="Close", linewidth=1.4)
    if "ma200" in df.columns:
        ax.plot(df["trade_date"], df["ma200"], label="MA200", linewidth=1.2)

    if "above_ma200" in df.columns:
        below = df[~df["above_ma200"] & df["ma200"].notna()]
        ax.scatter(below["trade_date"], below["close"], s=10, alpha=0.5, label="Below MA200")

    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.grid(alpha=0.25)
    ax.legend()

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=160)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="画 ETF Close 与 MA200 趋势图")
    p.add_argument("--input", default="data/etf_daily_with_indicators.csv")
    p.add_argument("--output", default="reports/etf_trend.png")
    p.add_argument("--title", default="ETF Close vs MA200")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    df = load_data(Path(args.input))
    draw_chart(df, Path(args.output), args.title)
    print(f"图表已输出: {args.output}")


if __name__ == "__main__":
    main()

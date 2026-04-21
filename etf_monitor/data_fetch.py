from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def fetch_with_akshare(symbol: str, adjust: str = "qfq") -> pd.DataFrame:
    """Fetch ETF daily bars from AKShare (Eastmoney source)."""
    import akshare as ak

    df = ak.fund_etf_hist_em(symbol=symbol, period="daily", adjust=adjust)
    rename_map = {
        "日期": "trade_date",
        "开盘": "open",
        "收盘": "close",
        "最高": "high",
        "最低": "low",
        "成交量": "volume",
        "成交额": "amount",
    }
    missing = [k for k in rename_map if k not in df.columns]
    if missing:
        raise ValueError(f"AKShare 返回字段与预期不一致，缺少: {missing}")

    out = df.rename(columns=rename_map)[list(rename_map.values())].copy()
    out["trade_date"] = pd.to_datetime(out["trade_date"])
    out = out.sort_values("trade_date").reset_index(drop=True)
    return out


def fetch_with_tushare(ts_code: str, start_date: str, end_date: str, token: str) -> pd.DataFrame:
    """Fetch ETF daily bars from Tushare pro.fund_daily."""
    import tushare as ts

    ts.set_token(token)
    pro = ts.pro_api()
    df = pro.fund_daily(
        ts_code=ts_code,
        start_date=start_date,
        end_date=end_date,
        fields="ts_code,trade_date,open,high,low,close,vol,amount",
    )
    out = df.rename(columns={"vol": "volume"}).copy()
    out["trade_date"] = pd.to_datetime(out["trade_date"])
    out = out.sort_values("trade_date").reset_index(drop=True)
    return out[["trade_date", "open", "high", "low", "close", "volume", "amount"]]


def save_data(df: pd.DataFrame, output: Path, symbol: str) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    df = df.copy()
    df.insert(0, "symbol", symbol)
    if output.suffix.lower() == ".csv":
        df.to_csv(output, index=False)
    elif output.suffix.lower() in {".parquet", ".pq"}:
        df.to_parquet(output, index=False)
    else:
        raise ValueError("仅支持 .csv 或 .parquet/.pq 输出")
    return output


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="下载 ETF 日线数据到本地")
    p.add_argument("--source", choices=["akshare", "tushare"], default="akshare")
    p.add_argument("--symbol", required=True, help="AKShare 用6位代码，例如 159865")
    p.add_argument("--output", default="data/etf_daily.csv", help="输出路径 .csv/.parquet")
    p.add_argument("--adjust", default="qfq", help="AKShare复权参数: qfq/hfq/''")

    p.add_argument("--ts-code", help="Tushare 代码，例如 159865.SZ")
    p.add_argument("--start-date", default="20200101", help="Tushare 起始日期 YYYYMMDD")
    p.add_argument("--end-date", default=pd.Timestamp.today().strftime("%Y%m%d"))
    p.add_argument("--tushare-token", help="Tushare token")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    output = Path(args.output)

    if args.source == "akshare":
        df = fetch_with_akshare(args.symbol, adjust=args.adjust)
        saved = save_data(df, output, args.symbol)
    else:
        if not (args.ts_code and args.tushare_token):
            raise ValueError("使用 tushare 时必须提供 --ts-code 和 --tushare-token")
        df = fetch_with_tushare(
            ts_code=args.ts_code,
            start_date=args.start_date,
            end_date=args.end_date,
            token=args.tushare_token,
        )
        saved = save_data(df, output, args.ts_code)

    print(f"已保存 {len(df)} 行到: {saved}")


if __name__ == "__main__":
    main()

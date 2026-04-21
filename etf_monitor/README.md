# ETF MA200 本地监控脚手架

一个最小可运行的本地系统，覆盖 4 个脚本：

- `data_fetch.py`：拉取 ETF 日线（AKShare / Tushare）
- `indicators.py`：计算 MA20/60/120/200 + 趋势状态
- `plot.py`：输出 Close vs MA200 趋势图
- `monitor.py`：输出最近一天趋势摘要（是否站上 MA200、连续天数）

## 环境

```bash
pip install pandas numpy matplotlib akshare tushare pyarrow
```

> 若仅使用 AKShare，可先不装 `tushare`。

## 快速开始（AKShare）

1) 下载 ETF 日线到本地 CSV：

```bash
python etf_monitor/data_fetch.py --source akshare --symbol 159865 --output data/etf_daily.csv
```

2) 计算指标：

```bash
python etf_monitor/indicators.py --input data/etf_daily.csv --output data/etf_daily_with_indicators.csv
```

3) 画图：

```bash
python etf_monitor/plot.py --input data/etf_daily_with_indicators.csv --output reports/etf_trend.png --title "159865 Close vs MA200"
```

4) 查看最新状态：

```bash
python etf_monitor/monitor.py --input data/etf_daily_with_indicators.csv
```

## Tushare 用法

```bash
python etf_monitor/data_fetch.py \
  --source tushare \
  --symbol 159865 \
  --ts-code 159865.SZ \
  --start-date 20200101 \
  --end-date 20260421 \
  --tushare-token <YOUR_TOKEN> \
  --output data/etf_daily.csv
```

## 定时建议

- A 股 ETF 建议在交易日 `15:10` 之后调度。
- 可使用 cron / Windows 任务计划。

示例 cron（工作日 15:15）：

```cron
15 15 * * 1-5 cd /path/to/Tools && python etf_monitor/data_fetch.py --source akshare --symbol 159865 --output data/etf_daily.csv && python etf_monitor/indicators.py --input data/etf_daily.csv --output data/etf_daily_with_indicators.csv && python etf_monitor/plot.py --input data/etf_daily_with_indicators.csv --output reports/etf_trend.png && python etf_monitor/monitor.py --input data/etf_daily_with_indicators.csv
```

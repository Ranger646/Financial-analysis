# 全球金融指标实时可视化工具

这是一个**轻量级单页仪表盘**，用于快速观察全球主要金融资产的实时变化，帮助你分析当前经济环境。

## 为什么之前会出现 “Failed to fetch”

之前前端直接在浏览器里请求 Yahoo Finance 接口，容易触发跨域限制（CORS）或被上游拦截，因此会显示 `Failed to fetch`。

现在已改为：
- 浏览器请求本地同源接口 `/api/quotes`
- 本地 Python 服务端再去请求 Yahoo Finance

这样可以规避浏览器跨域限制，显著降低 `Failed to fetch` 的概率。

## 功能

- 一屏查看核心资产：
  - 美股/欧股/亚股主要指数
  - 主要汇率（EURUSD、USDJPY）
  - 大宗商品（黄金、原油）
  - 美国 10Y 国债收益率
  - 加密资产（BTC）
- 自动刷新（每 60 秒）+ 手动立即刷新
- 可切换互动图表（TradingView）进行细看

## 使用方式（推荐）

1. 在仓库根目录启动服务：

   ```bash
   python app.py
   ```

2. 浏览器访问：

   ```
   http://localhost:8080
   ```

## 数据来源

- 行情卡片：Yahoo Finance Quote API（通过本地代理转发）
- 互动图表：TradingView Embed

> 说明：行情数据可用性与更新频率取决于数据源与网络环境。

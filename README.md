---
title: 外贸助手
emoji: 🌐
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# 🌐 外贸助手 (Trade Assistant)

基于 Streamlit 的外贸市场调研工具，帮助外贸从业者快速搜索目标国家的潜在客户。

## 功能

- **客户搜索**：输入国家和商品，搜索中大型城市的在售店铺，获取地址、电话、邮箱等联系方式
- **搜索结果**：表格展示，支持 WhatsApp/Telegram/邮件一键联系
- **竞品分析**：分析目标市场的竞品、销售渠道、年度趋势
- **90天增长计划**：基于单位经济和渠道策略，生成三阶段执行方案
- **广告投放指南**：Meta/Google/TikTok 三大平台投放要点
- **中英双语**：界面支持中文/英文切换

## 使用

1. 在左侧菜单选择功能模块
2. 输入目标国家、城市（可选）、商品名称
3. 点击搜索按钮，等待结果（通常 30-60 秒）
4. 在搜索结果页查看表格，点击 WhatsApp/Telegram/邮件按钮直接联系客户

## 技术栈

- Streamlit 1.67
- Python 3.11
- Docker
- 数据来源：DuckDuckGo / Bing / OpenStreetMap / eBay（免费公开数据）

## 隐私

- 不收集用户数据
- Serper API Key（可选）仅保存在本地 config.json，不外传
- 所有搜索通过公开 API 完成，无付费墙

"""
外贸助手 - 侧边栏布局完整版

左侧菜单：
1. 客户搜索（店铺查找 + 销售统计）
2. 搜索结果
3. 使用提示（子菜单）
4. 设置（子菜单，含语言切换 + 代理勾选）
"""

import json
import time
from pathlib import Path
from urllib.parse import quote_plus

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from search_engine import SearchEngine, ProxyConfig
from shop_finder import ShopFinder
from sales_stats import SalesStats
from competitor_analysis import analyze_competitors, CompetitorReport
from growth_plan import generate_growth_plan, GrowthPlanInput
from cities import get_country_list, get_cities, COUNTRIES, get_country_en, get_country_code
from phone_utils import format_phone
from exporter import export_file

# ===== 页面配置 =====
st.set_page_config(
    page_title="Trade Assistant" if st.session_state.get("lang", "zh") == "en" else "外贸助手",
    page_icon="🌐",
    layout="wide",
)

# ===== 语言 =====
if "lang" not in st.session_state or st.session_state.lang not in ("zh", "en"):
    st.session_state.lang = "zh"

LANG = st.session_state.lang

I18N = {
    "zh": {
        "sidebar_title": "🌐 外贸助手",
        "menu_market": "客户搜索",
        "menu_results": "搜索结果",
        "menu_tips": "使用提示",
        "menu_settings": "设置",
        "lang_switch": "语言切换",
        "lang_zh": "中文",
        "lang_en": "English",
        "setting_proxy": "代理设置",
        "setting_proxy_hint": "勾选后使用本地代理（如 Clash/V2Ray）",
        "setting_proxy_on": "✅ 代理已启用",
        "setting_proxy_off": "⚪ 代理未启用",
        "tip_title": "💡 使用提示",
        "tip1": "- 商品名支持中英文",
        "tip2": "- 城市可选，不选则搜全国主要城市",
        "tip3": "- 搜索需要时间，请耐心等待",
        "tip4": "- 若文字被翻译插件改写，请关闭该插件",
        "tab_shop": "🏪 店铺查找",
        "tab_stats": "📊 销售统计",
        "country": "🌍 选择国家",
        "city": "🏙️ 选择城市（可选）",
        "city_all_opt": "🌐 全部城市",
        "city_input_ph": "直接输入城市名（如：横滨、名古屋）",
        "city_select": "或从列表选择",
        "all_cities": "（全部主要城市）",
        "manual_city_opt": "✏️ 手动输入...",
        "manual_city_label": "输入城市名",
        "manual_city_ph": "例如：横滨、名古屋、札幌...",
        "city_help": "可从列表选择，或选「手动输入」输入任意城市名",
        "product": "📦 输入商品名称",
        "product_ph": "例如：蓝牙耳机、LED 灯、服装...",
        "search": "🔍 开始搜索",
        "num_cities": "全国城市数",
        "searching": "正在搜索，请稍候...",
        "found": "✅ 找到 ",
        "found_tail": " 家店铺",
        "total": "店铺总数",
        "has_phone": "有电话",
        "has_email": "有邮箱",
        "has_addr": "有地址",
        "filter_hint": "👆 点击上方卡片可筛选",
        "current_filter": "当前筛选：",
        "shop_list": "📋 店铺列表",
        "map_btn": "📍 地图",
        "contact_person": "👤 联系人：",
        "phone": "📞 电话：",
        "email": "📧 邮箱：",
        "address": "🏠 地址：",
        "no_contact": "⚠️ 暂未获取到联系方式",
        "website": "🔗 网站",
        "detail": "📄 详情",
        "no_shops_filter": "当前筛选条件下没有店铺。",
        "map_header": "🗺️ 地图定位",
        "map_hint": "💡 点击左侧「📍 地图」按钮可定位",
        "no_geo": "📍 暂无店铺的坐标信息",
        "input_product_warn": "⚠️ 请输入商品名称",
        "stats_header": "📊 商品销售热度分析",
        "stats_product_ph": "例如：手机壳、咖啡机、运动鞋...",
        "stats_city_ph": "输入城市名（如：东京、大阪），留空则统计全省市",
        "stats_city_select": "或从列表选择",
        "metric_desc_title": "📊 统计指标说明",
        "metric_result_count": "🔍 搜索结果条数",
        "metric_result_count_desc": "网上关于该商品的搜索结果多少条，反映市场关注度",
        "metric_shop_count": "🏪 涉及店铺数",
        "metric_shop_count_desc": "有多少不同的店铺/域名在销售该商品",
        "metric_platform_count": "🛒 涉及电商平台数",
        "metric_platform_count_desc": "Amazon、eBay、Rakuten 等电商平台出现的数量",
        "metric_price_mentions": "💰 价格提及数",
        "metric_price_mentions_desc": "有多少条结果提到了价格，并抓取抽样价格",
        "stats_cities": "分析城市数",
        "stats_btn": "📊 开始分析",
        "analyzing": "正在分析，请稍候...",
        "stats_done": "✅ 分析完成：",
        "stats_total": " 共 ",
        "stats_total_tail": " 条搜索结果",
        "heat_header": "🌡️ 各城市销售热度",
        "heat_score": "热度分数",
        "detail_data": "📋 详细数据",
        "heat": "热度",
        "search_results": "搜索结果",
        "shops": "涉及店铺",
        "platforms": "电商平台",
        "prices": "价格提及",
        "top_cities": "🎯 主要销售城市推荐",
        "export": "📤 导出",
        "export_format": "导出格式",
        "excel_opt": "Excel 表格（.xlsx）",
        "pdf_opt": "PDF 文件（.pdf）",
        "exported": "✅ 已导出",
        "no_results_export": "⚠️ 还没有搜索结果",
        "contact_whatsapp": "WhatsApp",
        "contact_telegram": "Telegram",
        "contact_email": "发邮件",
        "menu_competitor": "竞品分析",
        "menu_growth": "90天增长计划",
        "menu_ads": "广告投放",
        "page_title": "外贸助手",
        "tab_country": "按国家",
        "tab_city": "按城市",
        "shop_count_unit": "家",
        "no_results": "暂无搜索结果。请先在「客户搜索」中搜索。",
        "stopped": "⏹ 已停止",
        "gp_alloc_channel": "渠道",
        "gp_alloc_pct": "占比",
        "gp_alloc_monthly": "月预算",
        "col_name": "商家",
        "col_city": "城市",
        "col_phone": "电话",
        "col_address": "地址",
        "col_email_hdr": "邮箱地址",
        "stop": "⏹ 停止",
        "col_wa": "WHATSAPP",
        "col_tg": "TELEGRAM",
        "col_email": "邮件",
        "ads_header": "📢 广告投放（Meta / Google / TikTok）",
        "ads_note": "💡 基于出海营销最佳实践：选择平台查看投放搭建、测试与放量规则、常见误区、追踪与合规要点",
        "ads_tab_meta": "📘 Meta 广告",
        "ads_tab_google": "🔴 Google 广告",
        "ads_tab_tiktok": "🎵 TikTok 广告",
        "ads_tab_tracking": "📊 追踪配置",
        "ads_tab_compliance": "🛡️ 合规防封",
        "ads_footer": "⚠️ 平台功能与政策变化频繁，具体操作以各广告管理工具当前界面和最新政策页为准。",
        "comp_header": "🎯 市场竞品分析",
        "comp_product_ph": "输入商品名称（如：phone case）",
        "comp_city_ph": "输入城市名，留空则分析全国",
        "comp_years": "分析年份数",
        "comp_period": "分析时间段",
        "comp_start": "开始",
        "comp_end": "结束",
        "comp_btn": "🎯 开始竞品分析",
        "comp_done": "✅ 竞品分析完成：",
        "comp_total_tail": " 条市场信息",
        "comp_sources": "数据来源",
        "comp_note": "💡 说明：本模块基于公开网页的免费数据做统计推断（提及频次、在售商品），不涉及精确销售额。年份/月份的数值反映市场关注度，非官方销量。",
        "comp_date_err": "⚠️ 结束时间不能早于开始时间",
        "gp_tab": "📋 90天增长计划",
        "comp_tab": "🎯 市场竞品分析",
        "gp_header": "📋 90天海外增长计划",
        "gp_note": "💡 填写产品和预算信息，生成 90 天增长方案（含单位经济、渠道选择、三阶段执行计划）",
        "gp_price": "💰 售价（美元）",
        "gp_cost": "📦 产品成本（美元/件）",
        "gp_shipping": "🚢 运费（美元/件）",
        "gp_tariff": "🏛️ 关税（美元/件）",
        "gp_budget": "💵 每月营销预算（美元）",
        "gp_stage": "📊 当前阶段",
        "gp_stage_idea": "想法阶段（还没有销量）",
        "gp_stage_early": "早期销量（刚开始有订单）",
        "gp_stage_scaling": "放量阶段（要加大投入）",
        "gp_btype": "🎯 业务类型",
        "gp_btype_impulse": "冲动型 B2C（视觉化、冲动消费）",
        "gp_btype_decision": "决策型 B2C（用户主动搜索）",
        "gp_btype_b2b": "B2B（批发/经销商/合作）",
        "gp_btype_tiktok": "内容型 B2C（适合演示、35岁以下）",
        "gp_btn": "📋 生成 90 天增长计划",
        "gp_unit_econ": "💰 单位经济",
        "gp_ue_price": "售价",
        "gp_ue_cost": "总成本",
        "gp_ue_profit": "毛利",
        "gp_ue_margin": "毛利率",
        "gp_ue_broas": "保本 ROAS",
        "gp_ue_troas": "目标 ROAS",
        "gp_ue_tcpa": "目标 CPA",
        "gp_channel": "🎯 推荐主渠道",
        "gp_channel_reason": "推荐理由",
        "gp_channel_skill": "对应技能",
        "gp_budget_alloc": "💵 预算分配",
        "gp_phases": "📅 90 天三阶段计划",
        "gp_phase": "阶段",
        "gp_days": "时间",
        "gp_goal": "目标",
        "gp_actions": "执行动作",
        "gp_budget_pct": "预算占比",
        "gp_kpi": "KPI",
        "gp_top3": "⚡ 本周要做的前三件事",
        "gp_research": "🔍 市场调研清单（14 天验证）",
        "gp_compliance": "⚖️ 合规提示",
        "gp_none": "⚠️ 请填写售价、成本和预算",
        "comp_competitors": "🏆 主要竞品（品牌/卖家/网站）",
        "comp_comp_name": "名称",
        "comp_comp_type": "类型",
        "comp_comp_count": "提及次数",
        "comp_channels": "🛒 销售渠道分布",
        "comp_channel_name": "渠道",
        "comp_channel_count": "出现次数",
        "comp_channel_pct": "占比 %",
        "comp_yearly": "📈 近几年市场关注度",
        "comp_year": "年份",
        "comp_mentions": "提及次数",
        "comp_models": "🔥 热销型号 / 单价",
        "comp_model": "型号",
        "comp_model_count": "出现次数",
        "comp_avg_price": "平均单价",
        "comp_price_stats": "💰 单价统计（基于在售商品）",
        "comp_price_count": "样本数",
        "comp_price_min": "最低",
        "comp_price_max": "最高",
        "comp_price_avg": "平均",
        "comp_price_median": "中位",
        "comp_monthly": "📅 月度销售热度（淡旺季）",
        "comp_month": "月份",
        "comp_peak": "旺季月份",
        "comp_off": "淡季月份",
        "comp_reasons": "🔍 旺季/淡季成因（基于文章关键词统计）",
        "comp_reason": "原因",
        "comp_reason_count": "关键词出现次数",
        "comp_queries_used": "搜索关键词",
        "comp_none": "⚠️ 未获取到有效数据，请检查网络/代理或换关键词",
        "footer": "🌐 外贸助手 · 数据来源：DuckDuckGo / Bing / OpenStreetMap · 仅供参考",
    },
    "en": {
        "sidebar_title": "🌐 Trade Assistant",
        "menu_market": "Customer Search",
        "menu_results": "Search Results",
        "menu_tips": "Usage Tips",
        "menu_settings": "Settings",
        "lang_switch": "Language",
        "lang_zh": "中文",
        "lang_en": "English",
        "setting_proxy": "Proxy Settings",
        "setting_proxy_hint": "Enable to use local proxy (e.g. Clash/V2Ray)",
        "setting_proxy_on": "✅ Proxy Enabled",
        "setting_proxy_off": "⚪ Proxy Disabled",
        "tip_title": "💡 Tips",
        "tip1": "- Product name supports EN/CN",
        "tip2": "- City optional; if empty, searches major cities nationwide",
        "tip3": "- Search takes time, please be patient",
        "tip4": "- Close translation extension if it rewrites text",
        "tab_shop": "🏪 Shop Finder",
        "tab_stats": "📊 Sales Stats",
        "country": "🌍 Country",
        "city": "🏙️ City (optional)",
        "city_all_opt": "🌐 All cities",
        "city_input_ph": "Type a city name (e.g. Yokohama, Nagoya)",
        "city_select": "Or select from list",
        "all_cities": "All major cities",
        "manual_city_opt": "✏️ Manual input...",
        "manual_city_label": "Enter city name",
        "manual_city_ph": "e.g. Yokohama, Nagoya, Sapporo...",
        "city_help": "Select from list, or choose 'Manual input' to type any city",
        "product": "📦 Product name",
        "product_ph": "e.g. Bluetooth headset, LED lights, apparel...",
        "search": "🔍 Search",
        "num_cities": "Number of cities",
        "searching": "Searching, please wait...",
        "found": "✅ Found ",
        "found_tail": " shops",
        "total": "Total Shops",
        "has_phone": "Has Phone",
        "has_email": "Has Email",
        "has_addr": "Has Address",
        "filter_hint": "👆 Click cards above to filter",
        "current_filter": "Current filter: ",
        "shop_list": "📋 Shop List",
        "map_btn": "📍 Map",
        "contact_person": "👤 Contact: ",
        "phone": "📞 Phone: ",
        "email": "📧 Email: ",
        "address": "🏠 Address: ",
        "no_contact": "⚠️ No contact info yet",
        "website": "🔗 Website",
        "detail": "📄 Details",
        "no_shops_filter": "No shops under current filter.",
        "map_header": "🗺️ Map",
        "map_hint": "💡 Click the '📍 Map' button to locate a shop",
        "no_geo": "📍 No coordinates for shops yet",
        "input_product_warn": "⚠️ Please enter a product name",
        "stats_header": "📊 Sales Heat Analysis",
        "stats_product_ph": "e.g. phone case, coffee machine, sneakers...",
        "stats_city_ph": "Type a city name (e.g. Tokyo, Osaka). Leave blank to analyze all cities",
        "stats_city_select": "Or select from list",
        "metric_desc_title": "📊 Metric Explanations",
        "metric_result_count": "🔍 Search Results",
        "metric_result_count_desc": "Number of search results for this product online, reflecting market attention",
        "metric_shop_count": "🏪 Shops Involved",
        "metric_shop_count_desc": "Number of different shops/domains selling this product",
        "metric_platform_count": "🛒 E-commerce Platforms",
        "metric_platform_count_desc": "Number of platforms like Amazon, eBay, Rakuten appearing in results",
        "metric_price_mentions": "💰 Price Mentions",
        "metric_price_mentions_desc": "Number of results mentioning prices, with sampled prices captured",
        "stats_btn": "📊 Analyze",
        "stats_cities": "Cities to analyze",
        "analyzing": "Analyzing, please wait...",
        "stats_done": "✅ Analysis complete: ",
        "stats_total": " Total ",
        "stats_total_tail": " results",
        "heat_header": "🌡️ Sales Heat by City",
        "heat_score": "Heat Score",
        "detail_data": "📋 Detailed Data",
        "heat": "Heat",
        "search_results": "Results",
        "shops": "Shops",
        "platforms": "Platforms",
        "prices": "Price Mentions",
        "top_cities": "🎯 Recommended Cities",
        "export": "📤 Export",
        "export_format": "Format",
        "excel_opt": "Excel (.xlsx)",
        "pdf_opt": "PDF (.pdf)",
        "exported": "✅ Exported",
        "no_results_export": "⚠️ No results yet",
        "contact_whatsapp": "WhatsApp",
        "contact_telegram": "Telegram",
        "contact_email": "Email",
        "menu_competitor": "Competitor Analysis",
        "menu_growth": "90-Day Growth Plan",
        "menu_ads": "Paid Ads",
        "page_title": "Trade Assistant",
        "tab_country": "By Country",
        "tab_city": "By City",
        "shop_count_unit": "",
        "no_results": "No search results yet. Please search in 'Customer Search' first.",
        "stopped": "⏹ Stopped",
        "gp_alloc_channel": "Channel",
        "gp_alloc_pct": "Share",
        "gp_alloc_monthly": "Monthly Budget",
        "col_name": "Shop",
        "col_city": "City",
        "col_phone": "Phone",
        "col_address": "Address",
        "col_email_hdr": "Email",
        "stop": "⏹ Stop",
        "col_wa": "WHATSAPP",
        "col_tg": "TELEGRAM",
        "col_email": "EMAIL",
        "ads_header": "📢 Paid Ads (Meta / Google / TikTok)",
        "ads_note": "💡 Based on overseas growth best practices: select a platform to view campaign setup, testing & scaling rules, common pitfalls, tracking, and compliance essentials.",
        "ads_tab_meta": "📘 Meta Ads",
        "ads_tab_google": "🔴 Google Ads",
        "ads_tab_tiktok": "🎵 TikTok Ads",
        "ads_tab_tracking": "📊 Tracking Setup",
        "ads_tab_compliance": "🛡️ Compliance & Ban Prevention",
        "ads_footer": "⚠️ Platform features and policies change frequently. Always refer to the current ad manager interface and latest policy pages.",
        "comp_header": "🎯 Market Competitor Analysis",
        "comp_product_ph": "Enter product name (e.g. phone case)",
        "comp_city_ph": "Enter city name, leave blank for nationwide",
        "comp_years": "Years to analyze",
        "comp_period": "Analysis Period",
        "comp_start": "Start",
        "comp_end": "End",
        "comp_btn": "🎯 Start Competitor Analysis",
        "comp_done": "✅ Competitor analysis complete:",
        "comp_total_tail": " market signals",
        "comp_sources": "Data Sources",
        "comp_note": "💡 Note: This module makes statistical inferences from free public web data (mention frequency, live listings). It does not involve exact sales revenue. Year/month values reflect market attention, not official sales.",
        "comp_date_err": "⚠️ End date cannot be earlier than start date",
        "gp_tab": "📋 90-Day Growth Plan",
        "comp_tab": "🎯 Market Competitor Analysis",
        "gp_header": "📋 90-Day Overseas Growth Plan",
        "gp_note": "💡 Fill in product and budget info to generate a 90-day growth plan (unit economics, channel selection, 3-phase execution).",
        "gp_price": "💰 Price (USD)",
        "gp_cost": "📦 Product Cost (USD/unit)",
        "gp_shipping": "🚢 Shipping (USD/unit)",
        "gp_tariff": "🏛️ Tariff (USD/unit)",
        "gp_budget": "💵 Monthly Marketing Budget (USD)",
        "gp_stage": "📊 Current Stage",
        "gp_stage_idea": "Idea (no sales yet)",
        "gp_stage_early": "Early Sales (just got orders)",
        "gp_stage_scaling": "Scaling (ready to invest more)",
        "gp_btype": "🎯 Business Type",
        "gp_btype_impulse": "Impulse B2C (visual, impulse purchase)",
        "gp_btype_decision": "Decision B2C (users actively search)",
        "gp_btype_b2b": "B2B (wholesale / distributor / partnership)",
        "gp_btype_tiktok": "Content B2C (demo-friendly, under 35)",
        "gp_btn": "📋 Generate 90-Day Growth Plan",
        "gp_unit_econ": "💰 Unit Economics",
        "gp_ue_price": "Price",
        "gp_ue_cost": "Total Cost",
        "gp_ue_profit": "Gross Profit",
        "gp_ue_margin": "Gross Margin",
        "gp_ue_broas": "Breakeven ROAS",
        "gp_ue_troas": "Target ROAS",
        "gp_ue_tcpa": "Target CPA",
        "gp_channel": "🎯 Recommended Primary Channel",
        "gp_channel_reason": "Reason",
        "gp_channel_skill": "Skill Ref",
        "gp_budget_alloc": "💵 Budget Allocation",
        "gp_phases": "📅 90-Day 3-Phase Plan",
        "gp_phase": "Phase",
        "gp_days": "Time",
        "gp_goal": "Goal",
        "gp_actions": "Actions",
        "gp_budget_pct": "Budget %",
        "gp_kpi": "KPI",
        "gp_top3": "⚡ Top 3 Actions This Week",
        "gp_research": "🔍 Market Research Checklist (14-Day Validation)",
        "gp_compliance": "⚖️ Compliance Notes",
        "gp_none": "⚠️ Please fill in price, cost, and budget",
        "comp_competitors": "🏆 Key Competitors (Brands / Sellers / Sites)",
        "comp_comp_name": "Name",
        "comp_comp_type": "Type",
        "comp_comp_count": "Mentions",
        "comp_channels": "🛒 Sales Channel Distribution",
        "comp_channel_name": "Channel",
        "comp_channel_count": "Appearances",
        "comp_channel_pct": "Share %",
        "comp_yearly": "📈 Market Attention by Year",
        "comp_year": "Year",
        "comp_mentions": "Mentions",
        "comp_models": "🔥 Top Models / Prices",
        "comp_model": "Model",
        "comp_model_count": "Appearances",
        "comp_avg_price": "Avg Price",
        "comp_price_stats": "💰 Price Stats (live listings)",
        "comp_price_count": "Samples",
        "comp_price_min": "Min",
        "comp_price_max": "Max",
        "comp_price_avg": "Avg",
        "comp_price_median": "Median",
        "comp_monthly": "📅 Monthly Sales Heat (Peak/Off Season)",
        "comp_month": "Month",
        "comp_peak": "Peak Months",
        "comp_off": "Off-Season Months",
        "comp_reasons": "🔍 Peak/Off-Season Causes (article keyword stats)",
        "comp_reason": "Cause",
        "comp_reason_count": "Keyword Count",
        "comp_queries_used": "Search Queries",
        "comp_none": "⚠️ No valid data. Check network/proxy or try different keywords.",
        "footer": "🌐 Trade Assistant · Sources: DuckDuckGo / Bing / OpenStreetMap · For reference only",
    },
}


def T(key):
    return I18N[LANG].get(key, I18N["zh"].get(key, key))


def country_display(zh):
    if LANG == "en":
        return COUNTRIES.get(zh, {}).get("en", zh)
    return zh


def city_display(pair):
    zh, en = pair
    return en if LANG == "en" else zh


# 竞品报告字段的中英映射（报告数据内部存中文，英文模式转英文显示）
_COMP_TYPE_EN = {"品牌": "Brand", "网站": "Website", "eBay卖家": "eBay Seller"}
_MONTH_EN = ["January", "February", "March", "April", "May", "June", "July",
             "August", "September", "October", "November", "December"]
_MONTH_ZH = [f"{i}月" for i in range(1, 13)]
_SEASON_EN = {
    "节假日/购物季": "Holiday / Shopping Season",
    "返校/开学季": "Back to School",
    "夏季旺季": "Summer Peak",
    "冬季旺季": "Winter Peak",
    "促销活动": "Promotions",
    "新品发布": "New Releases",
    "换季": "Seasonal Change",
}


def _month_disp(m_zh):
    """月份中文转英文显示"""
    if LANG != "en":
        return m_zh
    if m_zh in _MONTH_ZH:
        return _MONTH_EN[_MONTH_ZH.index(m_zh)]
    return m_zh


def _comp_type_disp(t):
    return _COMP_TYPE_EN.get(t, t) if LANG == "en" else t


def _season_disp(r):
    return _SEASON_EN.get(r, r) if LANG == "en" else r


def shop_city_display(city_zh, country_zh):
    """按当前语言显示店铺城市名（数据存中文，英文模式转英文）"""
    if LANG != "en":
        return city_zh
    for czh, cen in get_cities(country_zh):
        if czh == city_zh:
            return cen
    return city_zh


# @cached_resource
@st.cache_resource
def get_finder(proxy=None):
    return ShopFinder(SearchEngine(proxy=proxy))


@st.cache_resource
def get_stats(proxy=None):
    return SalesStats(SearchEngine(proxy=proxy))


class SearchStopped(Exception):
    """用户点击停止按钮中断搜索"""
    pass


def make_whatsapp_link(shop):
    if not shop.phone:
        return None
    digits = "".join(c for c in shop.phone if c.isdigit())
    if not digits.startswith("+") and not digits.startswith("00"):
        code = get_country_code(shop.country)
        if code:
            digits = code.lstrip("+") + digits.lstrip("0")
    return f"https://wa.me/{digits}"


def make_telegram_link(shop):
    if shop.website:
        return shop.website
    return None


def make_telegram_deep_link(shop):
    """优先唤起本机 Telegram 客户端；无用户名则退回网页"""
    # Shop 未提供 telegram 用户名，退回官网；若官网缺失返回 None
    return shop.website or None


def make_email_link(shop):
    if shop.email:
        return f"mailto:{shop.email}"
    return None


def city_combobox(country_zh, key, label, placeholder):
    """城市选择：默认下拉选择常见城市，末尾「手动输入」可键入任意城市名，返回字符串（空=全部）"""
    cities = get_cities(country_zh)
    # 下拉框显示名按语言切换（英文显示英文名），但返回值仍用中文名（搜索/缓存依赖）
    city_names = [c[0] for c in cities]          # 内部值（中文）
    city_labels = [city_display(c) for c in cities]  # 显示名（按语言）
    manual_opt = T("manual_city_opt")
    all_opt = T("city_all_opt")
    all_label = all_opt
    options = [all_label] + city_names + [manual_opt]
    labels_map = dict(zip(city_names, city_labels))
    city_key = f"{key}_{country_zh}"
    sel_state_key = f"{city_key}_sel"
    if sel_state_key in st.session_state and st.session_state[sel_state_key] not in options:
        del st.session_state[sel_state_key]
    def _city_fmt(val):
        if val == all_label:
            return all_opt
        return labels_map.get(val, val)

    sel = st.selectbox(label, options=options, key=f"{city_key}_sel", index=0,
                       format_func=_city_fmt)
    if sel == all_opt:
        return ""
    if sel == manual_opt:
        value = st.text_input(T("manual_city_label"),
                              placeholder=placeholder,
                              key=f"{city_key}_manual", help=T("city_help"))
        return (value or "").strip()
    return (sel or "").strip()


# ===== 侧边栏 =====
with st.sidebar:
    st.markdown(f"**{T('sidebar_title')}**")
    st.divider()

    if st.button(T("menu_market"), use_container_width=True):
        st.session_state.page = "market"
    if st.button(T("menu_results"), use_container_width=True):
        st.session_state.page = "results"
    if st.button(T("menu_competitor"), use_container_width=True):
        st.session_state.page = "competitor"
    if st.button(T("menu_growth"), use_container_width=True):
        st.session_state.page = "growth"
    if st.button(T("menu_ads"), use_container_width=True):
        st.session_state.page = "ads"

    with st.expander(T("menu_tips"), expanded=False):
        st.markdown(T("tip1"))
        st.markdown(T("tip2"))
        st.markdown(T("tip3"))
        st.markdown(T("tip4"))

    with st.expander(T("menu_settings"), expanded=False):
        st.subheader(T("lang_switch"))
        c1, c2 = st.columns(2)
        with c1:
            if st.button(T("lang_zh"), use_container_width=True,
                         type="primary" if LANG == "zh" else "secondary"):
                st.session_state.lang = "zh"
                st.rerun()
        with c2:
            if st.button(T("lang_en"), use_container_width=True,
                         type="primary" if LANG == "en" else "secondary"):
                st.session_state.lang = "en"
                st.rerun()
        st.divider()
        st.subheader(T("setting_proxy"))
        # 云环境（HF Spaces/Docker）默认关闭代理，本地保持开启
        import os as _os
        _is_cloud = bool(_os.environ.get("SPACE_ID") or _os.environ.get("CLOUD_DEPLOYMENT"))
        proxy_enabled = st.checkbox(
            T("setting_proxy_hint"),
            value=st.session_state.get("proxy_enabled", not _is_cloud),
            key="proxy_check",
        )
        st.session_state.proxy_enabled = proxy_enabled
        if proxy_enabled:
            st.caption(T("setting_proxy_on"))
        else:
            st.caption(T("setting_proxy_off"))


# ===== paid-ads 广告投放 内容定义 =====
# 每个 entry: ("section标题", [正文行...], ("表格标题",[表头],[行]) 或 None)
PAID_ADS_ZH = {
    "meta": [
        ("搭建清单", [
            "- 商务资产组合已验证，信息与网站和付款方式一致",
            "- 域名已验证；像素 + 转化 API，事件已去重",
            "- 网站具备隐私政策、退款政策、配送政策、联系页和关于我们",
            "- 付款方式稳定；新账户先保守消耗",
        ], None),
        ("账户结构（越简单越好）", [
            "- 测试系列：找赢家素材，宽泛定向，固定日预算",
            "- 放量系列：放已验证的赢家，用进阶赋能型销售系列或 CBO",
            "- 再营销（可选，有足够流量后再做），注意避免预算重叠",
            "- 默认宽泛定向 + 强素材，在 Meta 上素材本身就在做定向",
        ], None),
        ("测试设置", [
            "- 素材测试用 ABO，放量用 CBO 或进阶赋能型系列",
            "- 一个概念一个广告组，每组 3–5 条（同概念不同钩子）",
            "- 每个测试广告组日预算约 1 倍目标 CPA，2–3 天能出结论",
            "- 至少跑 3 天再按 CPA 判断，不要第一天就下结论",
            "- 广告组每周约需 50 次优化事件才能退出学习期",
        ], None),
        ("新素材关停 / 保留规则", [], (
            "达到对应消耗后",
            ["情况", "决定"],
            [
                ["约 1 倍 CPA，链接 CTR 明显低于账户平均且无加购", "关停"],
                ["约 1.5–2 倍 CPA，无购买", "关停"],
                ["约 2 倍 CPA，有购买但 CPA 高于目标 20–50%，钩子/CTR 强", "迭代：换钩子换落地页再跑"],
                ["连续 3 天以上 CPA 达标且多笔购买", "赢家，移入放量"],
            ],
        )),
        ("放量规则", [
            "- 垂直放量：CPA 在目标内时每 48–72 小时提预算约 20%，CPA 突增当天不加",
            "- 水平放量：加预算开始推高 CPA 时停止，改为复制赢家到新广告组",
            "- 一次加幅超 50% 或仍在学习期时，优先复制而不是猛加预算",
        ], None),
        ("排查：CPA 上涨", [], (
            "常见原因与对策",
            ["变化的指标", "可能原因", "怎么做"],
            [
                ["CPM 上涨", "季节性 / 人群饱和 / 素材质量低", "上新素材、放宽人群"],
                ["CTR 下降、频次上升", "素材疲劳", "赢家概念换新钩子或上新概念"],
                ["CTR 正常、转化率下降", "落地页 / 报价 / 结账故障", "检查网站和报价"],
                ["数据正常但转化骤降", "追踪坏了", "检查事件管理工具"],
                ["投放停止", "政策标记 / 付款失败", "按合规流程处理"],
            ],
        )),
        ("中国卖家常见误区", [
            "- 一堆小预算广告组，永远出不了学习期",
            "- 弱素材叠加窄兴趣定向",
            "- 投一天花几美金就下结论",
            "- 新账户一夜之间把预算拉满",
            "- 一条素材跑几个月，疲劳了怪算法",
        ], None),
    ],
    "google": [
        ("选择广告系列类型", [], (
            "按情况先做",
            ["情况", "先做"],
            [
                ["电商且有商品数据", "购物广告或 PMax（商品数据要优化好）"],
                ["用户在搜问题或品类", "非品牌词搜索广告"],
                ["品牌已有搜索量", "品牌词搜索广告（防竞品截流）"],
                ["需要曝光或素材触达", "搜索跑通后再做 Demand Gen / YouTube"],
            ],
        )),
        ("搜索广告要点", [
            "- 按意图做关键词：购买意图、问题意图、对比意图",
            "- 按主题细分广告组，让广告和落地页匹配搜索词",
            "- 广泛匹配只配合智能出价和充足否定词；小预算用词组/完全匹配",
            "- 第一天就加否定词：free、jobs、DIY、used 等",
            "- 自适应搜索广告：最多 15 个标题、4 条描述",
            "- 补全附加链接、宣传信息、结构化摘要、图片",
        ], None),
        ("购物广告与 PMax", [
            "- 商品数据质量决定效果：标题写清品牌+产品+属性+尺寸颜色",
            "- 有 GTIN 就填，图片清晰，价格库存准确",
            "- Merchant Center 要求清晰的配送退货政策，新店铺常因虚假陈述被封",
            "- PMax 按品类或利润档分资产组，并加品牌排除",
        ], None),
        ("出价与每周优化", [
            "- 先用尽可能提高转化积累数据",
            "- 30 天内约 30 个以上转化后再切目标 CPA 或 ROAS",
            "- 每次调整 10–20%，两次调整间隔一周",
            "- 看搜索词报告加否定词，表现好的词单独拿出来",
            "- 消耗超 2 倍目标 CPA 仍无转化的词和商品暂停",
        ], None),
        ("中国卖家常见误区", [
            "- 广泛匹配 + 无否定词 + 手动出价",
            "- 所有流量都导到首页",
            "- 不重视 Merchant Center 政策，直到被封",
            "- 让 PMax 吃品牌词流量，误以为是新增长",
        ], None),
    ],
    "tiktok": [
        ("核心原则", [
            "- 素材就是策略：竖屏 9:16、真人、真实场景、字幕、有声",
            "- 前 2–3 秒决定一切：开头就上钩子，不要先放 logo",
            "- 数量胜过精致：每周多条新素材，TikTok 素材疲劳比 Meta 快",
        ], None),
        ("投放搭建", [
            "- 从宽泛定向开始，让算法根据素材信号找买家",
            "- 简单结构：一个测试系列 + 一个放量系列",
            "- 预算不足出不了学习期，先确认最低预算",
            "- Spark Ads：用自然帖投广告保留互动，更原生",
            "- 做 TikTok Shop 先把商品页、价格、评论做好",
        ], None),
        ("有效素材形式", [
            "- 真人讲述：问题 → 解决方案",
            "- 开箱与第一印象",
            "- 我换用 XX 的三个理由",
            "- 绿幕回应评论或差评",
            "- 使用过程演示（避免敏感的前后对比）",
        ], None),
        ("看哪些指标", [
            "- 钩子：2 秒和 6 秒播放率",
            "- 留存：平均观看时长、完播率",
            "- 点击：CTR",
            "- 转化：CVR、CPA、ROAS",
            "- 钩子率高但 CTR 低=中段/行动号召弱；钩子率低=换开头",
        ], None),
        ("中国卖家常见误区", [
            "- 把电视广告风格或 Meta 图片素材直接搬上 TikTok",
            "- 钩子太慢或以品牌开头",
            "- 使用未获商用授权的热门音乐",
            "- 文案翻译腔重，应找能自然对美国观众说话的达人",
        ], None),
    ],
    "tracking": [
        ("追踪方案", [], (
            "各平台追踪",
            ["平台", "浏览器端", "服务器端", "重点检查"],
            [
                ["Meta", "像素", "转化 API", "用同一 event_id 去重，事件匹配质量好"],
                ["Google", "Google 代码", "增强型转化 / GA4 导入", "传金额币种，每目标一个主要转化"],
                ["TikTok", "TikTok 像素", "Events API", "event_id 去重，传金额币种"],
                ["分析", "GA4", "—", "定义关键事件，关联广告平台"],
            ],
        )),
        ("标准电商事件", [
            "- 浏览页面 → 查看商品 → 加购 → 发起结账 → 添加支付信息 → 购买（带金额、币种、商品 ID）",
            "- 线索类：浏览 → 提交线索/注册 → 回传合格线索",
        ], None),
        ("UTM 规范", [
            "- utm_source：平台（facebook / google / tiktok / newsletter）",
            "- utm_medium：paid_social / cpc / email / influencer",
            "- utm_campaign：广告系列名",
            "- utm_content：广告或素材 ID",
            "- 全部小写、用下划线",
        ], None),
        ("校验步骤", [
            "- 下一笔真实测试订单（之后退款）或测试线索",
            "- 用官方测试工具检查（Meta 事件管理/Google Tag Assistant/TikTok 像素助手）",
            "- 确认金额币种正确、事件只触发一次",
            "- 对比同一周平台报告购买数与实际订单数；平台多报属正常归因重叠",
        ], None),
    ],
    "compliance": [
        ("上线前检查：主体与账户", [
            "- 广告账户、付款方式、网站上的公司信息一致",
            "- 能做企业验证的都做，所有管理员开启双重验证",
            "- 付款方式稳定，新账户逐步提高消耗",
        ], None),
        ("上线前检查：网站", [
            "- 产品信息清楚、价格真实、配送时间准确",
            "- 具备隐私政策、条款、退款退货政策、配送政策、真实邮箱联系页",
            "- 落地页与广告宣称和报价一致",
            "- 无遮挡内容的弹窗，结账流程正常",
        ], None),
        ("上线前检查：广告内容", [
            "- 不做无法证实的宣称（治愈/保证效果/无依据的第一）",
            "- 不用个人特征语句（你超重吗？），讲产品不讲用户特征",
            "- 健康、减肥、美容类避免前后对比图",
            "- 不用假按钮、假通知、误导性紧迫感",
            "- 不擅用商标、名人、版权音乐画面",
        ], None),
        ("高风险品类", [
            "- 保健品、减肥、医疗宣称化妆品、CBD、酒类、金融、交友、博彩、成人用品、武器相关",
            "- 这些有额外规则、资质要求甚至禁止，投放前查最新政策",
        ], None),
        ("被标记后怎么办", [
            "- 看清具体原因和对应政策",
            "- 确实违规就修改广告或落地页，不要原样重提",
            "- 误判就通过官方渠道申诉，简短陈述事实",
            "- 账户级限制先完成验证并等待审核，不要另找捷径",
            "- 记录每次拒审原因和修改，避免重犯",
        ], None),
        ("本模块红线", [
            "- 本模块帮助合规，不帮助规避审核",
            "- 伪装页面、买号养号、冒用身份、开新户绕过封禁均违反平台条款，会导致永久封禁",
        ], None),
    ],
}

PAID_ADS_EN = {
    "meta": [
        ("Setup Checklist", [
            "- Business asset group verified; info matches website and payment method",
            "- Domain verified; Pixel + Conversions API with deduplicated events",
            "- Website has privacy, refund, shipping policies, contact and about pages",
            "- Stable payment method; new accounts start with conservative spend",
        ], None),
        ("Account Structure (keep it simple)", [
            "- Testing campaign: find winning creatives, broad targeting, fixed daily budget",
            "- Scaling campaign: proven winners in Advantage+ Sales or CBO",
            "- Retargeting (optional, once you have enough traffic), avoid budget overlap",
            "- Default to broad targeting + strong creative; on Meta creative does the targeting",
        ], None),
        ("Testing Setup", [
            "- Use ABO for creative testing; CBO or Advantage+ for scaling",
            "- One concept per ad set, 3–5 ads each (different hooks of same concept)",
            "- Test ad set daily budget ≈ 1x target CPA, conclusions in 2–3 days",
            "- Run at least 3 days before judging on CPA, not day one",
            "- Ad set needs ~50 optimization events per week to exit learning phase",
        ], None),
        ("New Creative Kill / Keep Rules", [], (
            "After reaching the stated spend",
            ["Situation", "Decision"],
            [
                ["~1x CPA, link CTR well below account avg, no add-to-cart", "Kill"],
                ["~1.5–2x CPA, no purchase", "Kill"],
                ["~2x CPA, has purchase, CPA 20–50% above target, strong hook/CTR", "Iterate: new hook/landing page"],
                ["3+ consecutive days CPA on target with multiple purchases", "Winner, move to scaling"],
            ],
        )),
        ("Scaling Rules", [
            "- Vertical: raise budget ~20% every 48–72h while CPA is on target; not on a CPA spike day",
            "- Horizontal: when raising budget pushes CPA up, stop and duplicate winners into new ad sets",
            "- For increases over ~50% or ad sets still in learning, duplicate instead of big budget jumps",
        ], None),
        ("Diagnosing Rising CPA", [], (
            "Causes and fixes",
            ["Changing Metric", "Likely Cause", "Action"],
            [
                ["CPM up", "Seasonality / audience fatigue / weak creative", "New creative, broaden audience"],
                ["CTR down, frequency up", "Creative fatigue", "New hook on winner, or new concept"],
                ["CTR normal, CVR down", "Landing page / offer / checkout issue", "Check website and offer"],
                ["Data normal but conversions drop", "Tracking broken", "Check Events Manager"],
                ["Delivery stops", "Policy flag / payment failure", "Follow compliance flow"],
            ],
        )),
        ("Common China-Seller Mistakes", [
            "- Many tiny-budget ad sets that never exit learning phase",
            "- Weak creative stacked with narrow interest targeting",
            "- Judging after one day and a few dollars",
            "- Maxing a new account's budget overnight",
            "- Running one creative for months, then blaming the algorithm",
        ], None),
    ],
    "google": [
        ("Choosing Campaign Type", [], (
            "Start here based on your situation",
            ["Situation", "Start With"],
            [
                ["Ecommerce with product feed", "Shopping or PMax (feed must be optimized)"],
                ["Users searching problems/categories", "Non-brand search ads"],
                ["Brand already has search volume", "Brand search ads (blocks competitors)"],
                ["Need awareness/reach", "Demand Gen or YouTube after search works"],
            ],
        )),
        ("Search Ads Essentials", [
            "- Build keywords by intent: purchase, question, comparison (X vs Y)",
            "- Split ad groups by theme so ads and landing pages match search terms",
            "- Broad match only with smart bidding and plenty of negatives; small budgets use phrase/exact",
            "- Add negatives day one: free, jobs, DIY, used, etc.",
            "- RSA: up to 15 headlines, 4 descriptions",
            "- Complete sitelinks, promotions, structured snippets, images",
        ], None),
        ("Shopping & PMax", [
            "- Feed quality drives results: title = brand + product + key attributes + size/color",
            "- Fill GTIN when available; clear images; accurate price and stock",
            "- Merchant Center needs clear shipping/return policies; new stores often banned for misrepresentation",
            "- Split PMax asset groups by category or margin tier; add brand exclusions",
        ], None),
        ("Bidding & Weekly Optimization", [
            "- Start with Maximize Conversions to accumulate data",
            "- Switch to target CPA/ROAS after ~30+ conversions within 30 days",
            "- Adjust 10–20% at a time, a week apart",
            "- Review search terms report: add negatives, isolate winners",
            "- Pause words/products over 2x target CPA with no conversions",
        ], None),
        ("Common China-Seller Mistakes", [
            "- Broad match + no negatives + manual bidding",
            "- Sending all traffic to the homepage",
            "- Ignoring Merchant Center policy until banned",
            "- Letting PMax cannibalize brand terms and calling it growth",
        ], None),
    ],
    "tiktok": [
        ("Core Principles", [
            "- Creative IS the strategy: 9:16 vertical, real people, real scenes, captions, sound",
            "- First 2–3 seconds decide everything: hook immediately, no logo first",
            "- Volume beats polish: multiple new creatives weekly; TikTok fatigue is faster than Meta",
        ], None),
        ("Campaign Setup", [
            "- Start with broad targeting; let the algorithm find buyers via creative signals",
            "- Simple structure: one testing + one scaling campaign",
            "- Confirm minimum ad set budget; under-funded ad sets never exit learning",
            "- Spark Ads: boost organic posts (keep likes/comments) for a native feel",
            "- For TikTok Shop, perfect product page, price and reviews first",
        ], None),
        ("Effective Creative Formats", [
            "- Talking head: problem → solution",
            "- Unboxing and first impressions",
            "- Three reasons I switched to X",
            "- Green-screen responding to comments or bad reviews",
            "- Process demos (avoid policy-sensitive before/after)",
        ], None),
        ("Metrics to Watch", [
            "- Hook: 2s and 6s view rates",
            "- Retention: average watch time, completion rate",
            "- Click: CTR",
            "- Conversion: CVR, CPA, ROAS",
            "- High hook + low CTR = weak middle/CTA; low hook = change the opening",
        ], None),
        ("Common China-Seller Mistakes", [
            "- Reusing TV-style or Meta image ads on TikTok",
            "- Slow hooks or brand-first openings",
            "- Using popular music without commercial license",
            "- Heavy translation tone; use creators who speak naturally to US viewers",
        ], None),
    ],
    "tracking": [
        ("Tracking Stack", [], (
            "Per-platform tracking",
            ["Platform", "Browser", "Server", "Key Check"],
            [
                ["Meta", "Pixel", "Conversions API", "Dedup via same event_id; good match quality"],
                ["Google", "Google tag", "Enhanced conversions / GA4 import", "Pass amount & currency; one primary conversion per goal"],
                ["TikTok", "TikTok Pixel", "Events API", "event_id dedup; pass amount & currency"],
                ["Analytics", "GA4", "—", "Define key events, link ad platforms"],
            ],
        )),
        ("Standard Ecommerce Events", [
            "- Page view → View content → Add to cart → Begin checkout → Add payment → Purchase (with value, currency, item ID)",
            "- Lead: page view → submit lead/signup → (if possible) qualified lead back",
        ], None),
        ("UTM Convention", [
            "- utm_source: platform (facebook / google / tiktok / newsletter)",
            "- utm_medium: paid_social / cpc / email / influencer",
            "- utm_campaign: campaign name",
            "- utm_content: ad or creative ID",
            "- All lowercase, underscores",
        ], None),
        ("Validation Steps", [
            "- Place a real test order (refund after) or a test lead",
            "- Verify with official tools (Meta Events Manager / Google Tag Assistant / TikTok Pixel helper)",
            "- Confirm amount and currency are correct and the event fires once",
            "- Compare platform purchases vs actual orders weekly; platforms over-reporting is normal attribution overlap",
        ], None),
    ],
    "compliance": [
        ("Pre-Launch Check: Entity & Account", [
            "- Ad account, payment method, and website company info all match",
            "- Do business verification wherever possible; enable 2FA for all admins",
            "- Stable payment; ramp spend gradually on new accounts",
        ], None),
        ("Pre-Launch Check: Website", [
            "- Clear product info, honest prices, accurate shipping times",
            "- Have privacy, terms, refund/return, shipping policies, and a real contact email",
            "- Landing page matches ad claims and offer",
            "- No pop-ups blocking content; checkout works",
        ], None),
        ("Pre-Launch Check: Ad Content", [
            "- No unverifiable claims (cure / guaranteed results / unsupported 'first')",
            "- No personal-attribute callouts (are you overweight?); talk about the product, not the user",
            "- Health/weight-loss/beauty: avoid before-after images",
            "- No fake buttons, fake notifications, or misleading urgency",
            "- No unauthorized trademarks, celebrities, or copyrighted music/footage",
        ], None),
        ("High-Risk Categories", [
            "- Supplements, weight loss, medical-claim cosmetics, CBD, alcohol, finance, dating, gambling, adult, weapons",
            "- These carry extra rules, requirements, or full bans; check the latest policy before running",
        ], None),
        ("If Flagged", [
            "- Read the specific reason and the policy it cites",
            "- If actually in violation, fix the ad or landing page; don't resubmit unchanged",
            "- If it's a mistake, appeal via official channels with a short factual statement",
            "- For account-level limits, complete required verification and wait; don't take shortcuts",
            "- Log every rejection and fix to avoid repeats",
        ], None),
        ("Hard Lines", [
            "- This module helps you comply, not evade review",
            "- Cloaking, buying/accounts farming, identity misuse, or new accounts to bypass bans violate platform terms and cause permanent bans",
        ], None),
    ],
}

# ===== 主内容区 =====
if "page" not in st.session_state:
    st.session_state.page = "market"

proxy = ProxyConfig.detect_working_proxy() if st.session_state.get("proxy_enabled") else None

if st.session_state.page == "market":
    st.header(T("menu_market"))
    tab1, tab2 = st.tabs([T("tab_shop"), T("tab_stats")])

    # ===== Tab 1: 店铺查找 =====
    with tab1:
        col1, col2, col3 = st.columns([1, 1, 1.5])
        with col1:
            country = st.selectbox(T("country"), get_country_list(),
                                   key="shop_country", format_func=country_display)
        with col2:
            # 城市选择：单框 input+datalist（可自由键入，也可点开下拉选预设城市）
            city_zh = city_combobox(
                country, key=f"shop_city_combo",
                label=T("city"), placeholder=T("city_input_ph"),
            )
        
        with col3:
            product = st.text_input(T("product"), placeholder=T("product_ph"), key="shop_product")

        # 城市滑动条逻辑：滑动条在左（缩短），搜索按钮在右
        country_cities_count = len(get_cities(country)) if country else 0
        col_slider, col_btn1 = st.columns([3.5, 1])
        with col_slider:
            if city_zh:
                # 选了城市，锁死为1
                max_cities = st.select_slider(T("num_cities"), options=[1], value=1,
                                              key="shop_max_locked", disabled=True)
                cities_limit = 1
            else:
                # 只选国家，显示 1 到 ALL
                city_options = list(range(1, country_cities_count + 1)) + [T("all")]
                default_val = min(6, country_cities_count) if country_cities_count > 0 else 1
                max_cities = st.select_slider(T("num_cities"), options=city_options,
                                              value=default_val, key="shop_max")
                cities_limit = 999 if max_cities == T("all") else max_cities
        with col_btn1:
            _s1, _s2 = st.columns([1, 1])
            with _s1:
                search_btn = st.button(T("search"), type="primary", use_container_width=True)
            with _s2:
                stop_btn = st.button(T("stop"), use_container_width=True, key="shop_stop_btn")
            if stop_btn:
                st.session_state["shop_stop"] = True

        if search_btn and product:
            progress_bar = st.progress(0)
            status_text = st.empty()

            st.session_state["shop_stop"] = False

            def update_progress(done, total, msg):
                if st.session_state.get("shop_stop"):
                    raise SearchStopped()
                pct = int(done / max(total, 1) * 100)
                progress_bar.progress(pct)
                status_text.info(msg)

            shops = []
            try:
                with st.spinner(T("searching")):
                    finder = get_finder(proxy)
                    shops = finder.find_shops(country, product, city_zh=city_zh,
                                              max_cities=cities_limit,
                                              max_results_per_city=10,
                                              fetch_details=True,
                                              progress_callback=update_progress)
            except SearchStopped:
                progress_bar.empty()
                status_text.warning(T("stopped"))
                st.stop()
            progress_bar.empty()
            status_text.empty()
            st.session_state.shops = shops
            st.session_state.shop_query = {
                "country": country,
                "product": product,
                "city": city_zh or T("all"),
            }
            st.session_state.contact_filter = "全部"

        if "shops" in st.session_state and st.session_state.shops:
            shops = st.session_state.shops
            query = st.session_state.shop_query
            st.success(T("found") + f"**{len(shops)}**" + T("found_tail"))

            with_phone = sum(1 for s in shops if s.phone)
            with_email = sum(1 for s in shops if s.email)
            with_addr = sum(1 for s in shops if s.address)
            if "contact_filter" not in st.session_state:
                st.session_state.contact_filter = "全部"

            filter_cards = [
                ("全部", len(shops), "🏪", T("total")),
                ("有电话", with_phone, "📞", T("has_phone")),
                ("有邮箱", with_email, "📧", T("has_email")),
                ("有地址", with_addr, "🏠", T("has_addr")),
            ]
            cols = st.columns(4)
            for col, (value, count, icon, label) in zip(cols, filter_cards):
                with col:
                    selected = st.session_state.contact_filter == value
                    if st.button(f"{icon} {count} · {label}", key=f"filter_{value}",
                                 type="primary" if selected else "secondary",
                                 use_container_width=True):
                        st.session_state.contact_filter = value
                        st.rerun()

            active_filter = st.session_state.contact_filter
            st.caption(T("filter_hint"))

            def match_filter(shop):
                if active_filter == "有电话":
                    return bool(shop.phone)
                if active_filter == "有邮箱":
                    return bool(shop.email)
                if active_filter == "有地址":
                    return bool(shop.address)
                return True

            st.divider()

            col_list, col_map = st.columns([1, 1.2])
            with col_list:
                st.subheader(T("shop_list"))
                if "selected_shop" not in st.session_state:
                    st.session_state.selected_shop = 0

                shown = 0
                for idx, shop in enumerate(shops):
                    if not match_filter(shop):
                        continue
                    shown += 1
                    with st.container():
                        name_col, btn_col = st.columns([3, 1])
                        with name_col:
                            st.markdown(f"**{idx + 1}. {shop.name}**")
                            st.caption(f"📍 {shop.city}, {shop.country}")
                        with btn_col:
                            if st.button(T("map_btn"), key=f"map_btn_{idx}", type="secondary"):
                                st.session_state.selected_shop = idx

                        contact_lines = []
                        if shop.contact_person:
                            contact_lines.append(T("contact_person") + shop.contact_person)
                        if shop.phone:
                            p_disp = format_phone(shop.phone, shop.country)
                            p_dial = p_disp.replace(" ", "").replace("-", "")
                            contact_lines.append(
                                f'{T("phone")}<a href="tel:{p_dial}" '
                                f'style="color:var(--accent);font-weight:600;">{p_disp}</a>'
                            )
                        if shop.email:
                            contact_lines.append(
                                f'{T("email")}<a href="mailto:{shop.email}" '
                                f'style="color:var(--accent);font-weight:600;">{shop.email}</a>'
                            )
                        if shop.address:
                            contact_lines.append(T("address") + shop.address)
                        if contact_lines:
                            st.markdown('<div class="contact-info">' + "<br>".join(contact_lines) + "</div>",
                                        unsafe_allow_html=True)
                        else:
                            st.caption(T("no_contact"))

                        # 操作按钮：网站/详情/WhatsApp/Telegram/邮件
                        btn_cols = st.columns(5)
                        with btn_cols[0]:
                            if shop.website:
                                st.link_button(T("website"), shop.website, use_container_width=True)
                        with btn_cols[1]:
                            if shop.detail_url and shop.detail_url != shop.website:
                                st.link_button(T("detail"), shop.detail_url, use_container_width=True)
                        with btn_cols[2]:
                            wa = make_whatsapp_link(shop)
                            if wa:
                                st.link_button(T("contact_whatsapp"), wa, use_container_width=True)
                        with btn_cols[3]:
                            tg = make_telegram_link(shop)
                            if tg:
                                st.link_button(T("contact_telegram"), tg, use_container_width=True)
                        with btn_cols[4]:
                            em = make_email_link(shop)
                            if em:
                                st.link_button(T("contact_email"), em, use_container_width=True)

                        st.divider()

                if shown == 0:
                    st.warning(T("no_shops_filter"))

            with col_map:
                st.subheader(T("map_header"))
                geo_shops = [s for s in shops if s.lat and s.lon and match_filter(s)]
                if geo_shops:
                    center_lat = sum(s.lat for s in geo_shops) / len(geo_shops)
                    center_lon = sum(s.lon for s in geo_shops) / len(geo_shops)

                    features = []
                    for idx, shop in enumerate(geo_shops):
                        orig_idx = shops.index(shop)
                        is_selected = orig_idx == st.session_state.selected_shop
                        features.append({
                            "type": "Feature",
                            "geometry": {"type": "Point", "coordinates": [shop.lon, shop.lat]},
                            "properties": {
                                "name": f"{orig_idx + 1}. {shop.name}",
                                "selected": is_selected,
                            },
                        })
                    geojson_data = {"type": "FeatureCollection", "features": features}
                    map_zoom = 12 if query["city"] not in (T("all"), "全部") else 6
                    map_html = f"""
                    <!DOCTYPE html><html><head><meta charset="utf-8">
                    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                    <style>#map {{ height: 600px; width: 100%; border-radius: 12px; }}</style>
                    </head><body><div id="map"></div><script>
                    var map = L.map('map').setView([{center_lat}, {center_lon}], {map_zoom});
                    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                        attribution: '© OpenStreetMap contributors', maxZoom: 19 }}).addTo(map);
                    var shopsData = {json.dumps(geojson_data, ensure_ascii=False)};
                    var markers = [];
                    shopsData.features.forEach(function(feature) {{
                        var coords = feature.geometry.coordinates;
                        var props = feature.properties;
                        var iconColor = props.selected ? 'red' : 'blue';
                        var icon = L.icon({{
                            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-' + iconColor + '.png',
                            iconSize: props.selected ? [35, 51] : [25, 41],
                            iconAnchor: props.selected ? [17, 51] : [12, 41],
                            popupAnchor: [1, -34] }});
                        var marker = L.marker([coords[1], coords[0]], {{icon: icon}})
                            .addTo(map).bindPopup(props.name);
                        markers.push(marker);
                    }});
                    var selectedFeature = shopsData.features.find(f => f.properties.selected);
                    if (selectedFeature) {{
                        var c = selectedFeature.geometry.coordinates;
                        map.flyTo([c[1], c[0]], {map_zoom + 1}, {{duration: 1.5}});
                        setTimeout(function() {{
                            var idx = shopsData.features.indexOf(selectedFeature);
                            if (markers[idx]) markers[idx].openPopup();
                        }}, 1600);
                    }}
                    </script></body></html>
                    """
                    st.components.v1.html(map_html, height=620)
                    st.caption(T("map_hint"))
                else:
                    st.info(T("no_geo"))

            # 导出
            if shops:
                st.divider()
                st.subheader(T("export"))
                col_e1, col_e2 = st.columns([2, 1])
                with col_e1:
                    fmt = st.selectbox(T("export_format"),
                                       [T("excel_opt"), T("pdf_opt")], key="export_fmt")
                with col_e2:
                    if st.button("💾 " + T("exported"), use_container_width=True):
                        fmt_code = "excel" if "Excel" in fmt or "表格" in fmt else "pdf"
                        try:
                            path, data, fname = export_file(shops, query, active_filter, fmt_code, lang=LANG)
                            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" if fmt_code == "excel" else "application/pdf"
                            st.download_button(
                                label=f"⬇️ {fname}",
                                data=data,
                                file_name=fname,
                                mime=mime,
                                key="download_btn",
                            )
                            st.success(T("exported"))
                        except Exception as e:
                            st.error(f"❌ {e}")

        elif search_btn and not product:
            st.warning(T("input_product_warn"))

    # ===== Tab 2: 销售统计 =====
    with tab2:
        st.subheader(T("stats_header"))

        # 第一行：国家 / 城市 / 商品（与店铺查找一致）
        col1, col2, col3 = st.columns([1, 1, 1.5])
        with col1:
            stat_country = st.selectbox(T("country"), get_country_list(), key="stat_country",
                                        format_func=country_display)
        with col2:
            stat_city_input = city_combobox(stat_country, key="stat_city_combo",
                                            label=T("city"), placeholder=T("stats_city_ph"))
        with col3:
            stat_product = st.text_input(T("product"), placeholder=T("stats_product_ph"), key="stat_product")

        # 城市滑动条（左）+ 开始分析按钮（右）
        stat_country_cities_count = len(get_cities(stat_country)) if stat_country else 0
        col_slider, col_btn = st.columns([3.5, 1])
        with col_slider:
            if stat_city_input:
                stat_max_cities = st.select_slider(T("stats_cities"), options=[1], value=1,
                                                   key="stat_max_locked", disabled=True)
                stat_cities_limit = 1
                stat_city_override = stat_city_input
            else:
                stat_city_override = None
                stat_city_options = list(range(1, stat_country_cities_count + 1)) + [T("all")]
                stat_default = min(6, stat_country_cities_count) if stat_country_cities_count > 0 else 1
                stat_max_cities = st.select_slider(T("stats_cities"),
                                                   options=stat_city_options, value=stat_default, key="stat_max")
                stat_cities_limit = 999 if stat_max_cities == T("all") else stat_max_cities
        with col_btn:
            stat_btn = st.button(T("stats_btn"), type="primary", use_container_width=True)
        
        # 4个指标说明折叠面板
        with st.expander(T("metric_desc_title"), expanded=False):
            st.markdown(f"**{T('metric_result_count')}**")
            st.caption(T("metric_result_count_desc"))
            st.divider()
            st.markdown(f"**{T('metric_shop_count')}**")
            st.caption(T("metric_shop_count_desc"))
            st.divider()
            st.markdown(f"**{T('metric_platform_count')}**")
            st.caption(T("metric_platform_count_desc"))
            st.divider()
            st.markdown(f"**{T('metric_price_mentions')}**")
            st.caption(T("metric_price_mentions_desc"))
        
        if stat_btn and stat_product:
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(done, total, msg):
                pct = int(done / max(total, 1) * 100)
                progress_bar.progress(pct)
                status_text.info(msg)

            with st.spinner(T("analyzing")):
                stats_engine = get_stats(proxy)
                report = stats_engine.generate_report(stat_product, stat_country,
                                                      max_cities=stat_cities_limit,
                                                      max_results_per_city=20,
                                                      progress_callback=update_progress,
                                                      city_override=stat_city_override if stat_city_override else None)
            progress_bar.empty()
            status_text.empty()
            st.session_state.sales_report = report

        if "sales_report" in st.session_state:
            report = st.session_state.sales_report
            st.success(T("stats_done") + f"{report.product} · {report.country_zh} · "
                       f"{T('stats_total')}{report.total_results}{T('stats_total_tail')}")
            sorted_cities = report.sorted_cities()
            st.subheader(T("heat_header"))
            chart_data = pd.DataFrame({
                T("heat_score"): [c.heat_score for c in sorted_cities],
            }, index=[c.city_zh for c in sorted_cities])
            st.bar_chart(chart_data, use_container_width=True, height=300)

            st.subheader(T("detail_data"))
            for city_stat in sorted_cities:
                with st.expander(f"🏙️ {city_stat.city_zh} ({city_stat.city_en}) · "
                                 f"{T('heat')} {city_stat.heat_score}", expanded=False):
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.metric(T("search_results"), city_stat.result_count)
                    with c2:
                        st.metric(T("shops"), city_stat.shop_count)
                    with c3:
                        st.metric(T("platforms"), city_stat.platform_count)
                    with c4:
                        st.metric(T("prices"), city_stat.price_mentions)
                    if city_stat.sample_prices:
                        st.write(" | ".join(city_stat.sample_prices))

        elif stat_btn and not stat_product:
            st.warning(T("input_product_warn"))

elif st.session_state.page == "results":
    st.header(T("menu_results"))
    if "shops" not in st.session_state or not st.session_state.shops:
        st.info(T("no_results"))
    else:
        shops = st.session_state.shops
        query = st.session_state.shop_query
        st.caption(f"{query.get('country','')} · {query.get('product','')}")
        
        # 导出按钮（放在标题旁边的小按钮 + 下拉）
        _hdr_col, _btn_col = st.columns([4, 1])
        with _btn_col:
            if st.button(T("export"), key="results_export_icon", use_container_width=True):
                st.session_state.show_export_menu = not st.session_state.get("show_export_menu", False)
        
        # 导出下拉菜单
        if st.session_state.get("show_export_menu", False):
            with st.expander(T("export"), expanded=True):
                res_fmt = st.selectbox(T("export_format"),
                                       [T("excel_opt"), T("pdf_opt")], key="results_export_fmt")
                if st.button("💾 " + T("export"), use_container_width=True, key="results_export_btn"):
                    res_fmt_code = "excel" if ("Excel" in res_fmt or "表格" in res_fmt) else "pdf"
                    try:
                        _path, res_data, res_fname = export_file(shops, query, "全部", res_fmt_code, lang=LANG)
                        res_mime = ("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    if res_fmt_code == "excel" else "application/pdf")
                        st.download_button(
                            label=f"⬇️ {res_fname}",
                            data=res_data,
                            file_name=res_fname,
                            mime=res_mime,
                            key="results_download_btn",
                        )
                        st.session_state.show_export_menu = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")
        
        # 按国家分组
        by_country = {}
        for shop in shops:
            by_country.setdefault(shop.country, []).append(shop)

        tab1, tab2 = st.tabs([T("tab_country"), T("tab_city")])

        def build_shop_table(shops_list):
            """构建紧凑表格：商家/城市/电话/地址/邮箱/WhatsApp/Telegram，缺项留空"""
            rows = []
            for shop in shops_list:
                rows.append({
                    T("col_name"): shop.name or "",
                    T("col_city"): shop_city_display(shop.city, shop.country) if shop.city else "",
                    T("col_phone"): format_phone(shop.phone, shop.country) if shop.phone else "",
                    T("col_address"): shop.address or "",
                    T("col_email_hdr"): shop.email or "",
                    "_wa": make_whatsapp_link(shop) or "",
                    "_tg": make_telegram_deep_link(shop) or "",
                })
            return pd.DataFrame(rows)

        _col_cfg = {
            T("col_name"): st.column_config.TextColumn(T("col_name"), width="medium"),
            T("col_city"): st.column_config.TextColumn(T("col_city"), width="small"),
            T("col_phone"): st.column_config.TextColumn(T("col_phone"), width="small"),
            T("col_address"): st.column_config.TextColumn(T("col_address"), width="medium"),
            T("col_email_hdr"): st.column_config.TextColumn(T("col_email_hdr"), width="medium"),
            "_wa": st.column_config.LinkColumn(T("col_wa"), display_text="💬 WhatsApp"),
            "_tg": st.column_config.LinkColumn(T("col_tg"), display_text="📨 Telegram"),
        }

        with tab1:
            for country_name, cshops in by_country.items():
                country_disp = COUNTRIES.get(country_name, {}).get("en", country_name) if LANG == "en" else country_name
                with st.expander(f"🌍 {country_disp} ({len(cshops)}{T('shop_count_unit')})", expanded=True):
                    df = build_shop_table(cshops)
                    st.dataframe(df, use_container_width=True, hide_index=True,
                                 column_config=_col_cfg)
        with tab2:
            by_city = {}
            for shop in shops:
                by_city.setdefault(shop.city, []).append(shop)
            for city_name, cshops in by_city.items():
                city_disp = shop_city_display(city_name, cshops[0].country) if cshops else city_name
                with st.expander(f"🏙️ {city_disp} ({len(cshops)}{T('shop_count_unit')})", expanded=False):
                    df = build_shop_table(cshops)
                    st.dataframe(df, use_container_width=True, hide_index=True,
                                 column_config=_col_cfg)


elif st.session_state.page == "competitor":
    st.header(T("comp_header"))
    st.caption(T("comp_note"))

    import datetime as _dt
    _this_year = _dt.date.today().year

    # ========== 市场竞品分析 ==========
    col1, col2, col3 = st.columns([1, 1, 1.5])
    with col1:
        comp_country = st.selectbox(T("country"), get_country_list(), key="comp_country",
                                    format_func=country_display)
    with col2:
        comp_city = city_combobox(comp_country, key="comp_city_combo",
                                  label=T("city"), placeholder=T("comp_city_ph"))
    with col3:
        comp_product = st.text_input(T("product"), placeholder=T("comp_product_ph"), key="comp_product")

    _col_period, col_btn = st.columns([3, 1])
    with _col_period:
        _pc1, _pc2, _spacer = st.columns([1, 1, 2])
        with _pc1:
            comp_start_date = st.date_input(
                f"{T('comp_period')} · {T('comp_start')}",
                value=_dt.date(_this_year - 4, 1, 1),
                key="comp_start_date",
            )
        with _pc2:
            comp_end_date = st.date_input(
                f"{T('comp_period')} · {T('comp_end')}",
                value=_dt.date(_this_year, 12, 31),
                key="comp_end_date",
            )
        if isinstance(comp_start_date, _dt.date) and isinstance(comp_end_date, _dt.date):
            if comp_end_date < comp_start_date:
                st.error(T("comp_date_err"))
    with col_btn:
        _c1, _c2 = st.columns([1, 1])
        with _c1:
            comp_btn = st.button(T("comp_btn"), type="primary", use_container_width=True)
        with _c2:
            comp_stop = st.button(T("stop"), use_container_width=True, key="comp_stop_btn")
        if comp_stop:
            st.session_state["comp_stop"] = True

    if comp_btn and comp_product and isinstance(comp_start_date, _dt.date) and isinstance(comp_end_date, _dt.date) and comp_end_date >= comp_start_date:
        comp_country_code = get_country_code(comp_country) if comp_country else "US"
        comp_start_year = comp_start_date.year
        comp_end_year = comp_end_date.year
        progress_bar = st.progress(0)
        status_text = st.empty()

        st.session_state["comp_stop"] = False

        def update_progress(done, total, msg):
            if st.session_state.get("comp_stop"):
                raise SearchStopped()
            pct = int(done / max(total, 1) * 100)
            progress_bar.progress(min(pct, 100))
            status_text.info(msg)

        report = None
        try:
            with st.spinner(T("analyzing")):
                comp_engine = SearchEngine(proxy)
                report = analyze_competitors(
                    comp_engine, comp_product, comp_country, comp_country_code,
                    city=comp_city,
                    start_year=comp_start_year,
                    end_year=comp_end_year,
                    progress_callback=update_progress,
                )
        except SearchStopped:
            progress_bar.empty()
            status_text.warning(T("stopped"))
            st.stop()
        progress_bar.empty()
        status_text.empty()
        st.session_state.comp_report = report

    if "comp_report" in st.session_state:
        report = st.session_state.comp_report
        if report.total_search_results == 0 and report.total_products == 0:
            st.warning(T("comp_none"))
        else:
            st.success(T("comp_done") + f"**{report.total_search_results + report.total_products}**" + T("comp_total_tail"))
            st.caption(f"{report.country_zh} · {report.city or T('all')} · {report.product} · {report.year_range}")
            st.info("📊 " + T("comp_sources") + "：" + " / ".join(report.sources))

            st.subheader(T("comp_yearly"))
            yr = report.yearly_mentions
            year_df = pd.DataFrame({T("comp_mentions"): [yr.get(y, 0) for y in sorted(yr.keys())]},
                                   index=sorted(yr.keys()))
            st.bar_chart(year_df, use_container_width=True, height=280)
            st.caption(" | ".join(f"{y}: {yr.get(y, 0)}" for y in sorted(yr.keys())))

            st.subheader(T("comp_monthly"))
            mm = report.monthly_mentions
            month_labels = [_month_disp(k) for k in mm.keys()]
            month_vals = [mm[k] for k in mm.keys()]
            month_df = pd.DataFrame({T("comp_mentions"): month_vals}, index=month_labels)
            st.bar_chart(month_df, use_container_width=True, height=300)
            if report.peak_months:
                st.success(f"🔥 **{T('comp_peak')}**：" + "、".join(_month_disp(m) for m in report.peak_months))
            if report.off_months:
                st.info(f"❄️ **{T('comp_off')}**：" + "、".join(_month_disp(m) for m in report.off_months))

            if report.season_reasons:
                with st.expander(T("comp_reasons"), expanded=True):
                    reason_df = pd.DataFrame(
                        [{T("comp_reason"): _season_disp(r["reason"]), T("comp_reason_count"): r["count"]}
                         for r in report.season_reasons]
                    )
                    st.table(reason_df)

            st.subheader(T("comp_competitors"))
            if report.competitors:
                comp_df = pd.DataFrame(
                    [{T("comp_comp_name"): c["name"], T("comp_comp_type"): _comp_type_disp(c["type"]),
                      T("comp_comp_count"): c["count"]} for c in report.competitors]
                )
                st.dataframe(comp_df, use_container_width=True, hide_index=True)
            else:
                st.info(T("comp_none"))

            st.subheader(T("comp_channels"))
            if report.channels:
                ch_df = pd.DataFrame(
                    [{T("comp_channel_name"): c["name"], T("comp_channel_count"): c["count"],
                      T("comp_channel_pct"): c["pct"]} for c in report.channels]
                )
                st.dataframe(ch_df, use_container_width=True, hide_index=True)
            else:
                st.info(T("comp_none"))

            st.subheader(T("comp_models"))
            ps = report.price_stats
            if ps.get("count"):
                cur = ps.get("currency", "USD")
                st.markdown(
                    f"**{T('comp_price_stats')}**："
                    f"{T('comp_price_count')} {ps['count']} · "
                    f"{T('comp_price_min')} {ps['min']} {cur} · "
                    f"{T('comp_price_max')} {ps['max']} {cur} · "
                    f"{T('comp_price_avg')} {ps['avg']} {cur} · "
                    f"{T('comp_price_median')} {ps['median']} {cur}"
                )
            if report.top_models:
                model_df = pd.DataFrame(
                    [{T("comp_model"): m["model"], T("comp_model_count"): m["count"],
                      T("comp_avg_price"): (f"{m['avg_price']} {ps.get('currency', 'USD')}" if m["avg_price"] else "—")}
                     for m in report.top_models]
                )
                st.dataframe(model_df, use_container_width=True, hide_index=True)
            else:
                st.info(T("comp_none"))

            with st.expander(T("comp_queries_used"), expanded=False):
                for q in report.search_queries:
                    st.caption("• " + q)

elif st.session_state.page == "growth":
    st.header(T("gp_tab"))
    st.caption(T("gp_note"))

    gp_c1, gp_c2, gp_c3 = st.columns([1, 1, 1])
    with gp_c1:
        gp_product = st.text_input(T("product"), placeholder=T("comp_product_ph"), key="gp_product")
    with gp_c2:
        gp_price = st.number_input(T("gp_price"), min_value=0.0, value=19.9, step=0.1, key="gp_price")
    with gp_c3:
        gp_cost = st.number_input(T("gp_cost"), min_value=0.0, value=5.0, step=0.1, key="gp_cost")

    gp_c4, gp_c5, gp_c6 = st.columns([1, 1, 1])
    with gp_c4:
        gp_shipping = st.number_input(T("gp_shipping"), min_value=0.0, value=2.0, step=0.1, key="gp_shipping")
    with gp_c5:
        gp_tariff = st.number_input(T("gp_tariff"), min_value=0.0, value=0.0, step=0.1, key="gp_tariff")
    with gp_c6:
        gp_budget = st.number_input(T("gp_budget"), min_value=0.0, value=3000.0, step=100.0, key="gp_budget")

    gp_c7, gp_c8 = st.columns([1, 1])
    with gp_c7:
        gp_stage = st.selectbox(T("gp_stage"),
                                options=["idea", "early_sales", "scaling"],
                                format_func=lambda x: T("gp_stage_idea") if x == "idea" else (T("gp_stage_early") if x == "early_sales" else T("gp_stage_scaling")),
                                key="gp_stage")
    with gp_c8:
        gp_btype = st.selectbox(T("gp_btype"),
                                options=["impulse_b2c", "decision_b2c", "b2b", "tiktok_b2c"],
                                format_func=lambda x: T("gp_btype_impulse") if x == "impulse_b2c" else (T("gp_btype_decision") if x == "decision_b2c" else (T("gp_btype_b2b") if x == "b2b" else T("gp_btype_tiktok"))),
                                key="gp_btype")

    gp_btn = st.button(T("gp_btn"), type="primary", use_container_width=True)

    if gp_btn and gp_product and gp_price > 0:
        gp_params = GrowthPlanInput(
            product=gp_product,
            price=float(gp_price),
            cost=float(gp_cost),
            gross_margin=0.0,
            budget_monthly=float(gp_budget),
            stage=gp_stage,
            business_type=gp_btype,
            target_market="美国",
            shipping_cost=float(gp_shipping),
            tariff_cost=float(gp_tariff),
        )
        gp_result = generate_growth_plan(gp_params, lang=LANG)
        st.session_state.gp_result = gp_result

    if "gp_result" in st.session_state:
        gp = st.session_state.gp_result
        ue = gp.unit_economics

        st.subheader(T("gp_unit_econ"))
        ue1, ue2, ue3, ue4 = st.columns(4)
        with ue1:
            st.metric(T("gp_ue_price"), f"${ue.price:.2f}")
            st.metric(T("gp_ue_cost"), f"${ue.total_cost:.2f}")
        with ue2:
            st.metric(T("gp_ue_profit"), f"${ue.gross_profit:.2f}")
            st.metric(T("gp_ue_margin"), f"{ue.gross_margin * 100:.1f}%")
        with ue3:
            st.metric(T("gp_ue_broas"), f"{ue.breakeven_roas:.2f}")
            st.metric(T("gp_ue_troas"), f"{ue.target_roas:.2f}")
        with ue4:
            st.metric(T("gp_ue_tcpa"), f"${ue.target_cpa:.2f}")

        st.subheader(T("gp_channel"))
        ch = gp.channel_recommendation
        st.markdown(f"**{ch.channel}**")
        st.caption(f"💡 {ch.reason}")
        st.caption(f"🔧 {T('gp_channel_skill')}：`{ch.skill_ref}`")

        st.subheader(T("gp_budget_alloc"))
        alloc = gp.budget_allocation
        alloc_df = pd.DataFrame(
            [{T("gp_alloc_channel"): k, T("gp_alloc_pct"): f"{v * 100:.0f}%", T("gp_alloc_monthly"): f"${gp.input_params.budget_monthly * v:.0f}"}
             for k, v in alloc.items()]
        )
        st.dataframe(alloc_df, use_container_width=True, hide_index=True)

        st.subheader(T("gp_phases"))
        for phase in gp.phases:
            with st.expander(f"**{phase.phase}** · {phase.days} · {phase.goal}", expanded=False):
                st.markdown(f"**{T('gp_kpi')}**：{phase.kpi}")
                st.markdown(f"**{T('gp_budget_pct')}**：{phase.budget_pct * 100:.0f}%")
                st.markdown(f"**{T('gp_actions')}**：")
                for act in phase.actions:
                    st.markdown(act)

        st.subheader(T("gp_top3"))
        for act in gp.top_3_actions:
            st.markdown(act)

        with st.expander(T("gp_research"), expanded=False):
            for item in gp.market_research_checklist:
                st.markdown(item)

        with st.expander(T("gp_compliance"), expanded=False):
            for note in gp.compliance_notes:
                st.markdown(f"• {note}")

    elif gp_btn:
        st.warning(T("gp_none"))


elif st.session_state.page == "ads":
    st.header(T("ads_header"))
    st.caption(T("ads_note"))

    pa_map = PAID_ADS_ZH if LANG == "zh" else PAID_ADS_EN
    ads_tab_keys = ["meta", "google", "tiktok", "tracking", "compliance"]
    ads_tab_labels = [T("ads_tab_meta"), T("ads_tab_google"), T("ads_tab_tiktok"),
                      T("ads_tab_tracking"), T("ads_tab_compliance")]
    _ads_sel = st.tabs(ads_tab_labels)
    for _i, _tk in enumerate(ads_tab_keys):
        with _ads_sel[_i]:
            _entries = pa_map[_tk]
            for _title, _bullets, _table in _entries:
                with st.expander(f"**{_title}**", expanded=False):
                    for _b in _bullets:
                        st.markdown(_b)
                    if _table:
                        _tcap, _thead, _trows = _table
                        st.caption(_tcap)
                        _adf = pd.DataFrame(_trows, columns=_thead)
                        st.dataframe(_adf, use_container_width=True, hide_index=True)
    st.caption(T("ads_footer"))

# ===== 页脚 =====
st.divider()
st.caption(T("footer"))


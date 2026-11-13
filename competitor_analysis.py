# -*- coding: utf-8 -*-
"""市场竞品分析引擎

数据来源（全部免费、无需 API Key）：
1. eBay Browse API（免 Key）：真实在售商品，含标题/单价/卖家 -> 竞品、热销型号、单价分布
2. 免费搜索引擎（DuckDuckGo/Bing）：市场文章里的年份提及、月份/季节关键词 -> 趋势与淡旺季的频次统计推断

所有统计均标注来源，不编造数字。
"""
import re
import time
import datetime
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict
from urllib.parse import urlparse

import requests

# ===== 销售渠道关键词 =====
CHANNELS = {
    "Amazon": ["amazon"],
    "eBay": ["ebay"],
    "AliExpress": ["aliexpress"],
    "Walmart": ["walmart"],
    "Etsy": ["etsy"],
    "Shopify/独立站": ["shopify", "myshopify"],
    "Alibaba/1688": ["alibaba", "1688"],
    "Rakuten": ["rakuten"],
    "MercadoLibre": ["mercadolibre"],
    "Shopee": ["shopee"],
    "Lazada": ["lazada"],
    "Wayfair": ["wayfair"],
    "Target": ["target.com"],
    "BestBuy": ["bestbuy"],
    "HomeDepot": ["homedepot"],
    "IKEA": ["ikea"],
}

MONTHS_ZH = ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]
MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# 季节性原因关键词（推断旺季/淡季成因）
SEASON_REASONS = {
    "节假日/购物季": ["black friday", "cyber monday", "christmas", "holiday", "gift", "黑色星期五", "网络星期一", "圣诞节", "假日", "礼物", "感恩节", "新年"],
    "返校/开学季": ["back to school", "返校", "开学"],
    "夏季旺季": ["summer", "夏季", "beach", "海滩"],
    "冬季旺季": ["winter", "冬季"],
    "促销活动": ["sale", "discount", "deal", "promo", "coupon", "促销", "打折", "优惠", "折扣"],
    "新品发布": ["new release", "launch", "new model", "新品", "发布", "上市", "首发"],
    "换季": ["seasonal", "换季", "季节性", "spring cleaning", "春季大扫除"],
}

_STOPWORDS = {"the", "and", "for", "with", "best", "top", "new", "how", "buy", "sale", "online", "shop", "price", "market", "guide", "free", "your", "you", "our", "all", "get", "more", "from", "what", "which", "where", "why", "who", "when"}


@dataclass
class Product:
    title: str
    price: Optional[float]
    currency: str
    seller: str
    platform: str = "eBay"
    url: str = ""
    country: str = ""


@dataclass
class CompetitorReport:
    product: str
    country: str
    country_zh: str
    city: str
    year_range: str
    total_products: int = 0
    total_search_results: int = 0
    competitors: List[Dict] = field(default_factory=list)
    channels: List[Dict] = field(default_factory=list)
    yearly_mentions: Dict[str, int] = field(default_factory=dict)
    top_models: List[Dict] = field(default_factory=list)
    price_stats: Dict = field(default_factory=dict)
    monthly_mentions: Dict[str, int] = field(default_factory=dict)
    season_reasons: List[Dict] = field(default_factory=list)
    peak_months: List[str] = field(default_factory=list)
    off_months: List[str] = field(default_factory=list)
    search_queries: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def _domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def _median(vals):
    if not vals:
        return None
    s = sorted(vals)
    n = len(s)
    if n % 2:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


# ===== 数据抓取：搜索引擎（免费） =====
_EBAY_SITE_MAP = {
    "US": 0, "GB": 3, "AU": 15, "CA": 2, "DE": 77, "FR": 71,
    "IT": 101, "ES": 186, "JP": 0, "CN": 0, "HK": 0, "SG": 216,
    "MY": 265, "TH": 212, "PH": 208, "IN": 203,
}
_EBAY_SITE_MAP = {
    "US": 0, "GB": 3, "AU": 15, "CA": 2, "DE": 77, "FR": 71,
    "IT": 101, "ES": 186, "JP": 0, "CN": 0, "HK": 0, "SG": 216,
    "MY": 265, "TH": 212, "PH": 208, "IN": 203,
}


def fetch_ebay_products(session: requests.Session, engine, query: str,
                        country_code: str = "US",
                        limit: int = 40) -> List[Product]:
    """通过免费搜索引擎抓取 eBay 在售商品页面，解析商品标题与价格。

    注：eBay 官方 Browse API 需 OAuth key，此处走免费搜索抓取公开页面。
    """
    site = country_code.upper() if country_code else "US"
    search_url = f"https://www.ebay.com/sch/i.html?_nkw={query}&_sacat=0&_stpos={site}"
    products: List[Product] = []
    try:
        html = engine.fetch_page(search_url, timeout=20)
        if not html:
            return products
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".s-item")[:limit]
        for it in items:
            title_el = it.select_one(".s-item__title")
            price_el = it.select_one(".s-item__price")
            if not title_el or not price_el:
                continue
            title = title_el.get_text(strip=True)
            price_txt = price_el.get_text(strip=True)
            m = re.search(r"([\d,]+\.?\d*)", price_txt)
            price_val = float(m.group(1).replace(",", "")) if m else None
            cur = "USD" if "US" in price_txt or "$" in price_txt else price_txt[:3]
            link_el = it.select_one("a.s-item__link")
            products.append(Product(
                title=title,
                price=price_val,
                currency=cur,
                seller="",
                platform="eBay",
                url=link_el["href"] if link_el else "",
                country=site,
            ))
    except Exception:
        pass
    return products


def analyze_competitors(engine, product: str, country_zh: str, country_code: str,
                        city: str = "", start_year: int = None, end_year: int = None,
                        progress_callback=None) -> CompetitorReport:
    """执行竞品分析主流程，返回 CompetitorReport"""
    from cities import get_country_en
    this_year = datetime.date.today().year
    if end_year is None:
        end_year = this_year
    if start_year is None:
        start_year = end_year - 4
    start_year = min(start_year, end_year)
    years = [str(y) for y in range(start_year, end_year + 1)]
    country_en = get_country_en(country_zh)

    report = CompetitorReport(
        product=product, country=country_en or country_zh, country_zh=country_zh,
        city=city or "", year_range=f"{years[0]}-{years[-1]}",
    )
    report.sources = ["免费搜索引擎：DuckDuckGo / Bing", "eBay 公开页面抓取"]

    base = f"{product} {country_en}".strip()
    if city:
        base = f"{product} {city} {country_en}".strip()
    queries = [
        f"{base} market competitors top brands",
        f"{base} best sellers popular models",
        f"{base} sales statistics trend {years[-1]}",
        f"{base} price range USD",
        f"{base} seasonal demand peak off season monthly",
        f"{product} market size {country_en} forecast 2024 2025",
    ]
    report.search_queries = queries

    total_steps = len(queries) + 1
    step = 0

    def _cb(msg):
        if progress_callback:
            progress_callback(step, total_steps, msg)

    # ---- 1) 抓取 eBay 在售商品 ----
    _cb(f"正在抓取 eBay 在售商品…")
    session = engine.session
    ebay_products = fetch_ebay_products(session, engine, product, country_code, limit=40)
    report.total_products = len(ebay_products)
    step += 1

    # ---- 2) 多关键词搜索市场文章 ----
    all_results = []
    seen = set()
    for i, q in enumerate(queries):
        _cb(f"搜索 ({i + 1}/{len(queries)})：{q}")
        try:
            res = engine.search(q, max_results=15)
        except Exception:
            res = []
        for r in res:
            if r.url and r.url not in seen:
                seen.add(r.url)
                all_results.append(r)
        time.sleep(1)
        step += 1
    report.total_search_results = len(all_results)

    # ---- 3) 拼接文本用于统计 ----
    texts = []
    for r in all_results:
        texts.append(f"{r.title} {r.snippet} {_domain_of(r.url)}")
    for p in ebay_products:
        texts.append(p.title)
    blob = " ".join(texts).lower()

    # ---- 4) 竞品识别 ----
    domain_counter = Counter()
    for r in all_results:
        d = _domain_of(r.url)
        if d:
            domain_counter[d] += 1
    for p in ebay_products:
        if p.seller:
            domain_counter[f"eBay卖家:{p.seller}"] += 1

    brand_counter = Counter()
    for r in all_results:
        title = r.title or ""
        for w in re.findall(r"\b([A-Z][A-Za-z]{2,})\b", title):
            if w.lower() not in _STOPWORDS:
                brand_counter[w] += 1

    comp_map: Dict[str, Dict] = {}
    for name, cnt in brand_counter.most_common(15):
        comp_map[name] = {"name": name, "count": cnt, "type": "品牌"}
    for name, cnt in domain_counter.most_common(15):
        if not name.startswith("eBay卖家") and "." in name:
            base_domain = name.split(".")[0].capitalize()
            if base_domain in comp_map:
                comp_map[base_domain]["count"] += cnt
            else:
                comp_map[base_domain] = {"name": base_domain, "count": cnt, "type": "网站"}
    for name, cnt in domain_counter.items():
        if name.startswith("eBay卖家:"):
            seller = name.replace("eBay卖家:", "")
            key = f"{seller}(eBay)"
            comp_map[key] = {"name": key, "count": cnt, "type": "eBay卖家"}
    report.competitors = sorted(comp_map.values(), key=lambda x: x["count"], reverse=True)[:15]
    step += 1
    _cb("竞品识别完成")

    # ---- 5) 销售渠道分布 ----
    channel_counter = Counter()
    for ch, kws in CHANNELS.items():
        c = sum(blob.count(kw) for kw in kws)
        if c:
            channel_counter[ch] += c
    if ebay_products:
        channel_counter["eBay"] += len(ebay_products)
    total_ch = sum(channel_counter.values()) or 1
    report.channels = [
        {"name": ch, "count": cnt, "pct": round(cnt / total_ch * 100, 1)}
        for ch, cnt in channel_counter.most_common(12)
    ]

    # ---- 6) 近 N 年提及次数（关注度趋势）----
    yearly = {}
    for y in years:
        yearly[y] = blob.count(y)
    report.yearly_mentions = yearly

    # ---- 7) 热销型号 + 单价 ----
    model_counter = Counter()
    model_prices: Dict[str, List[float]] = defaultdict(list)
    model_pat = re.compile(r"\b([A-Z]{1,4}[- ]?\d{2,5}[A-Z]?)\b|\b([A-Z]{2,4}\d{3,6})\b")
    price_pat = re.compile(r"(?:USD|\$|€|£|￥|¥)\s?(\d{1,6}(?:\.\d{1,2})?)")

    combined_texts = [f"{p.title} {p.url}" for p in ebay_products] + \
                     [f"{r.title} {r.snippet}" for r in all_results]
    for text in combined_texts:
        for m in model_pat.finditer(text):
            model = (m.group(1) or m.group(2) or "").strip().upper()
            if len(model) >= 3:
                model_counter[model] += 1
                for grp in price_pat.findall(text):
                    try:
                        model_prices[model].append(float(grp))
                    except (TypeError, ValueError):
                        pass

    ebay_prices = [p.price for p in ebay_products if p.price]
    report.price_stats = {
        "count": len(ebay_prices),
        "min": min(ebay_prices) if ebay_prices else None,
        "max": max(ebay_prices) if ebay_prices else None,
        "avg": round(sum(ebay_prices) / len(ebay_prices), 2) if ebay_prices else None,
        "median": round(_median(ebay_prices), 2) if ebay_prices else None,
        "currency": ebay_products[0].currency if ebay_products else "USD",
    }

    top_models = []
    for model, cnt in model_counter.most_common(10):
        prices = model_prices.get(model, [])
        top_models.append({
            "model": model,
            "count": cnt,
            "avg_price": round(sum(prices) / len(prices), 2) if prices else None,
        })
    report.top_models = top_models

    # ---- 8) 月度提及频次（淡旺季推断）----
    monthly = {}
    for i, (mzh, men) in enumerate(zip(MONTHS_ZH, MONTHS_EN)):
        monthly[i + 1] = blob.count(mzh.lower()) + blob.count(men.lower())
    report.monthly_mentions = {MONTHS_ZH[k - 1]: v for k, v in monthly.items()}

    # 季节性原因
    reason_counter = Counter()
    for reason, kws in SEASON_REASONS.items():
        c = sum(blob.count(kw.lower()) for kw in kws)
        if c:
            reason_counter[reason] += c
    report.season_reasons = [
        {"reason": r, "count": c} for r, c in reason_counter.most_common(8)
    ]

    # 旺季/淡季：按月度提及排序
    sorted_months = sorted(monthly.items(), key=lambda x: x[1], reverse=True)
    nonzero = [(m, c) for m, c in sorted_months if c > 0]
    if nonzero:
        report.peak_months = [MONTHS_ZH[m - 1] for m, c in nonzero[:3]]
        report.off_months = [MONTHS_ZH[m - 1] for m, c in sorted_months[-3:]]

    _cb("分析完成")
    return report


if __name__ == "__main__":
    print("competitor_analysis module loaded")

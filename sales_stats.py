"""
销售统计模块 - 统计某商品在目标国家各城市的销售情况

策略：
1. 对每个城市构建搜索关键词，统计搜索结果数量作为热度指标
2. 收集结果中出现的价格、平台、来源信息
3. 按城市汇总，排序输出主要销售城市

注意：搜索引擎不会直接给出销量，本模块用「信息热度」
（搜索结果条数、覆盖平台数、含价信息条数）作为代理指标。
真正销量数据需接入电商平台 API，属后续扩展。
"""

import re
import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from search_engine import SearchEngine
from cities import get_cities, get_country_en

logger = logging.getLogger(__name__)


@dataclass
class CitySalesStat:
    """单个城市的销售统计"""
    city_zh: str
    city_en: str
    result_count: int = 0          # 搜索结果条数（热度）
    shop_count: int = 0            # 涉及店铺/域名数
    platform_count: int = 0        # 涉及电商平台数
    price_mentions: int = 0        # 提到价格的条数
    sample_prices: List[str] = None  # 抽样价格
    top_results: List[Dict] = None  # 代表性结果

    def __post_init__(self):
        if self.sample_prices is None:
            self.sample_prices = []
        if self.top_results is None:
            self.top_results = []

    @property
    def heat_score(self) -> int:
        """综合热度分数 = 结果数 + 店铺数*2 + 平台数*3 + 价格条数"""
        return (
            self.result_count
            + self.shop_count * 2
            + self.platform_count * 3
            + self.price_mentions
        )

    def to_dict(self):
        d = asdict(self)
        d["heat_score"] = self.heat_score
        return d


@dataclass
class SalesReport:
    """整体销售报告"""
    product: str
    country_zh: str
    country_en: str
    cities: List[CitySalesStat]
    total_results: int = 0

    def sorted_cities(self) -> List[CitySalesStat]:
        """按热度降序排列的城市"""
        return sorted(self.cities, key=lambda c: c.heat_score, reverse=True)

    def to_dict(self):
        return {
            "product": self.product,
            "country_zh": self.country_zh,
            "country_en": self.country_en,
            "total_results": self.total_results,
            "cities": [c.to_dict() for c in self.sorted_cities()],
        }


# 主要电商平台域名 → 显示名
PLATFORM_DOMAINS = {
    "amazon": "Amazon",
    "ebay": "eBay",
    "etsy": "Etsy",
    "walmart": "Walmart",
    "alibaba": "Alibaba",
    "aliexpress": "AliExpress",
    "made-in-china": "Made-in-China",
    "shopee": "Shopee",
    "lazada": "Lazada",
    "flipkart": "Flipkart",
    "mercadolibre": "MercadoLibre",
    "otto": "Otto",
    "cdiscount": "Cdiscount",
    "rakuten": "Rakuten",
    "coupang": "Coupang",
    "jd.com": "JD",
    "taobao": "Taobao",
    "tmall": "Tmall",
    "wayfair": "Wayfair",
    "homedepot": "Home Depot",
    "bestbuy": "Best Buy",
    "target": "Target",
}

# 价格正则：支持 $ € £ ¥ 以及 USD/EUR 等写法
PRICE_RE = re.compile(
    r"(?:[$€£¥]\s?\d+(?:[.,]\d{1,2})?)"
    r"|(?:\d+(?:[.,]\d{1,2})?\s?(?:USD|EUR|GBP|JPY|CNY|RMB|AED|SAR|INR|BRL))"
    r"|(?:\d+(?:[.,]\d{1,2})?\s?(?:dollars?|euros?|pounds?))",
    re.IGNORECASE,
)


class SalesStats:
    """销售统计器"""

    def __init__(self, engine: SearchEngine):
        self.engine = engine

    def generate_report(
        self,
        product: str,
        country_zh: str,
        max_cities: int = 8,
        max_results_per_city: int = 20,
        progress_callback=None,
        city_override: Optional[str] = None,
    ) -> SalesReport:
        """
        生成销售统计报告
        :param product: 商品名
        :param country_zh: 国家中文名
        :param max_cities: 最多统计多少个城市
        :param max_results_per_city: 每城市取多少搜索结果
        :param progress_callback: 进度回调 (done, total, message)
        :param city_override: 指定城市中文名；传入时只统计该城市，忽略 max_cities
        :return: 销售报告
        """
        country_en = get_country_en(country_zh)
        if city_override:
            city_en = self._get_city_en(country_zh, city_override)
            cities = [(city_override, city_en)]
        else:
            cities = get_cities(country_zh)[:max_cities]

        stats: List[CitySalesStat] = []
        total = len(cities)
        grand_total = 0

        for i, (city_zh, city_en) in enumerate(cities):
            if progress_callback:
                progress_callback(
                    i, total, f"正在统计 {city_zh} ({i + 1}/{total})..."
                )

            stat = self._stat_city(
                product, country_en, city_zh, city_en, max_results_per_city
            )
            stats.append(stat)
            grand_total += stat.result_count
            time.sleep(0.8)  # 限速，避免封禁

        if progress_callback:
            progress_callback(total, total, "统计完成")

        return SalesReport(
            product=product,
            country_zh=country_zh,
            country_en=country_en,
            cities=stats,
            total_results=grand_total,
        )

    def _stat_city(
        self,
        product: str,
        country_en: str,
        city_zh: str,
        city_en: str,
        max_results: int,
    ) -> CitySalesStat:
        """统计单个城市"""
        stat = CitySalesStat(city_zh=city_zh, city_en=city_en)

        # 短查询词 + for sale/buy 限定，效果比长词好
        queries = [
            f"{product} store {city_en}",
            f"buy {product} {city_en}",
            f"{product} price {city_en}",
        ]

        all_results = []
        seen_urls = set()
        for q in queries:
            res = self.engine.search(q, max_results)
            for r in res:
                if r.url not in seen_urls:
                    seen_urls.add(r.url)
                    all_results.append(r)
            time.sleep(0.5)

        stat.result_count = len(all_results)
        domains = set()
        platforms = set()
        prices = []

        for r in all_results:
            # 域名统计
            try:
                from urllib.parse import urlparse
                d = urlparse(r.url).netloc.replace("www.", "")
                domains.add(d)
            except Exception:
                pass
            # 平台识别
            for key, name in PLATFORM_DOMAINS.items():
                if key in r.url.lower():
                    platforms.add(name)
            # 标题+摘要合并
            text = f"{r.title} {r.snippet}"
            m = PRICE_RE.search(text)
            if m:
                stat.price_mentions += 1
                if len(prices) < 5:
                    prices.append(m.group(0))
            # 代表性结果
            if len(stat.top_results) < 5:
                stat.top_results.append(
                    {"title": r.title, "url": r.url, "snippet": r.snippet}
                )

        stat.shop_count = len(domains)
        stat.platform_count = len(platforms)
        stat.sample_prices = prices
        return stat

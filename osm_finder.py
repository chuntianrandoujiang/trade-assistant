"""
OpenStreetMap 店铺查找模块 - 完全免费，无需 API Key

使用 Overpass API 查询 OSM 数据库中的店铺（POI）。
返回店铺名称、地址、电话、网站、坐标。

注意：
- OSM 数据由志愿者维护，覆盖程度因国家/城市而异
- 发达国家大城市覆盖较好，部分发展中国家可能数据稀疏
- 这是纯免费方案，适合作为 Playwright 搜索的补充/交叉验证
"""

import time
import logging
from typing import List, Optional
from dataclasses import dataclass

import requests

from cities import get_country_en

logger = logging.getLogger(__name__)

# Overpass API 公共实例（免费，无需 Key）
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]

# 商品关键词 → OSM shop=* 标签映射
# OSM 用 shop 标记零售店类型
PRODUCT_TO_OSM = {
    "led": "electrical",
    "灯": "lighting",
    "照明": "lighting",
    "灯饰": "lighting",
    "服装": "clothes",
    "衣服": "clothes",
    "服饰": "clothes",
    "鞋": "shoes",
    "手机": "mobile_phone",
    "电子": "electronics",
    "电脑": "computer",
    "家具": "furniture",
    "超市": "supermarket",
    "食品": "supermarket",
    "汽车": "car",
    "配件": "car_parts",
    "五金": "hardware",
    "工具": "hardware",
    "化妆品": "cosmetics",
    "珠宝": "jewelry",
    "眼镜": "optician",
    "玩具": "toys",
    "体育": "sports",
    "运动": "sports",
    "文具": "stationery",
    "书店": "books",
    "花": "florist",
}


@dataclass
class OsmShop:
    """OSM 店铺信息"""
    name: str = ""
    shop_type: str = ""  # OSM shop 类型
    address: str = ""
    phone: str = ""
    website: str = ""
    email: str = ""
    opening_hours: str = ""
    lat: float = 0.0
    lon: float = 0.0
    city: str = ""
    country: str = ""

    def to_dict(self):
        return self.__dict__.copy()


class OsmFinder:
    """通过 Overpass API 查询 OSM 店铺"""

    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self.proxies = (
            {"http": proxy, "https": proxy} if proxy else None
        )
        self.headers = {
            "User-Agent": "TradeResearchApp/1.0 (research)"
        }

    def _build_query(
        self, city_en: str, osm_tags: List[str]
    ) -> str:
        """
        构建 Overpass QL 查询
        :param city_en: 城市英文名
        :param osm_tags: OSM shop 标签列表
        :return: Overpass QL 查询字符串
        """
        # 对每个标签构建一个 shop=* 过滤器，用 union 合并
        filters = "".join(
            f'node["shop"="{tag}"](area.searchArea);' for tag in osm_tags
        )
        query = f"""
        [out:json][timeout:30];
        area["name"="{city_en}"]["boundary"="administrative"]->.searchArea;
        (
            {filters}
        );
        out body;
        """
        return query

    def _match_osm_tags(self, product: str) -> List[str]:
        """根据商品名匹配 OSM shop 标签"""
        product_lower = product.lower()
        matched = []
        for keyword, tag in PRODUCT_TO_OSM.items():
            if keyword in product_lower:
                matched.append(tag)
        if not matched:
            # 默认：尝试通用零售
            matched = ["shop"]
        return matched

    def find_shops(
        self,
        city_en: str,
        product: str,
        country_zh: str = "",
        max_results: int = 50,
    ) -> List[OsmShop]:
        """
        查询城市内某类商品店铺
        :param city_en: 城市英文名
        :param product: 商品关键词
        :param country_zh: 国家中文名（用于标注）
        :param max_results: 最多返回数量
        :return: OsmShop 列表
        """
        osm_tags = self._match_osm_tags(product)
        query = self._build_query(city_en, osm_tags)

        for url in OVERPASS_URLS:
            try:
                r = requests.post(
                    url,
                    data={"data": query},
                    headers=self.headers,
                    proxies=self.proxies,
                    timeout=45,
                )
                if r.status_code != 200:
                    logger.warning(
                        f"Overpass 返回 {r.status_code}（{url}）"
                    )
                    continue
                data = r.json()
                shops = self._parse_response(data, country_zh, city_en)
                return shops[:max_results]
            except Exception as e:
                logger.warning(f"Overpass 查询失败（{url}）：{e}")
                continue
        return []

    def _parse_response(
        self, data: dict, country_zh: str, city_en: str
    ) -> List[OsmShop]:
        """解析 Overpass JSON 响应"""
        shops = []
        for el in data.get("elements", []):
            tags = el.get("tags", {})
            name = tags.get("name", "")
            if not name:
                continue  # 无名店铺跳过

            # 地址拼接
            addr_parts = []
            if tags.get("addr:housenumber"):
                addr_parts.append(tags["addr:housenumber"])
            if tags.get("addr:street"):
                addr_parts.append(tags["addr:street"])
            if tags.get("addr:city"):
                addr_parts.append(tags["addr:city"])
            address = ", ".join(addr_parts)

            shop = OsmShop(
                name=name,
                shop_type=tags.get("shop", ""),
                address=address,
                phone=tags.get("phone", "") or tags.get("contact:phone", ""),
                website=(
                    tags.get("website", "") or tags.get("contact:website", "")
                ),
                email=tags.get("email", "") or tags.get("contact:email", ""),
                opening_hours=tags.get("opening_hours", ""),
                lat=el.get("lat", 0.0),
                lon=el.get("lon", 0.0),
                city=city_en,
                country=country_zh,
            )
            shops.append(shop)
        return shops


def product_to_osm_tag_hint(product: str) -> str:
    """给 UI 展示用的标签提示"""
    finder = OsmFinder()
    tags = finder._match_osm_tags(product)
    return ", ".join(tags)

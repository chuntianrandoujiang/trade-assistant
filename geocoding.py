"""
地理编码模块 - 把地址/城市/店铺地址转换为经纬度

使用 OpenStreetMap Nominatim（完全免费，无需 API 密钥）
注意：Nominatim 有频率限制（1秒1次），需要限速。
"""

import time
import logging
from typing import Optional, Tuple, Dict

import requests

logger = logging.getLogger(__name__)

# 内存缓存，避免重复请求
_cache: Dict[str, Optional[Tuple[float, float]]] = {}

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {
    "User-Agent": "TradeResearchApp/1.0 (educational/commercial research)"
}


def geocode(
    query: str,
    proxy: Optional[str] = None,
    timeout: int = 10,
    use_cache: bool = True,
) -> Optional[Tuple[float, float]]:
    """
    地理编码：地址/地名 → (lat, lon)
    :param query: 查询字符串，如 "New York" 或 "123 Main St, London"
    :param proxy: 代理地址（可选）
    :param timeout: 超时
    :param use_cache: 是否使用缓存
    :return: (纬度, 经度) 或 None
    """
    if not query or not query.strip():
        return None

    key = query.strip().lower()
    if use_cache and key in _cache:
        return _cache[key]

    proxies = {"http": proxy, "https": proxy} if proxy else None
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
    }
    try:
        r = requests.get(
            NOMINATIM_URL,
            params=params,
            headers=HEADERS,
            proxies=proxies,
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            _cache[key] = (lat, lon)
            time.sleep(1.1)  # Nominatim 限速：1秒/次
            return (lat, lon)
        _cache[key] = None
    except Exception as e:
        logger.warning(f"地理编码失败 [{query}]: {e}")
        _cache[key] = None

    return _cache.get(key)


def geocode_shop(
    shop_address: str,
    city_en: str,
    country_en: str,
    proxy: Optional[str] = None,
) -> Optional[Tuple[float, float]]:
    """
    优先用店铺详细地址定位，失败则用城市中心坐标
    :param shop_address: 店铺地址
    :param city_en: 城市英文名
    :param country_en: 国家英文名
    :param proxy: 代理
    :return: (lat, lon) 或 None
    """
    # 第一优先：店铺详细地址
    if shop_address:
        full = f"{shop_address}, {city_en}, {country_en}"
        r = geocode(full, proxy=proxy)
        if r:
            return r

    # 第二优先：城市 + 国家
    r = geocode(f"{city_en}, {country_en}", proxy=proxy)
    if r:
        return r

    # 兜底：仅城市
    return geocode(city_en, proxy=proxy)

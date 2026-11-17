"""
TomTom 地点搜索模块 - 免费 5万请求/天（需免费注册 API Key）

官网申请：https://developer.tomtom.com/maps/keys
免费 Key 可用于 200+ 国家的 POI 搜索与地理编码。
未配置 Key 时本模块自动跳过，不影响其他数据源。
"""

import logging
from typing import List, Optional, Dict

import requests

logger = logging.getLogger(__name__)

SEARCH_URL = "https://api.tomtom.com/search/2/search"
GEOCODE_URL = "https://api.tomtom.com/search/2/geocode"

HEADERS = {"User-Agent": "TradeResearchApp/1.0 (research)"}


class TomTomFinder:
    """通过 TomTom Search API 查询地点/店铺"""

    def __init__(self, api_key: str = "", proxy: Optional[str] = None):
        self.api_key = (api_key or "").strip()
        self.proxy = proxy
        self.proxies = (
            {"http": proxy, "https": proxy} if proxy else None
        )

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _auth_headers(self) -> Dict[str, str]:
        return {**HEADERS, "apiKey": self.api_key}

    def find_places(
        self,
        query: str,
        lat: float,
        lon: float,
        max_results: int = 10,
    ) -> List[Dict]:
        """
        在指定坐标附近搜索地点（如某城市内某类店铺）
        :return: [{name, address, phone, website, email, lat, lon, source}]
        """
        if not self.enabled:
            return []
        try:
            r = requests.get(
                f"{SEARCH_URL}/{query.strip().replace(' ', '%20')}.json",
                params={
                    "key": self.api_key,
                    "limit": min(max_results, 50),
                    "position": f"{lat},{lon}",
                },
                headers=self._auth_headers(),
                proxies=self.proxies,
                timeout=20,
            )
            if r.status_code == 401:
                logger.warning("TomTom Key 无效（401），请到 my.tomtom.com 检查")
                return []
            if r.status_code != 200:
                logger.warning(f"TomTom 返回 {r.status_code}")
                return []
            shops = []
            for place in (r.json().get("results") or []):
                # v2 结构：店铺详情在 poi 字段（name/phone/url），坐标在 position
                poi = place.get("poi") or {}
                position = place.get("position") or {}
                address = place.get("address") or {}
                street = (
                    f"{address.get('streetName','')} {address.get('streetNumber','')}".strip()
                )
                locality = ", ".join(
                    x for x in [
                        address.get("municipalitySubdivision", ""),
                        address.get("municipality", ""),
                        address.get("countrySubdivisionName", ""),
                    ] if x
                )
                addr_line = f"{street}, {locality}".strip(", ")
                website = poi.get("url", "")
                if website and not website.startswith("http"):
                    website = f"https://{website}"
                shops.append(
                    {
                        "name": (poi.get("name") or "").strip(),
                        "address": addr_line,
                        "phone": (poi.get("phone") or "").strip(),
                        "website": website.strip(),
                        "email": "",
                        "lat": position.get("lat", 0.0),
                        "lon": position.get("lon", 0.0),
                        "source": "tomtom",
                    }
                )
            return shops
        except Exception as e:
            logger.warning(f"TomTom 查询失败：{e}")
            return []

    def geocode(
        self, query: str
    ) -> Optional[Dict[str, float]]:
        """
        地址 → 坐标（补充 Nominatim 的失败场景）
        :return: {"lat": x, "lon": y} 或 None
        """
        if not self.enabled or not query or not query.strip():
            return None
        try:
            r = requests.get(
                f"{GEOCODE_URL}/{query.strip().replace(' ', '%20').replace('/', '%2F')}.json",
                params={"key": self.api_key, "limit": "1"},
                headers=self._auth_headers(),
                proxies=self.proxies,
                timeout=15,
            )
            if r.status_code != 200:
                return None
            results = (r.json().get("results") or [])
            if not results:
                return None
            pos = results[0].get("position") or {}
            return {"lat": pos.get("lat", 0.0), "lon": pos.get("lon", 0.0)}
        except Exception as e:
            logger.warning(f"TomTom 地理编码失败：{e}")
            return None

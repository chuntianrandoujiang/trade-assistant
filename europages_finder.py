"""
Europages B2B 企业目录抓取模块 - 完全免费，无需 Key

Europages 是欧洲最大的 B2B 供应商目录（260万+ 国际供应商，45 国）。
本模块直接抓取其公开搜索页，无需登录。

注意：
- 只能访问公开搜索页，频率限制：每次搜索间隔 2 秒
- 返回的公司含名称/城市/国家/电话/网站，邮箱通常在详情页
"""

import time
import logging
from typing import List, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# 国家中文名 → Europages 国家代码（小写）
COUNTRY_CODES = {
    "英国": "uk", "德国": "de", "法国": "fr", "荷兰": "nl",
    "比利时": "be", "西班牙": "es", "意大利": "it", "奥地利": "at",
    "瑞典": "se", "波兰": "pl", "瑞士": "ch", "爱尔兰": "ie",
    "葡萄牙": "pt", "捷克": "cz", "丹麦": "dk", "芬兰": "fi",
    "挪威": "no", "匈牙利": "hu", "罗马尼亚": "ro", "希腊": "gr",
    "美国": "us", "加拿大": "ca", "澳大利亚": "au", "新西兰": "nz",
    "中国": "cn", "日本": "jp", "韩国": "kr", "印度": "in",
    "巴西": "br", "墨西哥": "mx", "新加坡": "sg",
}

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


class EuropagesFinder:
    """抓取 Europages 公开搜索页的公司列表"""

    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self.proxies = (
            {"http": proxy, "https": proxy} if proxy else None
        )
        self.headers = {
            "User-Agent": UA,
            "Accept-Language": "en-US,en;q=0.9",
        }
        self._last_request = 0.0

    def _wait_throttle(self):
        elapsed = time.time() - self._last_request
        if elapsed < 2.0:
            time.sleep(2.0 - elapsed)
        self._last_request = time.time()

    def find_companies(
        self,
        product: str,
        country_zh: str,
        city_en: Optional[str] = None,
        max_results: int = 20,
    ) -> List[dict]:
        """
        在 Europages 搜索某国某商品的公司
        :param product: 商品关键词（英文）
        :param country_zh: 国家中文名
        :param city_en: 城市英文名（可选）
        :param max_results: 最多返回数量
        :return: [{name, city, country, phone, website, email, address, source}]
        """
        code = COUNTRY_CODES.get(country_zh, "")
        if not code:
            logger.info(f"Europages 不支持国家：{country_zh}，跳过")
            return []

        url = (
            f"https://www.europages.co.uk/companies/"
            f"{quote(product)}.html?country={code}"
        )
        if city_en:
            url += f"&city={quote(city_en)}"

        self._wait_throttle()
        try:
            r = requests.get(
                url,
                headers=self.headers,
                proxies=self.proxies,
                timeout=30,
                allow_redirects=True,
            )
            if r.status_code != 200:
                logger.warning(f"Europages 返回 {r.status_code}")
                return []
        except Exception as e:
            logger.warning(f"Europages 请求失败：{e}")
            return []

        return self._parse_list_page(r.text, product, country_zh, max_results)

    def _parse_list_page(
        self, html: str, product: str, country_zh: str, max_results: int
    ) -> List[dict]:
        """解析搜索列表页"""
        soup = BeautifulSoup(html, "html.parser")
        results: List[dict] = []

        # Europages 列表页公司卡片结构
        cards = soup.select(
            "div.company-card, div[class*='company'], article"
        )

        for card in cards:
            # 公司名
            name_el = card.select_one(
                "h2, h3, a[class*='name'], a[title]"
            )
            name = (name_el.get_text(strip=True) if name_el else "").strip()
            if not name or len(name) < 2:
                continue

            # 网站链接
            website = ""
            link_el = card.select_one("a[href*='http']")
            if link_el:
                website = link_el.get("href", "")

            # 电话（Europages 列表页一般不直接显示电话，多为 "Request" 按钮）
            phone = ""
            phone_el = card.select_one(
                "a[href*='tel:'], span[class*='phone']"
            )
            if phone_el:
                phone = phone_el.get("href", "").replace("tel:", "").strip()

            # 城市
            city = ""
            city_el = card.select_one(
                "span[class*='city'], span[class*='location']"
            )
            if city_el:
                city = city_el.get_text(strip=True)

            results.append(
                {
                    "name": name,
                    "city": city,
                    "country": country_zh,
                    "phone": phone,
                    "website": website,
                    "email": "",
                    "address": "",
                    "source": "europages",
                }
            )
            if len(results) >= max_results:
                break

        logger.info(f"Europages 解析到 {len(results)} 家公司")
        return results

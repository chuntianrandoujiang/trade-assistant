"""
店铺查找模块 - 搜索目标国家的店铺并提取联系方式

策略：
1. 为每个目标城市生成搜索关键词
2. 调用搜索引擎获取店铺候选
3. 访问候选网页提取联系方式（电话/邮箱/地址）
"""

import re
import math
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from search_engine import SearchEngine, SearchResult
from cities import get_cities, get_country_en
from geocoding import geocode, geocode_shop
from phone_utils import is_valid_phone

logger = logging.getLogger(__name__)


@dataclass
class Shop:
    """店铺信息"""
    name: str = ""
    city: str = ""
    country: str = ""
    product: str = ""
    website: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    contact_person: str = ""  # 联系人
    lat: float = 0.0  # 纬度
    lon: float = 0.0  # 经度
    geo_approx: bool = False  # 坐标是否为城市中心附近近似值
    source: str = ""  # 来源搜索引擎
    detail_url: str = ""  # 详情页链接
    snippet: str = ""

    def to_dict(self):
        return asdict(self)


class ShopFinder:
    """店铺查找器"""

    # 邮箱正则
    EMAIL_RE = re.compile(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    )
    # 电话正则（宽松，兼容国际格式）
    PHONE_RE = re.compile(
        r"(?:\+?\d{1,3}[\s\-]?)?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}"
    )
    # 搜索结果白名单：批发/店铺/黄页类站点
    B2B_SITES = [
        "alibaba.com", "made-in-china.com", "global.hktdc.com",
        "exporters.sg", "tradeindia.com", "indiamart.com",
        "europages.com", "kompass.com", "yellowpages.com",
        "yelp.com", "thomsonlocal.com", "gelbeseiten.de",
    ]

    def __init__(self, engine: SearchEngine):
        """
        :param engine: 搜索引擎实例
        """
        self.engine = engine
        self.proxy = engine.proxy

    def find_shops(
        self,
        country_zh: str,
        product: str,
        city_zh: Optional[str] = None,
        max_cities: int = 6,
        max_results_per_city: int = 10,
        fetch_details: bool = True,
        progress_callback=None,
    ) -> List[Shop]:
        """
        查找目标国家/城市的店铺
        :param country_zh: 国家中文名
        :param product: 商品名
        :param city_zh: 城市中文名（可选，None 表示搜全国）
        :param max_cities: 搜全国时最多搜索的城市数
        :param max_results_per_city: 每个城市最大结果数
        :param fetch_details: 是否访问详情页抓取联系方式
        :param progress_callback: 进度回调 (已完成数, 总数)
        :return: 店铺列表
        """
        country_en = get_country_en(country_zh)
        # 决定要搜索的城市范围
        if city_zh:
            cities = [
                (city_zh, self._get_city_en(country_zh, city_zh))
            ]
        else:
            cities = get_cities(country_zh)[:max_cities]  # 限制城市数

        shops: List[Shop] = []
        seen_websites = set()
        seen_domains = set()
        total = len(cities)

        for i, (city_cn, city_en) in enumerate(cities, 1):
            if progress_callback:
                progress_callback(i - 1, total, f"正在搜索 {city_cn}...")

            # 先用 Google Maps 商户接口拿实体店（地址/电话/坐标最完整）
            place_shops = self._search_places_for_city(
                product, country_zh, city_cn, city_en, max_results_per_city
            )
            for shop in place_shops:
                key = shop.website or shop.name.lower()
                if key in seen_websites:
                    continue
                seen_websites.add(key)
                if shop.website:
                    try:
                        seen_domains.add(
                            urlparse(shop.website).netloc.replace("www.", "")
                        )
                    except Exception:
                        pass
                shops.append(shop)

            queries = self._build_queries(product, country_en, city_en)
            search_results = self.engine.search_multi_queries(
                queries, max_results_per_city
            )

            for sr in search_results:
                # 过滤百科/社交等无关结果
                if self.is_noise_result(sr.url):
                    continue
                # 按域名去重（同一域名的不同页面只保留第一条）
                try:
                    domain = urlparse(sr.url).netloc.replace("www.", "")
                except Exception:
                    domain = sr.url
                if domain in seen_domains:
                    continue
                seen_domains.add(domain)
                shop = self._search_result_to_shop(
                    sr, country_zh, city_cn, product
                )
                if not shop.name:
                    continue
                key = shop.website or shop.name
                if key in seen_websites:
                    continue
                seen_websites.add(key)
                shops.append(shop)

        # 访问详情页抓取联系方式
        if fetch_details:
            total = len(shops)
            for i, shop in enumerate(shops):
                if progress_callback:
                    progress_callback(
                        i, total, f"正在抓取联系方式 ({i + 1}/{total})..."
                    )
                if shop.detail_url and not (shop.phone and shop.email):
                    self._enrich_shop(shop)

        # 地理编码（为地图展示准备坐标）
        # 优化：城市中心坐标只查一次并复用，避免逐店重复请求
        country_en = get_country_en(country_zh)
        city_center_cache = {}
        total = len(shops)
        for i, shop in enumerate(shops):
            if progress_callback:
                progress_callback(
                    i, total, f"正在定位坐标 ({i + 1}/{total})..."
                )
            city_en = self._get_city_en(country_zh, shop.city)

            # 地图接口已返回精确坐标，无需再次地理编码
            if shop.lat and shop.lon:
                continue

            # 城市中心（每个城市只查一次）
            if city_en not in city_center_cache:
                city_center_cache[city_en] = geocode(
                    f"{city_en}, {country_en}", proxy=self.proxy, timeout=8
                ) or geocode(city_en, proxy=self.proxy, timeout=8)
            center = city_center_cache[city_en]

            # 先尝试详细地址，失败则用城市中心附近散开的近似点
            coord = None
            if shop.address:
                addr = re.split(
                    r"(?:Store hours|Business Hours|Opening Hours|Hours\s*:|"
                    r"Corner of|About Contact|Contact Us|Instagram|FAQs|HELP &|Privacy)",
                    shop.address,
                    flags=re.IGNORECASE,
                )[0].strip(" ,.;")
                variants = [addr]
                if "," in addr:
                    variants.append(addr.split(",")[0])
                for variant in variants:
                    coord = geocode(
                        f"{variant}, {city_en}, {country_en}",
                        proxy=self.proxy,
                        timeout=8,
                    )
                    if coord:
                        break
            if coord:
                shop.lat, shop.lon = coord
            elif center:
                # 同一城市中心坐标会让多家店铺完全重叠，
                # 按店铺信息生成确定性小偏移，只为地图可读性
                seed = sum(ord(ch) for ch in (shop.website or shop.name))
                angle = (seed % 360) * math.pi / 180
                radius = 0.006 + (seed % 7) * 0.0015
                shop.lat = center[0] + radius * math.cos(angle)
                shop.lon = center[1] + radius * math.sin(angle) / max(
                    math.cos(math.radians(center[0])), 0.2
                )
                shop.geo_approx = True

        if progress_callback:
            progress_callback(total, total, "搜索完成")

        return shops

    @staticmethod
    def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """计算两点间球面距离（公里）"""
        r = 6371.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = (
            math.sin(dp / 2) ** 2
            + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        )
        return 2 * r * math.asin(math.sqrt(a))

    def _search_places_for_city(
        self,
        product: str,
        country_zh: str,
        city_cn: str,
        city_en: str,
        max_results: int,
    ) -> List[Shop]:
        """通过 Google Maps 商户接口获取本地实体店"""
        places = self.engine.search_places(
            f"{product} store {city_en}", max_results=max(max_results, 20)
        )
        if not places:
            places = self.engine.search_places(
                f"{product} {city_en}", max_results=max(max_results, 20)
            )

        country_en = get_country_en(country_zh)
        center = geocode(
            f"{city_en}, {country_en}", proxy=self.proxy, timeout=8
        )
        if not center:
            center = geocode(f"{city_en}", proxy=self.proxy, timeout=8)

        shops: List[Shop] = []
        for item in places:
            name = (item.get("title") or "").strip()
            if not name:
                continue
            lat = float(item.get("latitude") or 0)
            lon = float(item.get("longitude") or 0)
            if center and lat and lon:
                if self._distance_km(center[0], center[1], lat, lon) > 100:
                    continue
            rating = item.get("rating")
            category = item.get("category") or ""
            snippet_parts = [p for p in [category] if p]
            if rating:
                snippet_parts.append(f"评分 {rating}")
            shops.append(
                Shop(
                    name=name,
                    city=city_cn,
                    country=country_zh,
                    product=product,
                    website=item.get("website") or "",
                    phone=item.get("phoneNumber") or "",
                    address=item.get("address") or "",
                    lat=float(item.get("latitude") or 0),
                    lon=float(item.get("longitude") or 0),
                    source="google_maps",
                    detail_url=item.get("website") or "",
                    snippet=" · ".join(snippet_parts),
                )
            )
        return shops

    @staticmethod
    def _get_city_en(country_zh: str, city_zh: str) -> str:
        """获取城市英文名"""
        for cn, en in get_cities(country_zh):
            if cn == city_zh:
                return en
        return city_zh

    @staticmethod
    def _build_queries(
        product: str, country_en: str, city_en: str
    ) -> List[str]:
        """
        构建多个搜索关键词
        经验证：短词 + store/shop/near 限定词效果最好。
        太长的查询词会被 Bing 降权，返回百科类无关结果。
        """
        return [
            # 店铺类：product + store/shop + city（最有效）
            f"{product} store {city_en}",
            f"{product} shop near {city_en}",
            # 批发/经销类
            f"{product} wholesale {city_en}",
            # 带联系方式意图
            f"{product} store {city_en} phone address",
        ]

    # 无关结果的域名黑名单（百科/词典/社交等非店铺站点）
    NOISE_DOMAINS = [
        "wikipedia.org", "wikimedia", "merriam-webster.com",
        "dictionary.com", "britannica.com", "quora.com",
        "reddit.com", "youtube.com", "facebook.com", "twitter.com",
        "instagram.com", "linkedin.com", "pinterest.com", "tiktok.com",
        "amazon.com/gp/", "apps.apple.com", "play.google.com",
        ".edu", ".gov", "zhihu.com", "baidu.com", "baike",
        "blog", "forum", "news", "wikipedia", "encyclopedia",
        # 聚合/评测/媒体类（非实际店铺）
        "yelp.com", "tripadvisor.com", "cbsnews.com", "nbcnews.com",
        "hola.com", "lonelyplanet.com", "travelandleisure.com",
        "timeout.com", "thrillist.com", "yelp.ca", "yelp.co.uk",
    ]

    @classmethod
    def is_noise_result(cls, url: str) -> bool:
        """判断搜索结果是否为百科/社交等无关站点"""
        u = url.lower()
        return any(d in u for d in cls.NOISE_DOMAINS)

    def _search_result_to_shop(
        self,
        sr: SearchResult,
        country_zh: str,
        city_zh: str,
        product: str,
    ) -> Shop:
        """把搜索结果转换为 Shop 雏形"""
        shop = Shop(
            country=country_zh,
            city=city_zh,
            product=product,
            website=sr.url,
            source=sr.source,
            snippet=sr.snippet,
        )
        # 从 URL 提取域名作为店铺名兜底
        try:
            domain = urlparse(sr.url).netloc
            shop.name = domain.replace("www.", "")
        except Exception:
            shop.name = sr.title[:50]

        # 从标题提取可能更友好的名字
        title = sr.title
        # 去掉常见分隔符后的修饰词
        for sep in ["|", "–", "—", "-"]:
            if sep in title and len(title.split(sep)[0].strip()) > 3:
                shop.name = title.split(sep)[0].strip()
                break
        else:
            shop.name = title[:60]

        # 详情页 URL：优先 B2B 站点，其次原 URL
        shop.detail_url = sr.url

        # 从 snippet 中先尝试提取联系方式
        if sr.snippet:
            self._extract_contacts(snippet=sr.snippet, shop=shop)
        return shop

    def _enrich_shop(self, shop: Shop):
        """访问详情页补全联系方式"""
        html = self.engine.fetch_page(shop.detail_url, timeout=12)
        if not html:
            return
        self._extract_contacts(html=html, shop=shop)

    def _extract_contacts(
        self,
        shop: Shop,
        html: Optional[str] = None,
        snippet: Optional[str] = None,
    ):
        """从文本或 HTML 中提取联系方式"""
        text = ""
        soup = None
        if html:
            soup = BeautifulSoup(html, "lxml")
            # 移除 script/style
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()

            # 检测 meta 标签中的联系信息
            for meta in soup.find_all("meta"):
                content = meta.get("content", "")
                if not shop.email and "@" in content:
                    m = self.EMAIL_RE.search(content)
                    if m:
                        shop.email = m.group(0).lower()
                if not shop.phone and re.search(r"\+\d", content):
                    intl = re.search(
                        r"\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{2,4}[\s\-]?\d{2,4}",
                        content,
                    )
                    if intl:
                        shop.phone = intl.group(0).strip()

            # 检测 mailto 和 tel 链接
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("mailto:") and not shop.email:
                    email = href.replace("mailto:", "").strip().lower()
                    if "@" in email and self.EMAIL_RE.match(email):
                        shop.email = email
                elif href.startswith("tel:") and not shop.phone:
                    phone = href.replace("tel:", "").strip()
                    digits = re.sub(r"\D", "", phone)
                    if 7 <= len(digits) <= 15:
                        shop.phone = phone

            # 优先从带联系字样的区域提取
            contact_sections = soup.find_all(
                string=re.compile(
                    r"contact|电话|邮箱|地址|phone|email|address|tel:|mailto:|联系",
                    re.IGNORECASE,
                )
            )
            body_text = soup.get_text(" ", strip=True)
            text = body_text[:5000]
            # 收集联系区域的文本
            contact_texts = []
            for cs in contact_sections[:5]:
                parent = cs.parent
                if parent:
                    # 尝试取父元素的父元素（更宽范围）
                    grandparent = parent.parent
                    scope = grandparent if grandparent else parent
                    section_text = scope.get_text(" ", strip=True)[:800]
                    contact_texts.append(section_text)
            if contact_texts:
                text = " || ".join(contact_texts) + " || " + text

            # 尝试从 footer/header 找联系信息
            for tag_name in ["footer", "header"]:
                section = soup.find(tag_name)
                if section:
                    section_text = section.get_text(" ", strip=True)[:1000]
                    text = text + " || " + section_text

        elif snippet:
            text = snippet

        if not text:
            return

        # 邮箱
        if not shop.email:
            for m in self.EMAIL_RE.finditer(text):
                email = m.group(0).lower()
                # 过滤掉明显的图片占位/通用/无意义邮箱
                skip_domains = [".png", ".jpg", ".gif", ".webp", ".svg"]
                skip_locals = ["example", "test", "user@", "name@", "email@"]
                if not any(email.endswith(d) for d in skip_domains):
                    if not any(sl in email for sl in skip_locals):
                        shop.email = email
                        break

        # 电话
        if not shop.phone:
            # 搜索带 + 号的国际号码优先
            intl = re.search(
                r"\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{2,4}[\s\-]?\d{2,4}(?:[\s\-]?\d{2,4})?",
                text,
            )
            if intl and is_valid_phone(intl.group(0)):
                shop.phone = intl.group(0).strip()
            elif intl:
                shop.phone = intl.group(0).strip()
            else:
                # 多个电话匹配时取第一个合理的
                for m in self.PHONE_RE.finditer(text):
                    phone = m.group(0).strip()
                    if is_valid_phone(phone):
                        shop.phone = phone
                        break

        # 地址（严格规则：必须含门牌号 + 街道后缀，或含邮编）
        if not shop.address:
            shop.address = self._extract_address(text)

        # 联系人（严格规则：2-3 个英文姓名，排除常见废词）
        if not shop.contact_person:
            shop.contact_person = self._extract_contact_person(text)

    # 地址中的垃圾词组（一旦出现则丢弃该候选）
    ADDRESS_JUNK = [
        "quick links", "mailing list", "privacy", "careers", "skip to",
        "shop all", "sort by", "filters", "availability", "in stock",
        "minimum order", "membership", "quote form", "add to cart",
        "free shipping", "sign up", "log in", "cookie", "newsletter",
        "subscribe", "terms", "refund", "return policy",
    ]

    # 联系人中的废词（一旦命中则不当作姓名）
    PERSON_STOPWORDS = {
        "us", "u.s", "usa", "info", "start", "faq", "faqs", "customer",
        "care", "person", "about", "volume", "instagram", "contact",
        "phone", "email", "address", "shop", "home", "careers", "privacy",
        "policy", "store", "details", "view", "call", "repair", "heavy",
        "premium", "skip", "content", "get", "head", "order", "sales",
        "support", "service", "services", "team", "company", "page",
        "menu", "search", "account", "login", "cart", "help", "hours",
    }

    # 街道后缀
    STREET_SUFFIX = (
        r"(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|"
        r"Drive|Dr|Way|Place|Pl|Court|Ct|Highway|Hwy|Parkway|Pkwy|Square|Sq)"
    )

    def _extract_address(self, text: str) -> str:
        """
        提取真实地址：要么含门牌号+街道后缀，要么含邮编
        """
        candidates = []

        # 模式1：门牌号 + 街名 + 街道后缀（英文）
        for m in re.finditer(
            r"\d{1,6}\s+[A-Z][\w\.\-]*(?:\s+[A-Z][\w\.\-]*){0,4}\s+"
            + self.STREET_SUFFIX
            + r"\b[^\n|]{0,60}",
            text,
        ):
            candidates.append(m.group(0).strip())

        # 模式2：含邮编的地址（如 "Valley Stream, NY 11581"）
        for m in re.finditer(
            r"[A-Z][\w\s\.\-]{2,40},\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?", text
        ):
            candidates.append(m.group(0).strip())

        # 模式3：Address: xxx 形式
        for m in re.finditer(
            r"(?:Address|Addr|\u5730\u5740)[:\s]+([^\n|]{10,120})", text, re.IGNORECASE
        ):
            candidates.append(m.group(1).strip())

        # 模式4：中文地址
        for m in re.finditer(
            r"[\u4e00-\u9fa5]{2,10}(?:\u7701|\u5e02|\u533a|\u9547)"
            r"[\u4e00-\u9fa5\d]{2,40}(?:\u8def|\u8857|\u9053|\u5df7|\u5f04|\u53f7)[\u4e00-\u9fa5\d\-]{0,20}",
            text,
        ):
            candidates.append(m.group(0).strip())

        for cand in candidates:
            # 去掉紧跟在地址后的电话残留，如 "· (312) 440-3580"
            cand = re.split(r"\s*·\s*\(?\d", cand)[0].strip()
            # 截断常见杂项（营业时间、路口描述等）
            cand = re.split(
                r"(?:Store hours|Business Hours|Opening Hours|Hours\s*:|"
                r"Mon(?:day)?\s*[-\u2013]|Corner of|About Contact|Contact Us|Instagram|FAQs|HELP &|Privacy|Opens |\bToday |\bTomorrow |\bGet\b|Phone:|Email:)",
                cand,
                flags=re.IGNORECASE,
            )[0].strip(" ,.;")
            low = cand.lower()
            if len(cand) < 10 or len(cand) > 160:
                continue
            if any(j in low for j in self.ADDRESS_JUNK):
                continue
            # 至少要有一个数字（门牌号或邮编）
            if not re.search(r"\d", cand):
                continue
            return cand.rstrip(" .,;")
        return ""

    def _extract_contact_person(self, text: str) -> str:
        """
        提取真实姓名：2-3 个首字母大写的单词，且不含常见废词
        """
        patterns = [
            r"(?:Contact person|Contact name|Attn|Attention|\u8054\u7cfb\u4eba)[:\s]+"
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})",
            r"\b(?:Mr|Mrs|Ms|Dr)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})",
        ]
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                name = m.group(1).strip()
                words = [w for w in name.split() if w]
                if not (2 <= len(words) <= 3):
                    continue
                if any(w.lower().strip(".,") in self.PERSON_STOPWORDS for w in words):
                    continue
                if all(len(w) >= 2 and w[0].isupper() for w in words):
                    return name
        return ""

"""
搜索引擎模块 - 外贸调研工具核心

功能：
1. 通过本地代理访问外网
2. 支持 DuckDuckGo HTML、Bing 等搜索引擎
3. 失败时自动切换到 Playwright 浏览器渲染
4. 返回结构化的搜索结果
"""

import re
import time
import logging
import base64
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from urllib.parse import quote_plus, urlparse, parse_qs, unquote

import requests
from bs4 import BeautifulSoup

from config import get_serper_key

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """单条搜索结果"""
    title: str
    url: str
    snippet: str
    source: str  # 引擎名称

    def to_dict(self):
        return asdict(self)


class ProxyConfig:
    """本地代理配置"""

    # 常见本地代理端口（按优先级）
    CANDIDATE_PORTS = [7890, 7897, 10809, 1080, 8118, 2080, 10808]

    @staticmethod
    def detect_working_proxy() -> Optional[str]:
        """自动探测可用的本地代理端口"""
        import socket
        for port in ProxyConfig.CANDIDATE_PORTS:
            s = socket.socket()
            s.settimeout(0.5)
            try:
                s.connect(("127.0.0.1", port))
                s.close()
                proxy = f"http://127.0.0.1:{port}"
                # 验证代理是否真的能访问外网
                try:
                    requests.get(
                        "https://www.google.com/generate_204",
                        proxies={"http": proxy, "https": proxy},
                        timeout=5,
                    )
                    return proxy
                except Exception:
                    continue
            except Exception:
                s.close()
                continue
        return None


class SearchEngine:
    """搜索引擎封装：DuckDuckGo HTML 优先，Bing 备用，Playwright 兜底"""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) "
        "Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    ]

    def __init__(self, proxy: Optional[str] = None):
        """
        初始化
        :param proxy: 代理地址，如 http://127.0.0.1:7897。None 则自动检测
        """
        self.proxy = proxy or ProxyConfig.detect_working_proxy()
        self.proxies = (
            {"http": self.proxy, "https": self.proxy} if self.proxy else None
        )
        self.session = requests.Session()
        if self.proxies:
            self.session.proxies.update(self.proxies)
        self.session.headers.update({"User-Agent": self.USER_AGENTS[0]})
        self.serper_key = get_serper_key()
        logger.info(f"SearchEngine 初始化完成，代理: {self.proxy}")

    def search(self, query: str, max_results: int = 20) -> List[SearchResult]:
        """
        执行搜索，自动选择可用的引擎
        :param query: 搜索关键词
        :param max_results: 最大结果数
        :return: 搜索结果列表
        """
        results = []
        # 尝试顺序：Serper API（最优质）→ DuckDuckGo HTML → Bing → Playwright
        for engine_name, engine_func in [
            ("serper", self._search_serper),
            ("duckduckgo", self._search_duckduckgo),
            ("bing", self._search_bing),
        ]:
            try:
                logger.info(f"尝试引擎: {engine_name}, query: {query}")
                results = engine_func(query, max_results)
                if results:
                    logger.info(f"引擎 {engine_name} 返回 {len(results)} 条结果")
                    return results
            except Exception as e:
                logger.warning(f"引擎 {engine_name} 失败: {e}")

        # HTTP 方式全部失败，尝试 Playwright
        try:
            logger.info("尝试 Playwright 浏览器搜索")
            results = self._search_playwright(query, max_results)
            if results:
                return results
        except Exception as e:
            logger.error(f"Playwright 搜索也失败: {e}")

        return results

    def _search_serper(
        self, query: str, max_results: int
    ) -> List[SearchResult]:
        """
        通过 Serper.dev API 搜索（返回高质量 Google 结果）
        免费额度 2500 次/月，无需代理，结果精准。
        """
        if not self.serper_key:
            return []  # 未配置 Key 则跳过
        r = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": self.serper_key,
                "Content-Type": "application/json",
            },
            json={"q": query, "num": max_results},
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        results = []
        for item in data.get("organic", [])[:max_results]:
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("link", ""),
                    snippet=item.get("snippet", ""),
                    source="serper",
                )
            )
        return results

    def search_places(
        self, query: str, max_results: int = 20
    ) -> List[dict]:
        """
        调用 Serper 的 Google Maps 商户接口。
        直接返回店铺名称、地址、电话、经纬度，适合本地实体店调研。
        """
        if not self.serper_key:
            return []
        try:
            r = requests.post(
                "https://google.serper.dev/places",
                headers={
                    "X-API-KEY": self.serper_key,
                    "Content-Type": "application/json",
                },
                json={"q": query, "num": max_results},
                timeout=30,
            )
            r.raise_for_status()
            return r.json().get("places", [])[:max_results]
        except Exception as e:
            logger.warning(f"地图商户搜索失败 [{query}]: {e}")
            return []

    def _search_duckduckgo(
        self, query: str, max_results: int
    ) -> List[SearchResult]:
        """DuckDuckGo HTML 版搜索"""
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {"User-Agent": self.USER_AGENTS[0]}
        r = self.session.get(url, headers=headers, timeout=15)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "lxml")
        results = []
        # DuckDuckGo HTML 结果选择器
        for item in soup.select("div.result")[:max_results]:
            link = item.select_one("a.result__a")
            snippet = item.select_one("a.result__snippet") or item.select_one(
                ".result-snippet"
            )
            if not link or not link.get("href"):
                continue
            raw_url = link["href"]
            # DuckDuckGo 有时会用跳转链接，需要解析
            real_url = self._extract_ddg_url(raw_url)
            if not real_url:
                continue
            title = link.get_text(strip=True)
            snippet_text = (
                snippet.get_text(strip=True) if snippet else ""
            )
            results.append(
                SearchResult(
                    title=title,
                    url=real_url,
                    snippet=snippet_text,
                    source="duckduckgo",
                )
            )
        return results

    @staticmethod
    def _extract_ddg_url(raw: str) -> Optional[str]:
        """从 DuckDuckGo 的跳转链接中提取真实 URL"""
        if raw.startswith("//duckduckgo.com/l/") or raw.startswith(
            "https://duckduckgo.com/l/"
        ):
            parsed = urlparse(raw if raw.startswith("http") else "https:" + raw)
            qs = parse_qs(parsed.query)
            if "uddg" in qs:
                return unquote(qs["uddg"][0])
        if raw.startswith("http"):
            return raw
        return None

    def _search_bing(self, query: str, max_results: int) -> List[SearchResult]:
        """Bing 搜索"""
        # 强制英文+美国地区，避免返回无关地区结果
        url = (
            f"https://www.bing.com/search?q={quote_plus(query)}"
            "&setlang=en-US&cc=US&mkt=en-US"
        )
        headers = {
            "User-Agent": self.USER_AGENTS[1],
            "Accept-Language": "en-US,en;q=0.9",
            "Cookie": "_EDGE_S=mkt=en-us; SRCHHPGUSR=SRCHLANG=en",
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/webp,*/*;q=0.8"
            ),
        }
        r = self.session.get(url, headers=headers, timeout=15)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "lxml")
        results = []
        # Bing 结果选择器
        for item in soup.select("li.b_algo")[:max_results]:
            link = item.select_one("h2 a")
            snippet = item.select_one(".b_caption p") or item.select_one(
                "div.b_caption"
            )
            if not link or not link.get("href"):
                continue
            # 解码 Bing 跳转链接
            real_url = self._decode_bing_url(link["href"])
            title = link.get_text(strip=True)
            snippet_text = (
                snippet.get_text(strip=True) if snippet else ""
            )
            results.append(
                SearchResult(
                    title=title,
                    url=real_url or link["href"],
                    snippet=snippet_text,
                    source="bing",
                )
            )
        return results

    @staticmethod
    def _decode_bing_url(raw: str) -> Optional[str]:
        """解码 Bing 的 /ck/a 跳转链接，提取真实 URL"""
        if "bing.com/ck/a" not in raw:
            return raw
        try:
            parsed = urlparse(raw)
            qs = parse_qs(parsed.query)
            u = qs.get("u", [None])[0]
            if u:
                # u 参数是 base64，去掉前缀 a1
                if u.startswith("a1"):
                    u = u[2:]
                # 补齐 base64 padding
                padding = "=" * (-len(u) % 4)
                decoded = base64.urlsafe_b64decode(u + padding).decode(
                    "utf-8", errors="ignore"
                )
                if decoded.startswith("http"):
                    return decoded
        except Exception:
            pass
        # 兜底：尝试 u 参数直接是 URL 的情况
        try:
            parsed = urlparse(raw)
            qs = parse_qs(parsed.query)
            u = qs.get("u", [None])[0]
            if u and u.startswith("http"):
                return u
        except Exception:
            pass
        return None

    def _search_playwright(
        self, query: str, max_results: int
    ) -> List[SearchResult]:
        """使用 Playwright 无头浏览器搜索（反爬兜底方案）"""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning("Playwright 未安装，跳过此方案")
            return []

        results = []
        with sync_playwright() as p:
            launch_args = {"headless": True}
            if self.proxy:
                launch_args["proxy"] = {"server": self.proxy}
            browser = p.chromium.launch(**launch_args)
            context = browser.new_context(user_agent=self.USER_AGENTS[0])
            page = context.new_page()
            try:
                page.goto(
                    f"https://html.duckduckgo.com/html/?q={quote_plus(query)}",
                    timeout=30000,
                )
                page.wait_for_selector("div.result", timeout=10000)
                items = page.query_selector_all("div.result")[:max_results]
                for item in items:
                    link_el = item.query_selector("a.result__a")
                    snippet_el = item.query_selector("a.result__snippet")
                    if not link_el:
                        continue
                    href = link_el.get_attribute("href") or ""
                    real_url = self._extract_ddg_url(href) or href
                    title = link_el.inner_text()
                    snippet = (
                        snippet_el.inner_text() if snippet_el else ""
                    )
                    results.append(
                        SearchResult(
                            title=title,
                            url=real_url,
                            snippet=snippet,
                            source="duckduckgo-playwright",
                        )
                    )
            finally:
                browser.close()
        return results

    def fetch_page(self, url: str, timeout: int = 15) -> Optional[str]:
        """
        抓取页面 HTML 内容
        :param url: 目标 URL
        :param timeout: 超时时间
        :return: HTML 字符串或 None
        """
        try:
            headers = {"User-Agent": self.USER_AGENTS[2]}
            r = self.session.get(url, headers=headers, timeout=timeout)
            r.raise_for_status()
            return r.text
        except Exception as e:
            logger.warning(f"抓取页面失败 {url}: {e}")
            return None

    def search_multi_queries(
        self, queries: List[str], max_results_per_query: int = 15
    ) -> List[SearchResult]:
        """
        多关键词搜索，合并去重
        :param queries: 关键词列表
        :param max_results_per_query: 每个关键词的最大结果数
        :return: 合并去重后的结果
        """
        all_results: List[SearchResult] = []
        seen_urls = set()
        for q in queries:
            results = self.search(q, max_results_per_query)
            for r in results:
                if r.url not in seen_urls:
                    seen_urls.add(r.url)
                    all_results.append(r)
            time.sleep(1)  # 避免频率限制
        return all_results

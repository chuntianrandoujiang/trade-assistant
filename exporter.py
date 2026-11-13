"""
导出模块 - 把店铺列表导出为 Excel / PDF 文件

Excel：openpyxl 生成，中文表头，电话带国际码
PDF：reportlab + 黑体（SimHei）保证中文正常显示
文件同时保存到 results/ 目录，并返回字节内容供网页下载
"""

import io
from datetime import datetime
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from phone_utils import format_phone
from cities import COUNTRIES, get_cities

import os

# 导出列：(Shop 字段名, 中文列名, 英文列名)
EXPORT_COLUMNS = [
    ("country", "国家", "Country"),
    ("city", "城市", "City"),
    ("product", "产品名称", "Product"),
    ("name", "商家名称", "Shop Name"),
    ("phone", "电话", "Phone"),
    ("email", "邮箱", "Email"),
    ("address", "地址", "Address"),
    ("contact_person", "联系人", "Contact"),
    ("website", "网站", "Website"),
    ("source", "数据来源", "Source"),
]

# 数据来源英文码 → 可读名称（中英）
SOURCE_NAMES = {
    "google_maps": {"zh": "谷歌地图", "en": "Google Maps"},
    "serper": {"zh": "Google 搜索", "en": "Google Search"},
    "duckduckgo": {"zh": "DuckDuckGo", "en": "DuckDuckGo"},
    "duckduckgo-playwright": {"zh": "DuckDuckGo", "en": "DuckDuckGo"},
    "bing": {"zh": "必应搜索", "en": "Bing Search"},
    "osm": {"zh": "OpenStreetMap", "en": "OpenStreetMap"},
    "overpass": {"zh": "OpenStreetMap", "en": "OpenStreetMap"},
}

# 文案（中英）
_EXPORT_TEXT = {
    "sheet": {"zh": "店铺列表", "en": "Shop List"},
    "pdf_title": {"zh": "外贸市场店铺清单", "en": "Overseas Market Shop List"},
    "pdf_doc_title": {"zh": "外贸市场店铺导出", "en": "Overseas Market Shop Export"},
    "all_country": {"zh": "全国", "en": "All"},
    "all_city": {"zh": "全部", "en": "All"},
    "filter": {"zh": "筛选", "en": "Filter"},
    "total_suffix": {"zh": "家", "en": "shops"},
    "export_time": {"zh": "导出时间", "en": "Exported"},
    "file_prefix": {"zh": "店铺", "en": "shops"},
    "filter_all": {"zh": "全部", "en": "All"},
    "filter_phone": {"zh": "有电话", "en": "With Phone"},
    "filter_email": {"zh": "有邮箱", "en": "With Email"},
    "filter_addr": {"zh": "有地址", "en": "With Address"},
}


def _tx(key, lang):
    """取文案"""
    return _EXPORT_TEXT.get(key, {}).get(lang, _EXPORT_TEXT.get(key, {}).get("zh", ""))


def _filter_tag_lang(tag, lang):
    """把内部中文筛选标签转成目标语言（导出文件里显示）"""
    mapping = {
        "全部": "filter_all",
        "有电话": "filter_phone",
        "有邮箱": "filter_email",
        "有地址": "filter_addr",
    }
    key = mapping.get(tag)
    return _tx(key, lang) if key else tag


def _country_display(country_zh, lang):
    """按语言返回国家名"""
    if lang != "en":
        return country_zh
    return COUNTRIES.get(country_zh, {}).get("en", country_zh)


def _city_display(city_zh, country_zh, lang):
    """按语言返回城市名"""
    if lang != "en" or not city_zh:
        return city_zh
    for czh, cen in get_cities(country_zh):
        if czh == city_zh:
            return cen
    return city_zh


def _source_label(value, lang="zh"):
    """把数据来源英文码转成可读名称，未知值原样返回"""
    key = str(value or "").strip().lower()
    entry = SOURCE_NAMES.get(key)
    if entry is None:
        return str(value or "")
    return entry.get(lang, entry.get("zh", ""))

def _rows_from_shops(shops, lang="zh", country_zh=None):
    """把店铺列表转成导出行（电话自动加国际码；英文模式下国家/城市转英文）"""
    rows = []
    for s in shops:
        d = s.to_dict()
        d["phone"] = format_phone(d.get("phone", ""), d.get("country", ""))
        d["source"] = _source_label(d.get("source", ""), lang)
        if lang == "en":
            d["country"] = _country_display(d.get("country", ""), lang)
            d["city"] = _city_display(d.get("city", ""), country_zh or d.get("country", ""), lang)
        rows.append(d)
    return rows


def build_excel(shops, lang="zh", country_zh=None) -> bytes:
    """生成 Excel(.xlsx) 文件内容"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment

    rows = _rows_from_shops(shops, lang, country_zh)
    wb = Workbook()
    ws = wb.active
    ws.title = _tx("sheet", lang)

    # 表头样式
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="667EEA")
    ws.append([label[1] if lang == "zh" else label[2] for label in EXPORT_COLUMNS])
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # 数据行
    for r in rows:
        ws.append([r.get(key, "") for key, _, _ in EXPORT_COLUMNS])

    # 列宽与冻结首行
    widths = [10, 12, 14, 32, 18, 32, 42, 14, 32, 12]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + i)].width = w
    ws.freeze_panes = "A2"

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _query_text(query, key, default=""):
    """兼容 query 为字典或字符串两种传入方式"""
    if isinstance(query, dict):
        return str(query.get(key, default) or default)
    return str(query or "")


# 导出时要求同时正确显示的字符：中文 + 西里尔/拉丁变音（德 äöü、法 çé、西 ñ）
# SimHei 缺这些变音字符，会渲染成方块 □
_FONT_TEST_CHARS = "中文äöüÄÖÜßçéñ"

# 候选字体（按优先级）。全部用 ttc/ttf，缺失或注册失败则自动跳过
# 按优先级排列，跨 Windows / Linux 双平台。
# Linux（如 ModelScope DSW）没有 C:\Windows\Fonts，需要列出常见中文字体位置。
_FONT_CANDIDATES = [
    # Windows
    ("DengXian", r"C:\Windows\Fonts\Deng.ttf"),
    ("SimSun", r"C:\Windows\Fonts\simsun.ttc"),
    ("NSimSun", r"C:\Windows\Fonts\NSimSun.ttf"),
    ("SimHei", r"C:\Windows\Fonts\simhei.ttf"),
    # Linux 常见位置（ModelScope DSW / Docker 基础镜像）
    ("NotoSansCJK", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
    ("NotoSansCJKsc", "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf"),
    ("NotoSansSC", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    ("WenQuanYiMicro", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
    ("WenQuanYiZen", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
    ("DroidSansFallback", "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"),
    ("SourceHanSans", "/usr/share/fonts/source-han-sans/SourceHanSansSC-Regular.otf"),
    # 容器内常被安装到项目目录的字体
    ("LocalNoto", str(Path(__file__).parent / "fonts" / "NotoSansCJK-Regular.ttc")),
    ("LocalWQY", str(Path(__file__).parent / "fonts" / "wqy-microhei.ttc")),
]


def _scan_font_dirs():
    """
    扫描系统字体目录，把带 CJK 覆盖的 ttf/ttc/otf 追加进候选列表。

    DSW 等镜像的字体路径不固定，扫描比写死更稳。
    """
    dirs = [
        "/usr/share/fonts",
        "/usr/local/share/fonts",
        str(Path.home() / ".fonts"),
        r"C:\Windows\Fonts",
    ]
    found = []
    for d in dirs:
        root = Path(d)
        if not root.exists():
            continue
        for f in root.rglob("*"):
            if f.suffix.lower() in (".ttf", ".ttc", ".otf"):
                # 文件名做报告字体名：去掉扩展名，压缩空格，限长
                tag = "".join(ch for ch in f.stem if not ch.isspace())[:24]
                found.append((tag, str(f)))
    return found


def _get_scanned_fonts():
    """
    返回扫描到的系统字体候选（字体名, 路径）。

    结果按目录做稳定性排序，保证同一环境下每次选中的字体一致。
    """
    try:
        raw = sorted(_scan_font_dirs(), key=lambda x: x[1])
        # 同名（stem 相同）只保留最先命中的，避免 reportlab 重复注册同名字体报错
        out, used = [], set()
        for name, path in raw:
            if name in used:
                continue
            used.add(name)
            out.append((name, path))
        return out
    except Exception:
        return []


def _font_covers_chars(font_name):
    """检查已注册字体是否完整覆盖 _FONT_TEST_CHARS"""
    try:
        face = pdfmetrics.getFont(font_name).face
        for ch in _FONT_TEST_CHARS:
            if not face.charToGlyph.get(ord(ch), 0):
                return False
        return True
    except Exception:
        return False


def _pick_cjk_font():
    """
    挑选对「中文 + 拉丁变音字符」完整覆盖的中文字体。

    优先选变音字符不缺失的字体（DengXian / SimSun），
    避免因 SimHei 缺 ä/ö/ß 等字符而在 PDF 里显示成方块 □。
    """
    fallback = None
    candidates = list(_FONT_CANDIDATES)
    candidates.extend(_get_scanned_fonts())
    seen = set()
    for name, path in candidates:
        if (name, path) in seen:
            continue
        seen.add((name, path))
        if not os.path.exists(path):
            continue
        try:
            pdfmetrics.registerFont(TTFont(name, path))
        except Exception:
            continue
        if _font_covers_chars(name):
            return name
        if fallback is None:
            fallback = name
    return fallback or "Helvetica"
def build_pdf(shops, query, filter_tag, lang="zh", country_zh=None) -> bytes:
    """生成 PDF 文件内容（横版 A4，含标题与店铺表格）"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
    from reportlab.lib.styles import ParagraphStyle

    # 注册黑体，保证中文显示
    font_name = _pick_cjk_font()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=14 * mm,
        bottomMargin=14 * mm,
        title=_tx("pdf_doc_title", lang),
    )

    title_style = ParagraphStyle(
        "title", fontName=font_name, fontSize=16, alignment=1, spaceAfter=4
    )
    meta_style = ParagraphStyle(
        "meta",
        fontName=font_name,
        fontSize=10,
        alignment=1,
        textColor=colors.grey,
        spaceAfter=8,
    )
    cell_style = ParagraphStyle(
        "cell", fontName=font_name, fontSize=8.5, leading=12
    )

    elements = [
        Paragraph(_tx("pdf_title", lang), title_style),
        Paragraph(
            f"{_country_display(_query_text(query, 'country', _tx('all_country', lang)), lang)} · "
            f"{_city_display(_query_text(query, 'city', _tx('all_city', lang)), _query_text(query, 'country', ''), lang)} · "
            f"{_query_text(query, 'product')} · "
            f"{_tx('filter', lang)}: {filter_tag} · {len(shops)} {_tx('total_suffix', lang)} · "
            f"{_tx('export_time', lang)} {datetime.now():%Y-%m-%d %H:%M}",
            meta_style,
        ),
    ]

    data = [[Paragraph(label[1] if lang == "zh" else label[2], cell_style) for label in EXPORT_COLUMNS]]
    for r in _rows_from_shops(shops, lang, country_zh):
        data.append(
            [
                Paragraph(str(r.get(key, "") or ""), cell_style)
                for key, _, _ in EXPORT_COLUMNS
            ]
        )

    # 合计 273mm，正好等于 A4 横向可用宽度（297 - 12 - 12）
    col_widths = [
        15 * mm, 20 * mm, 24 * mm, 40 * mm, 24 * mm,
        42 * mm, 38 * mm, 18 * mm, 35 * mm, 17 * mm,
    ]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#667EEA")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#F2F4FB")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)

    doc.build(elements)
    return buf.getvalue()


def export_file(shops, query, filter_tag, fmt, target_dir=None, lang="zh"):
    """
    统一导出入口
    :param shops: 店铺列表（已按筛选过滤）
    :param query: 搜索条件 {country, product, city}
    :param filter_tag: 当前筛选标签（全部/有电话/有邮箱/有地址）
    :param fmt: "excel" 或 "pdf"
    :param target_dir: 保存文件夹（用户指定路径，默认项目下 results/）
    :return: (文件路径, 文件字节, 建议文件名)
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filter_tag = _filter_tag_lang(filter_tag, lang)
    tag = "" if filter_tag == _tx("filter_all", lang) else f"_{filter_tag}"
    country_disp = _country_display(_query_text(query, 'country', _tx('all_country', lang)), lang)
    base = f"{_tx('file_prefix', lang)}_{country_disp}{tag}_" \
           f"{_query_text(query, 'product')}_{ts}"

    _country_zh = _query_text(query, "country", "")
    if fmt == "excel":
        data = build_excel(shops, lang, _country_zh)
        ext = ".xlsx"
    else:
        data = build_pdf(shops, query, filter_tag, lang, _country_zh)
        ext = ".pdf"

    if target_dir:
        out_dir = Path(target_dir).expanduser()
    else:
        out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / (base + ext)
    path.write_bytes(data)
    return path, data, base + ext

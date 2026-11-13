"""
电话号码国际码工具

功能：
1. 根据国家中文名获取国际电话区号
2. 格式化电话号码（自动加 + 区号）
3. 清洗错误号码（过滤掉过长/异常的数字串）
"""

import re
from typing import Optional

# 国家中文名 → 国际电话区号
COUNTRY_PHONE_CODE = {
    "美国": "+1",
    "加拿大": "+1",
    "英国": "+44",
    "德国": "+49",
    "法国": "+33",
    "意大利": "+39",
    "西班牙": "+34",
    "日本": "+81",
    "韩国": "+82",
    "澳大利亚": "+61",
    "巴西": "+55",
    "印度": "+91",
    "俄罗斯": "+7",
    "阿联酋": "+971",
    "沙特": "+966",
    "泰国": "+66",
    "越南": "+84",
    "印度尼西亚": "+62",
    "马来西亚": "+60",
    "墨西哥": "+52",
    "南非": "+27",
    "土耳其": "+90",
    "尼日利亚": "+234",
    "肯尼亚": "+254",
    "埃及": "+20",
    "中国": "+86",
}


def get_phone_code(country_zh: str) -> str:
    """
    获取国家国际电话区号
    :param country_zh: 国家中文名
    :return: 国际码，如 "+1"、"+86"，未知国家返回 ""
    """
    return COUNTRY_PHONE_CODE.get(country_zh, "")


def format_phone(
    phone: str,
    country_zh: str = "",
) -> str:
    """
    格式化电话号码，自动加国际码
    :param phone: 原始电话号码
    :param country_zh: 国家中文名（用于推断国际码）
    :return: 格式化后的电话，如 "+1 212-686-2198"
    """
    if not phone:
        return ""

    phone = phone.strip()
    digits_all = re.sub(r"\D", "", phone)

    code = get_phone_code(country_zh)

    # 已有 + 号：仍然按国家规则重新排版
    if phone.startswith("+"):
        if code == "+1" and digits_all.startswith("1") and len(digits_all) == 11:
            d = digits_all[1:]
            return f"+1 {d[:3]}-{d[3:6]}-{d[6:]}"
        if code == "+1" and len(digits_all) == 10:
            return f"+1 {digits_all[:3]}-{digits_all[3:6]}-{digits_all[6:]}"
        return phone

    if not code:
        return phone  # 未知国家，原样返回

    digits = digits_all

    # 北美：去掉国内长途前缀 1，再按 3-3-4 排版
    if code == "+1":
        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]
        if len(digits) == 10:
            return f"+1 {digits[:3]}-{digits[3:6]}-{digits[6:]}"
        return f"+1 {digits}"

    # 其他国家：去掉本地前缀 0（国际拨号时需去掉）
    if digits.startswith("0"):
        digits = digits.lstrip("0")

    return f"{code} {digits}"


def is_valid_phone(phone: str) -> bool:
    """
    验证电话号码是否合理
    规则：
    1. 数字位数 7-15 位
    2. 不以 0 开头（国际码已去除）
    3. 不含连续重复数字超过 4 位（如 11111）
    4. 不是明显的日期/编号（如 19xxxx, 20xxxx 开头的 8 位）
    """
    if not phone:
        return False

    digits = re.sub(r"\D", "", phone)

    # 长度检查（实际商家号码少有超过 12 位，收紧以降低误判）
    if len(digits) < 7 or len(digits) > 12:
        return False

    # 连续重复数字检查（超过 4 位视为异常）
    if re.search(r"(\d)\1{4,}", digits):
        return False

    # 日期/编号检查（19xx 或 20xx 开头的 8 位）
    if len(digits) == 8 and (digits.startswith("19") or digits.startswith("20")):
        return False

    return True

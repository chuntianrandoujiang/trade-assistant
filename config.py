"""
配置模块 - 管理本地配置（如 API Key）

Serper API Key 仅保存在本地 config.json，不外传。
"""

import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

_DEFAULT = {
    "serper_api_key": "",
}


def load_config() -> dict:
    """加载配置，文件不存在则返回默认"""
    if CONFIG_PATH.exists():
        try:
            return {**_DEFAULT, **json.loads(CONFIG_PATH.read_text("utf-8"))}
        except Exception:
            return dict(_DEFAULT)
    return dict(_DEFAULT)


def save_config(cfg: dict):
    """保存配置到本地"""
    CONFIG_PATH.write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), "utf-8"
    )


def get_serper_key() -> str:
    """获取 Serper API Key（优先环境变量，其次配置文件）"""
    return os.environ.get("SERPER_API_KEY") or load_config().get(
        "serper_api_key", ""
    )


def set_serper_key(key: str):
    """保存 Serper API Key"""
    cfg = load_config()
    cfg["serper_api_key"] = key.strip()
    save_config(cfg)

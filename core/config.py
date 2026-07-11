"""AutoSoc 配置管理 — 基于 pydantic-settings 从 .env / 环境变量加载。"""

from pathlib import Path
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """全局配置，支持 .env 文件覆盖。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AUTOSOC_",
    )

    # ── 数据库 ──────────────────────────────────────────
    db_path: str = "data/autosoc.db"

    # ── AI Provider ────────────────────────────────────
    ai_provider: Literal["mock", "openai", "ollama"] = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"

    # ── 存储 ────────────────────────────────────────────
    storage_root: str = "storage"

    # ── 浏览器自动化 ──────────────────────────────────
    playwright_headless: bool = True
    playwright_slow_mo: int = 200  # 毫秒

    # ── 日志 ────────────────────────────────────────────
    log_level: str = "INFO"
    log_file: str = "data/autosoc.log"

    # ── 系统演进阶段 ──────────────────────────────────
    system_phase: Literal["manual", "cooperative", "autonomous"] = "manual"

    # ── 账号配置 ──────────────────────────────────────
    accounts_config_path: str = "data/accounts.json"


settings = Settings()


def get_data_dir() -> Path:
    """返回数据目录绝对路径。"""
    return Path(settings.db_path).parent.resolve()


def get_storage_root() -> Path:
    """返回存储根目录绝对路径。"""
    return Path(settings.storage_root).resolve()

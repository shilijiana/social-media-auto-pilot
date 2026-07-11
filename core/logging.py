"""日志配置 — 基于 loguru，终端 + 文件双输出。"""

import sys
from pathlib import Path

from loguru import logger

from autosoc.core.config import settings


def setup_logging():
    """配置 loguru 日志（终端 + 文件），应在应用启动时调用一次。"""
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger.remove()  # 移除默认 handler

    # 终端输出（彩色）
    logger.add(
        sys.stderr,
        level=settings.log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <7}</level> | <cyan>{name}</cyan> | {message}",
        colorize=True,
    )

    # 文件输出（结构化）
    logger.add(
        str(log_file),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <7} | {name}:{function}:{line} | {message}",
        rotation="10 MB",
        retention="30 days",
        compression="gz",
    )

    return logger


# 全局日志实例
log = logger

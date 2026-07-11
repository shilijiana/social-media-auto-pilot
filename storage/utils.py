"""存储路径工具 — 素材/内容/截图的路径生成与哈希命名。"""

import hashlib
from pathlib import Path
from typing import Optional


def hash_filename(data: bytes, ext: str = "") -> str:
    """基于内容生成哈希文件名。"""
    h = hashlib.sha256(data).hexdigest()[:16]
    return f"{h}{ext}"


def material_path(
    topic_id: int,
    material_type: str,
    filename: str,
    root: Optional[str] = None,
) -> str:
    """生成素材存储路径: materials/{topic_id}/{type}/{filename}"""
    return f"materials/{topic_id}/{material_type}/{filename}"


def content_output_path(
    content_id: int,
    version: int,
    filename: str,
    root: Optional[str] = None,
) -> str:
    """生成内容产出路径: outputs/{content_id}/v{version}/{filename}"""
    return f"outputs/{content_id}/v{version}/{filename}"


def screenshot_path(
    publication_id: int,
    timestamp: str,
) -> str:
    """生成发布截图路径: screenshots/{publication_id}/{timestamp}.png"""
    safe_ts = timestamp.replace(":", "-").replace(" ", "_")
    return f"screenshots/{publication_id}/{safe_ts}.png"

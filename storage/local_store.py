"""本地文件系统存储实现。"""

import os
import shutil
from pathlib import Path
from typing import Optional

from autosoc.storage.interfaces import AbstractFileStore


class LocalFileStore(AbstractFileStore):
    """基于本地文件系统的存储实现。

    建议目录结构:
        storage/materials/{topic_id}/{material_type}/{hash}.{ext}
        storage/outputs/{content_id}/{version}/
    """

    def __init__(self, root_path: str = "storage"):
        self.root = Path(root_path).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, relative_path: str) -> Path:
        """解析相对路径为绝对路径，防止目录遍历攻击。"""
        path = self.root.joinpath(relative_path).resolve()
        if not str(path).startswith(str(self.root)):
            raise ValueError(f"路径越界: {relative_path}")
        return path

    def write(self, relative_path: str, data: bytes) -> str:
        path = self._resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    def read(self, relative_path: str) -> Optional[bytes]:
        path = self._resolve(relative_path)
        if not path.exists():
            return None
        return path.read_bytes()

    def delete(self, relative_path: str) -> bool:
        path = self._resolve(relative_path)
        if not path.exists():
            return False
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
        return True

    def exists(self, relative_path: str) -> bool:
        return self._resolve(relative_path).exists()

    def list_files(self, directory: str) -> list[str]:
        dir_path = self._resolve(directory)
        if not dir_path.exists():
            return []
        return [
            str(p.relative_to(self.root))
            for p in dir_path.rglob("*")
            if p.is_file()
        ]

    def get_absolute_path(self, relative_path: str) -> str:
        return str(self._resolve(relative_path))

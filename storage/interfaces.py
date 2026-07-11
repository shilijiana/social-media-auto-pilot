"""文件存储抽象层定义。"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional


class AbstractFileStore(ABC):
    """文件存储抽象 — 封装文件读写操作，支持本地/对象存储切换。"""

    @abstractmethod
    def write(self, relative_path: str, data: bytes) -> str:
        """写入文件，返回完整存储路径。"""
        ...

    @abstractmethod
    def read(self, relative_path: str) -> Optional[bytes]:
        """读取文件，不存在时返回 None。"""
        ...

    @abstractmethod
    def delete(self, relative_path: str) -> bool:
        """删除文件。"""
        ...

    @abstractmethod
    def exists(self, relative_path: str) -> bool:
        """判断文件是否存在。"""
        ...

    @abstractmethod
    def list_files(self, directory: str) -> list[str]:
        """列出目录下的所有文件相对路径。"""
        ...

    @abstractmethod
    def get_absolute_path(self, relative_path: str) -> str:
        """获取文件的绝对路径（本地文件系统适用）。"""
        ...

    def open(self, relative_path: str, mode: str = "rb") -> BinaryIO:
        """打开文件流。"""
        raise NotImplementedError

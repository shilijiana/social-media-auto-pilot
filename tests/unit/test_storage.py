"""存储层测试。"""

import tempfile
from pathlib import Path

import pytest


class TestLocalFileStore:
    def test_write_and_read(self):
        from autosoc.storage.local_store import LocalFileStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalFileStore(tmpdir)
            path = store.write("test/hello.txt", b"Hello, World!")

            assert store.exists("test/hello.txt")
            data = store.read("test/hello.txt")
            assert data == b"Hello, World!"

    def test_delete(self):
        from autosoc.storage.local_store import LocalFileStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalFileStore(tmpdir)
            store.write("test/tmp.txt", b"delete me")
            assert store.exists("test/tmp.txt")

            result = store.delete("test/tmp.txt")
            assert result is True
            assert not store.exists("test/tmp.txt")

    def test_list_files(self):
        from autosoc.storage.local_store import LocalFileStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalFileStore(tmpdir)
            store.write("a.txt", b"a")
            store.write("sub/b.txt", b"b")
            store.write("sub/sub2/c.txt", b"c")

            files = store.list_files(".")
            assert len(files) == 3
            assert "a.txt" in files
            assert "sub/b.txt" in files

    def test_path_traversal_prevention(self):
        from autosoc.storage.local_store import LocalFileStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = LocalFileStore(tmpdir)
            with pytest.raises(ValueError, match="路径越界"):
                store.read("../etc/passwd")

    def test_storage_utils(self):
        from autosoc.storage.utils import hash_filename, material_path, content_output_path

        h = hash_filename(b"hello", ".png")
        assert h.endswith(".png")
        assert len(h) > 16

        mp = material_path(1, "image", "test.png")
        assert mp == "materials/1/image/test.png"

        cp = content_output_path(42, 2, "final.mp4")
        assert cp == "outputs/42/v2/final.mp4"

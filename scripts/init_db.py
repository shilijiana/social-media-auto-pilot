"""数据库初始化脚本 — 创建数据库和表结构。"""

import sys
from pathlib import Path


def find_project_root() -> Path:
    """从脚本位置向上查找项目根目录（包含 pyproject.toml）。"""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parent


def init_db(schema_path: str = None, db_path: str = None):
    """初始化数据库。"""
    project_root = find_project_root()

    # 切换到项目根目录，避免 editable install 与 cwd 的包名冲突
    import os
    os.chdir(project_root)

    # 现在可以安全导入 autosoc 了
    sys.path.insert(0, str(project_root))

    from autosoc.core.config import settings
    from autosoc.core.database import Database

    actual_db_path = db_path or settings.db_path

    # 确保 db_path 是绝对路径或相对于项目根
    db_file = Path(actual_db_path)
    if not db_file.is_absolute():
        db_file = project_root / actual_db_path

    db = Database(str(db_file))

    # 确定 schema 文件路径
    if schema_path:
        schema_file = Path(schema_path)
    else:
        schema_file = project_root / "data" / "schema.sql"

    if not schema_file.exists():
        print(f"错误: Schema 文件未找到: {schema_file}")
        sys.exit(1)

    db.initialize_schema(str(schema_file))
    print(f"✓ 数据库已初始化: {db_file}")
    print(f"  Schema: {schema_file}")
    print(f"  表数: {len(db.fetchall(\"SELECT name FROM sqlite_master WHERE type='table'\"))}")


if __name__ == "__main__":
    init_db()

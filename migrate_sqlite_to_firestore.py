"""migrate_sqlite_to_firestore.py

一次性脚本：将 `pedagogical_ai.db` 中的所有表完整迁移到 Firebase Firestore。

使用方法：
1. 确保已经在 Google Cloud 上创建了 Firestore 数据库，并下载服务账号 json。
2. 设置环境变量 `GOOGLE_APPLICATION_CREDENTIALS` 指向该 json 文件。
3. `pip install google-cloud-firestore tabulate`（tabulate 可选，只用于打印）
4. 运行：
    python migrate_sqlite_to_firestore.py

脚本会：
    • 遍历 SQLite 中的所有表；
    • 逐行读取记录，转换为字典；
    • 将每张表写入同名 collection；
    • 若行内存在 `id`/`pk`/`primary_key`/`uid` 字段，则用作文档 id；
      否则自动生成文档 id 并把原行号附加到字典。 

提示：此脚本只是通用示例，若要定义更合理的嵌套结构（如把某些表迁为子集合），
      请按项目业务需要修改 `_CUSTOM_COLLECTION_MAPPING` 部分。
"""
from __future__ import annotations

import os
import sqlite3
from typing import Any, Dict
from pathlib import Path

from google.cloud import firestore  # type: ignore
from tabulate import tabulate  # 手动安装，可删除相关使用

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
SQLITE_DB_PATH = Path(__file__).parent / "pedagogical_ai.db"

# 指定需要跳过的临时／系统表
_SKIP_TABLES = {"sqlite_sequence"}

# 针对项目需求可把某些表映射到子集合
#   e.g. {"step3_errors": "users/{user_id}/step3_errors"}
_CUSTOM_COLLECTION_MAPPING: dict[str, str] = {}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def discover_tables(cursor: sqlite3.Cursor) -> list[str]:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if row[0] not in _SKIP_TABLES]
    return tables


def row_to_dict(cursor: sqlite3.Cursor, row: tuple[Any, ...]) -> Dict[str, Any]:
    """将 sqlite3 行元组转为列名→值的 dict。"""
    return {description[0]: value for description, value in zip(cursor.description, row)}


def choose_doc_id(record: Dict[str, Any]) -> str | None:
    for key in ("id", "uid", "pk", "primary_key", "user_id", "session_id"):
        if key in record and record[key] is not None:
            return str(record[key])
    return None


# ---------------------------------------------------------------------------
# Migration main
# ---------------------------------------------------------------------------

def migrate_database(sqlite_path: Path) -> None:
    if not sqlite_path.exists():
        raise FileNotFoundError(f"SQLite DB not found: {sqlite_path}")

    print(f"🔄 开始迁移 SQLite → Firestore: {sqlite_path}")

    # Init Firestore client (需先配置凭据)
    fs_client = firestore.Client()

    with sqlite3.connect(sqlite_path) as conn:
        conn.row_factory = sqlite3.Row  # 获取 dict 样式行
        cursor = conn.cursor()

        for table in discover_tables(cursor):
            print(f"\n📥 正在迁移表: {table}")
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            print(f"   → 共 {len(rows)} 行")

            # 解析自定义映射
            collection_template = _CUSTOM_COLLECTION_MAPPING.get(table, table)
            batch = fs_client.batch()
            operations = 0

            for row in rows:
                record: Dict[str, Any] = dict(row)
                # 处理 bytes -> str (Firestore 不支持 bytes)
                for k, v in list(record.items()):
                    if isinstance(v, bytes):
                        record[k] = v.decode("utf-8", "ignore")

                # 决定集合路径与 doc_id
                coll_path = collection_template
                if "{user_id}" in coll_path and "user_id" in record:
                    coll_path = coll_path.replace("{user_id}", str(record["user_id"]))

                doc_id = choose_doc_id(record)

                doc_ref = fs_client.collection(coll_path).document(doc_id) if doc_id else fs_client.collection(coll_path).document()
                batch.set(doc_ref, record, merge=True)
                operations += 1

                # Firestore 批处理限制 500
                if operations >= 450:
                    batch.commit()
                    batch = fs_client.batch()
                    operations = 0

            # 提交剩余操作
            if operations > 0:
                batch.commit()

            print("   ✔️  完成")

    print("\n✅ 全部迁移完成！")


if __name__ == "__main__":
    migrate_database(SQLITE_DB_PATH) 
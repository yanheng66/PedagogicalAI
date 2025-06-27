from __future__ import annotations

"""services.firestore_service
一个极简的 Firestore 访问层封装。
确保在运行前已经设置 GOOGLE_APPLICATION_CREDENTIALS 指向服务账号 json，
或者在初始化时传入凭据路径。
"""

from typing import Any, Optional
import os

# google-cloud-firestore 仅在运行时才需要，如本地未安装可先 `pip install google-cloud-firestore`。
try:
    from google.cloud import firestore  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "google-cloud-firestore 未安装，请先 `pip install google-cloud-firestore`"  # noqa: E501
    ) from exc


def _get_default_credentials_path() -> Optional[str]:
    """返回默认的 service account json 路径（通过环境变量或常用文件名推断）。"""
    env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path and os.path.exists(env_path):
        return env_path

    # 允许放在项目根目录并命名为 firebase_service_account.json
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    candidate = os.path.join(project_root, "firebase_service_account.json")
    return candidate if os.path.exists(candidate) else None


# 全局单例 client，避免重复创建
_client: Optional[firestore.Client] = None


def get_client() -> firestore.Client:
    """获取（或惰性创建）Firestore Client。"""
    global _client
    if _client is None:
        cred_path = _get_default_credentials_path()
        if cred_path:
            _client = firestore.Client.from_service_account_json(cred_path)
        else:
            # 如果环境变量已经配置，直接用默认凭据
            _client = firestore.Client()
    return _client


# ---------------------------------------------------------------------------
# CRUD helpers
# ---------------------------------------------------------------------------


def add_document(collection_path: str, data: dict[str, Any], doc_id: str | None = None) -> str:
    """向指定 collection 写入文档，返回文档 id。"""
    client = get_client()
    coll_ref = client.collection(collection_path)
    if doc_id is None:
        doc_ref = coll_ref.document()
    else:
        doc_ref = coll_ref.document(doc_id)
    doc_ref.set(data, merge=True)
    return doc_ref.id


def update_document(collection_path: str, doc_id: str, data: dict[str, Any]) -> None:
    client = get_client()
    client.collection(collection_path).document(doc_id).set(data, merge=True)


def get_document(collection_path: str, doc_id: str) -> Optional[dict[str, Any]]:
    client = get_client()
    snap = client.collection(collection_path).document(doc_id).get()
    return snap.to_dict() if snap.exists else None


def delete_document(collection_path: str, doc_id: str) -> None:
    client = get_client()
    client.collection(collection_path).document(doc_id).delete()


def list_collection(collection_path: str) -> list[dict[str, Any]]:
    client = get_client()
    coll_ref = client.collection(collection_path)
    return [doc.to_dict() | {"id": doc.id} for doc in coll_ref.stream()]


# ---------------------------------------------------------------------------
# Convenience helpers for本项目中的常用结构（users/…）
# ---------------------------------------------------------------------------


def get_user_doc(uid: str) -> Optional[dict[str, Any]]:
    return get_document("users", uid)


def upsert_user_doc(uid: str, data: dict[str, Any]) -> None:
    update_document("users", uid, data)


def get_user_progress(uid: str) -> Optional[dict[str, Any]]:
    client = get_client()
    doc_ref = client.collection("users").document(uid).collection("progress").document("main")
    snap = doc_ref.get()
    return snap.to_dict() if snap.exists else None


def upsert_user_progress(uid: str, data: dict[str, Any]) -> None:
    client = get_client()
    doc_ref = client.collection("users").document(uid).collection("progress").document("main")
    doc_ref.set(data, merge=True) 
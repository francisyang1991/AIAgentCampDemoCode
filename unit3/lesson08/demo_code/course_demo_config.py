"""课程所有 Demo 共用的云端 Embedding 配置。

优先读取仓库根目录的 VOYAGE_API_KEY.txt，使用 voyage-4-lite；若未配置
Voyage，仍兼容原来的 GLM_API_KEY.txt。任何新 Demo 都可以复用 embed()。
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Literal, Sequence

COURSE_ROOT = Path(__file__).resolve().parent

VOYAGE_KEY_FILE = COURSE_ROOT / "VOYAGE_API_KEY.txt"
VOYAGE_BASE_URL = os.environ.get("VOYAGE_BASE_URL", "https://api.voyageai.com/v1")
VOYAGE_EMBED_MODEL = os.environ.get("VOYAGE_EMBED_MODEL", "voyage-4-lite")
VOYAGE_EMBED_DIMENSIONS = int(os.environ.get("VOYAGE_EMBED_DIMENSIONS", "1024"))

GLM_KEY_FILE = COURSE_ROOT / "GLM_API_KEY.txt"
GLM_BASE_URL = os.environ.get("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
GLM_EMBED_MODEL = os.environ.get("GLM_EMBED_MODEL", "embedding-3")
GLM_EMBED_DIMENSIONS = int(os.environ.get("GLM_EMBED_DIMENSIONS", "1024"))

_glm_client = None


def _read_key(path: Path, environment_name: str) -> str:
    key = os.environ.get(environment_name, "").strip()
    if key:
        return key
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    return ""


def get_voyage_api_key() -> str:
    return _read_key(VOYAGE_KEY_FILE, "VOYAGE_API_KEY")


def get_glm_api_key() -> str:
    return _read_key(GLM_KEY_FILE, "ZHIPUAI_API_KEY")


def embedding_provider() -> str:
    """Return the configured shared cloud provider, in priority order."""
    if get_voyage_api_key():
        return "voyage"
    if get_glm_api_key():
        return "glm"
    return ""


def get_glm_client():
    """Compatibility helper for demos that explicitly need the GLM client."""
    global _glm_client
    key = get_glm_api_key()
    if not key:
        raise RuntimeError(f"请先把智谱 API Key 填入 {GLM_KEY_FILE}")
    if _glm_client is None:
        from openai import OpenAI

        _glm_client = OpenAI(api_key=key, base_url=GLM_BASE_URL)
    return _glm_client


def _embed_voyage(
    texts: list[str],
    model: str,
    dimensions: int,
    input_type: Literal["query", "document"] | None,
) -> list[list[float]]:
    payload: dict = {
        "model": model,
        "input": texts,
        "output_dimension": dimensions,
    }
    if input_type:
        payload["input_type"] = input_type
    request = urllib.request.Request(
        f"{VOYAGE_BASE_URL.rstrip('/')}/embeddings",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {get_voyage_api_key()}",
            "Content-Type": "application/json",
        },
    )
    data = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 429 and attempt < 3:
                # Voyage accounts without a payment method currently allow 3 RPM.
                # A short paced retry keeps consecutive classroom demos usable.
                print("[course_demo_config] Voyage 免费层达到 3 RPM，21 秒后自动重试…")
                time.sleep(21)
                continue
            try:
                detail = json.loads(body).get("detail", body)
            except Exception:
                detail = body
            raise RuntimeError(f"Voyage HTTP {exc.code}: {detail}") from None
    if data is None:
        raise RuntimeError("Voyage embedding 重试后仍未返回结果")
    ordered = sorted(data["data"], key=lambda item: item["index"])
    return [item["embedding"] for item in ordered]


def embed(
    texts: Sequence[str],
    *,
    input_type: Literal["query", "document"] | None = None,
    model: str | None = None,
    dimensions: int | None = None,
) -> list[list[float]]:
    """Convert texts to vectors using the repository-level shared provider."""
    items = list(texts)
    if not items:
        return []

    provider = embedding_provider()
    if provider == "voyage":
        return _embed_voyage(
            items,
            model or VOYAGE_EMBED_MODEL,
            dimensions or VOYAGE_EMBED_DIMENSIONS,
            input_type,
        )
    if provider == "glm":
        response = get_glm_client().embeddings.create(
            model=model or GLM_EMBED_MODEL,
            input=items,
            dimensions=dimensions or GLM_EMBED_DIMENSIONS,
        )
        ordered = sorted(response.data, key=lambda item: item.index)
        return [item.embedding for item in ordered]
    raise RuntimeError(f"请先把 Voyage API Key 填入 {VOYAGE_KEY_FILE}")


def embedding_backend_tag() -> str:
    """Stable tag so vectors from different providers/configurations never mix."""
    if embedding_provider() == "voyage":
        return f"voyage-{VOYAGE_EMBED_MODEL}-{VOYAGE_EMBED_DIMENSIONS}d"
    if embedding_provider() == "glm":
        return f"glm-{GLM_EMBED_MODEL}-{GLM_EMBED_DIMENSIONS}d"
    return "unconfigured"

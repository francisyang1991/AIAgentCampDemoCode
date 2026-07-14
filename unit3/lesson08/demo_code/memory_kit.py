"""
memory_kit · 本节公共工具（真 embedding + 向量库）
==================================================================
This is not a lecture file — it's the "foundation" that demos 01-05 all import.
It does two things, and both use REAL embeddings (no fake/hash vectors):

  1) embed(texts)        text -> real embedding vector. Backend picked once:
                           ① OPENAI_API_KEY set  -> OpenAI text-embedding-3-small
                           ② else Ollama alive    -> local nomic-embed-text (768d, offline, free)
                           ③ neither              -> friendly message, clean exit (no traceback)
  2) get_collection(...) a vector-store collection. chromadb PersistentClient if
                          installed; otherwise an equivalent local JSON store with
                          the SAME add/query interface.

Both stores use our embed() so store/query embeddings always match (a key pitfall
this lesson calls out). banner() prints one line telling you which backend is live.

课堂关键：离线也是真向量——本机 Ollama 跑 nomic-embed-text，召回质量和上课看到的一致。
"""

from __future__ import annotations

import json
import math
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Sequence

# ---------------------------------------------------------------------------
# 0) config: one embedding model name per backend + a shared dim record.
#    铁律：存和查必须用"同一个" embedding（本节易错点之一）。模型名集中在这里，谁都从这取。
# ---------------------------------------------------------------------------
OPENAI_EMBED_MODEL = "text-embedding-3-small"        # OpenAI 轻量 embedding
OLLAMA_EMBED_MODEL = os.environ.get("OLLAMA_EMBED_MODEL", "nomic-embed-text")  # 本地真 embedding
OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

# runtime record of which backend is actually in use (for banner + debugging)
BACKEND = {"embed": "?", "store": "?"}

_openai_client = None  # lazy import so missing `openai` doesn't crash on import


def _ollama_alive() -> bool:
    """Probe the local Ollama daemon (0.6s timeout so it never stalls a class)."""
    try:
        urllib.request.urlopen(OLLAMA_BASE + "/api/version", timeout=0.6)
        return True
    except Exception:
        return False


def _embed_ollama_one(text: str) -> list[float]:
    """Call the local Ollama embeddings endpoint for one text -> a real vector."""
    payload = json.dumps({"model": OLLAMA_EMBED_MODEL, "prompt": text}).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_BASE + "/api/embeddings",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["embedding"]


def _fail_no_backend() -> None:
    """Neither OpenAI key nor Ollama: print how to fix, exit clean (no traceback)."""
    print(
        "\n⚠️  没有可用的 embedding 后端。二选一，再重跑：\n"
        "   ① 本地零成本（推荐）：装 Ollama，然后 `ollama pull nomic-embed-text`，\n"
        "      启动 Ollama（默认 http://localhost:11434）后直接重跑即可。\n"
        "   ② 用 OpenAI：`export OPENAI_API_KEY=sk-...` 后重跑。\n"
    )
    raise SystemExit(0)


def embed(texts: Sequence[str]) -> list[list[float]]:
    """Text list -> real embedding vectors. Backend chosen once, recorded in BACKEND.

    Order: OpenAI (if key) -> local Ollama nomic-embed-text -> friendly exit.
    绝不使用假向量：离线走本机 Ollama 的真 embedding。
    """
    global _openai_client
    texts = list(texts)

    # ① real OpenAI embedding when a REAL key is set.
    #    "ollama" is a placeholder some demos set (via _local.py) only to point the
    #    chat model at Ollama — it is NOT a real embedding key, so skip it here.
    _key = os.environ.get("OPENAI_API_KEY", "")
    if _key and _key != "ollama":
        try:
            if _openai_client is None:
                from openai import OpenAI
                _openai_client = OpenAI()
            resp = _openai_client.embeddings.create(model=OPENAI_EMBED_MODEL, input=texts)
            BACKEND["embed"] = f"openai:{OPENAI_EMBED_MODEL}"
            return [d.embedding for d in resp.data]
        except Exception as e:  # key/网络/额度问题 -> 退到本地真 embedding，别崩
            print(f"[memory_kit] OpenAI embedding 不可用（{type(e).__name__}），改用本地 Ollama。")

    # ② real local embedding via Ollama nomic-embed-text
    if _ollama_alive():
        try:
            vecs = [_embed_ollama_one(t) for t in texts]
            BACKEND["embed"] = f"ollama:{OLLAMA_EMBED_MODEL}"
            return vecs
        except Exception as e:
            print(f"[memory_kit] 本地 Ollama embedding 调用失败（{type(e).__name__}）。")

    # ③ nothing available -> honest exit
    _fail_no_backend()
    return []  # unreachable; keeps type checkers happy


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    """Cosine similarity: 1=same direction (most similar), 0=orthogonal, -1=opposite."""
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


# ---------------------------------------------------------------------------
# 1) vector store: chromadb if installed, else a local JSON store (same interface)
# ---------------------------------------------------------------------------
class _LocalCollection:
    """Offline fallback store that mimics a chromadb collection's add/query/where.

    Persists to a JSON file (survives restart) to prove the "persist path" point.
    query uses cosine distance (distance = 1 - cosine); top-k returns the closest few.
    Supports a simple `where=` equality filter over metadata, like ChromaDB.
    """

    def __init__(self, path: Path, name: str):
        self._file = path / f"{name}.json"
        path.mkdir(parents=True, exist_ok=True)
        self._rows: list[dict] = []  # {"id","document","embedding","metadata"}
        if self._file.exists():
            self._rows = json.loads(self._file.read_text(encoding="utf-8"))

    def _save(self) -> None:
        self._file.write_text(json.dumps(self._rows, ensure_ascii=False), encoding="utf-8")

    def add(self, ids, documents, metadatas=None, embeddings=None):
        metadatas = metadatas or [{} for _ in ids]
        if embeddings is None:
            embeddings = embed(documents)  # embed here if caller didn't
        existing = {r["id"] for r in self._rows}
        for i, _id in enumerate(ids):
            row = {
                "id": _id,
                "document": documents[i],
                "embedding": list(embeddings[i]),
                "metadata": metadatas[i],
            }
            if _id in existing:  # same id -> update (upsert), controls noise / duplicates
                self._rows = [row if r["id"] == _id else r for r in self._rows]
            else:
                self._rows.append(row)
        self._save()

    def _match(self, meta: dict, where: dict | None) -> bool:
        if not where:
            return True
        return all(meta.get(k) == v for k, v in where.items())

    def query(self, query_texts, n_results=3, where=None):
        q = embed(query_texts)[0]
        pool = [r for r in self._rows if self._match(r["metadata"], where)]
        scored = [(1.0 - cosine(q, r["embedding"]), r) for r in pool]
        scored.sort(key=lambda t: t[0])  # smaller distance = more similar, comes first
        top = scored[:n_results]
        # mirror chromadb's return shape (each field is a per-query 2-D list)
        return {
            "ids": [[r["id"] for _, r in top]],
            "documents": [[r["document"] for _, r in top]],
            "metadatas": [[r["metadata"] for _, r in top]],
            "distances": [[round(d, 4) for d, _ in top]],
        }

    def count(self) -> int:
        return len(self._rows)


class _ChromaWrapper:
    """Wrap a real chromadb collection so it uses OUR embed() and returns aligned shape."""

    def __init__(self, col):
        self._col = col

    def add(self, ids, documents, metadatas=None, embeddings=None):
        if embeddings is None:
            embeddings = embed(documents)
        self._col.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas if metadatas else None,
            embeddings=embeddings,
        )

    def query(self, query_texts, n_results=3, where=None):
        qemb = embed(query_texts)
        kwargs = {"query_embeddings": qemb, "n_results": n_results}
        if where:
            kwargs["where"] = where
        return self._col.query(**kwargs)

    def count(self) -> int:
        return self._col.count()


def get_collection(name: str = "memory", persist_dir: str = "./chroma_db"):
    """Get a vector-store collection. chromadb first; local JSON fallback otherwise.

    Either way it persists locally — chromadb via PersistentClient(path=...), the
    fallback via a JSON file. That is exactly this lesson's point: forget the path,
    lose it on restart.
    """
    persist = Path(persist_dir)
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(persist))
        # cosine space so distances read the way we teach; embeddings come from our embed()
        col = client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
        BACKEND["store"] = f"chromadb@{persist}"
        return _ChromaWrapper(col)
    except Exception as e:
        BACKEND["store"] = f"local-json@{persist}"
        if not isinstance(e, ImportError):
            print(f"[memory_kit] chromadb 不可用（{type(e).__name__}），改用本地 JSON 向量库。")
        return _LocalCollection(persist, name)


def banner() -> None:
    """Print one line at each demo's start: which real backend is live this run."""
    if BACKEND["embed"] == "?":  # not embedded yet -> probe so the banner is accurate
        embed(["probe"])
    print(
        f"[memory_kit] embed={BACKEND['embed']}  store={BACKEND['store']}  "
        f"(真 embedding：设 OPENAI_API_KEY 用 OpenAI，否则用本机 Ollama nomic-embed-text)"
    )

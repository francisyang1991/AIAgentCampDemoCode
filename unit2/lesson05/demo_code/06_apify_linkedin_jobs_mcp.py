"""
06 · Apify LinkedIn Jobs MCP smoke test — real job search, deterministic output
==============================================================================
Run:
    export APIFY_API_TOKEN="apify_api_..."
    python 06_apify_linkedin_jobs_mcp.py

Needs:
  - Node.js / npx.
  - Python deps from requirements.txt.
  - An Apify API token in APIFY_API_TOKEN.

This demo intentionally does NOT ask a model to decide tool parameters. For a
live classroom demo, deterministic beats impressive: we call the MCP tools
directly, print the real Actor run, then print real dataset rows with job links.

Flow:
  1) Connect to Apify's remote MCP through mcp-remote.
  2) Call curious_coder--linkedin-jobs-scraper with a public LinkedIn search URL.
  3) If the narrow entry-level search has no rows, fall back to a broader search.
  4) Call get-dataset-items to read title/company/location/link fields.

Safety:
  This demo only searches job postings. It does not apply to jobs, send emails,
  edit files, or submit forms. Keep tokens in environment variables; never paste
  them into source code or commit them.
"""

from __future__ import annotations

import asyncio
import csv
import json
import os
from dataclasses import dataclass

from agents.mcp import MCPServerStdio

APIFY_LINKEDIN_JOBS_MCP_URL = (
    "https://mcp.apify.com/?tools=curious_coder/linkedin-jobs-scraper"
)

ACTOR_TOOL = "curious_coder--linkedin-jobs-scraper"
DATASET_TOOL = "get-dataset-items"

OUTPUT_FIELDS = ["title", "companyName", "location", "link", "postedAt"]


@dataclass(frozen=True)
class SearchCase:
    label: str
    url: str


SEARCH_CASES = [
    SearchCase(
        label="narrow: software engineer + entry-level + San Francisco",
        url=(
            "https://www.linkedin.com/jobs/search/"
            "?keywords=software%20engineer"
            "&location=San%20Francisco%2C%20California%2C%20United%20States"
            "&f_TPR=r604800&f_E=2&position=1&pageNum=0"
        ),
    ),
    SearchCase(
        label="fallback: product manager + San Francisco",
        url=(
            "https://www.linkedin.com/jobs/search/"
            "?keywords=product%20manager"
            "&location=San%20Francisco%2C%20California%2C%20United%20States"
            "&f_TPR=r604800&position=1&pageNum=0"
        ),
    ),
]


def _apify_token() -> str:
    token = os.getenv("APIFY_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "缺少 APIFY_API_TOKEN。先运行：export APIFY_API_TOKEN='apify_api_...'"
        )
    return token


def _content_text(call_result) -> str:
    try:
        return call_result.content[0].text
    except Exception:
        return ""


def _default_dataset(run_info: dict) -> dict:
    return run_info.get("storages", {}).get("datasets", {}).get("default", {})


def _parse_toon_rows(text: str) -> list[dict]:
    rows: list[dict] = []
    in_items = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("items[") and "{" in line:
            in_items = True
            continue
        if not in_items:
            continue
        if line.startswith(("itemCount:", "totalItemCount:", "offset:", "limit:", "```")):
            break
        if not line:
            continue

        parsed = next(csv.reader([line]))
        if len(parsed) < len(OUTPUT_FIELDS):
            continue
        rows.append(dict(zip(OUTPUT_FIELDS, parsed[: len(OUTPUT_FIELDS)])))

    return rows


async def _run_actor(server: MCPServerStdio, search: SearchCase) -> dict:
    print(f"\n[1] 调用 Apify Actor：{search.label}")
    print(f"    LinkedIn URL: {search.url}")
    result = await server.call_tool(
        ACTOR_TOOL,
        {
            "urls": [search.url],
            # The Actor's input schema enforces count >= 10. We display top 5.
            "count": 10,
            "scrapeCompany": False,
        },
    )
    text = _content_text(result)
    try:
        run_info = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Actor 没返回 JSON：{text[:500]}") from exc

    dataset = _default_dataset(run_info)
    print(
        "    runId={run_id} status={status} items={items}".format(
            run_id=run_info.get("runId", "?"),
            status=run_info.get("status", "?"),
            items=dataset.get("itemCount", 0),
        )
    )
    return run_info


async def _fetch_jobs(server: MCPServerStdio, dataset_id: str, limit: int = 5) -> list[dict]:
    print(f"\n[2] 读取 MCP dataset items：datasetId={dataset_id}")
    result = await server.call_tool(
        DATASET_TOOL,
        {
            "datasetId": dataset_id,
            "limit": limit,
            "clean": True,
            "fields": ",".join(OUTPUT_FIELDS),
        },
    )
    rows = _parse_toon_rows(_content_text(result))
    print(f"    rows={len(rows)}")
    return rows


def _print_jobs(rows: list[dict]) -> None:
    if not rows:
        print("\n没有拿到岗位 rows。可以放宽关键词、地点或时间窗口。")
        return

    print("\n[3] 真实岗位结果（来自 Apify LinkedIn Jobs MCP）")
    for index, row in enumerate(rows, 1):
        print(f"\n{index}. {row.get('title', '').strip()}")
        print(f"   Company : {row.get('companyName', '').strip()}")
        print(f"   Location: {row.get('location', '').strip()}")
        print(f"   Posted  : {row.get('postedAt', '').strip()}")
        print(f"   URL     : {row.get('link', '').strip()}")


async def main() -> None:
    token = _apify_token()

    async with MCPServerStdio(
        name="Apify LinkedIn Jobs MCP",
        params={
            "command": "npx",
            "args": [
                "-y",
                "mcp-remote",
                APIFY_LINKEDIN_JOBS_MCP_URL,
                "--silent",
                "--header",
                f"Authorization: Bearer {token}",
            ],
        },
        client_session_timeout_seconds=120,
    ) as server:
        tools = await server.list_tools()
        print("已连接 Apify MCP。可用工具：", ", ".join(t.name for t in tools))

        for search in SEARCH_CASES:
            run_info = await _run_actor(server, search)
            dataset = _default_dataset(run_info)
            dataset_id = dataset.get("id")
            item_count = int(dataset.get("itemCount") or 0)
            if not dataset_id:
                continue
            if item_count == 0:
                print("    这个搜索没有结果，自动尝试下一个搜索条件。")
                continue

            rows = await _fetch_jobs(server, dataset_id)
            _print_jobs(rows)
            return

        print("\n所有搜索条件都没有返回岗位。可以换关键词、地点或移除 f_TPR 时间过滤。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        print(f"\n⚠️  {e}")
    except FileNotFoundError:
        print(
            "\n⚠️  没找到 npx（Node.js）。本 demo 通过 npx 运行 mcp-remote。\n"
            "   装 Node.js 后用 `npx --version` 验证，再重跑本文件。"
        )
    except Exception as e:
        print(
            f"\n[失败] Apify LinkedIn Jobs MCP demo 没跑通"
            f"（{type(e).__name__}：{e}）。检查 token、网络和 Apify 额度。"
        )

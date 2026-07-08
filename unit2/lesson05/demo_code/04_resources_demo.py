"""
04 · Resources demo — the "read-only data" primitive of MCP (rubric://{role})
==============================================================================
Run:     python 04_resources_demo.py
Needs:   01_minimal_mcp_server.py in this folder (launched here as a subprocess).
         NO API key / model required — this only reads a resource, it never
         calls an LLM. Perfect offline demo.

The MCP triad (P3 slides), on the axis of "who is in control":
  - Tools     = actions the model takes   (side effects, like HTTP POST)
  - Resources = data the app/user reads   (read-only, like HTTP GET)   <- focus
  - Prompts   = templates the user invokes (commands the Host offers)

This script connects to 01's ResuMatch Server, lists its Resources, then reads
the scoring rubric for a specific role. Note list_resources / read_resource are
async too — remember await.

ResuMatch theme: 01 exposes the scoring rubric as a resource TEMPLATE
rubric://{role}. That means any client (this script, a chat Host, a plugin) can
read the SAME scoring standard for ANY role by filling in {role} — the typical
use of Resources: treat the "scoring standard" as data anyone can read, not an
action that changes the world.
"""

import sys
import asyncio
from pathlib import Path

from agents.mcp import MCPServerStdio

SERVER_PATH = Path(__file__).with_name("01_minimal_mcp_server.py")


def _resource_text(read_result) -> str:
    """Pull the text out of a read_resource result (contents[0].text)."""
    for content in read_result.contents:
        text = getattr(content, "text", None)
        if text is not None:
            return text
    return str(read_result)


async def main():
    async with MCPServerStdio(
        name="ResuMatch Server",
        params={"command": sys.executable, "args": [str(SERVER_PATH)]},
    ) as server:
        # 1) List the resource templates this Server provides.
        #    rubric://{role} is a TEMPLATE — the {role} slot is filled by the client.
        templates = await server.list_resource_templates()
        print("可用的 Resource 模板：")
        for tpl in templates.resourceTemplates:
            print(f"  - {tpl.uriTemplate}  ({tpl.name})")

        # 2) Read the rubric for two different roles by filling in {role}.
        #    Same standard, any role — that is the point of a resource template.
        for role in ("senior-ml-engineer", "data-analyst"):
            uri = f"rubric://{role}"
            read = await server.read_resource(uri)
            print(f"\n读取 {uri} 的内容：")
            print(" ", _resource_text(read))


if __name__ == "__main__":
    asyncio.run(main())

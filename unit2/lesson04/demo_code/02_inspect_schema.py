"""
02 · Inspect the Schema that @function_tool auto-generates
--------------------------------------------------
Run:  python 02_inspect_schema.py

The model decides whether to call a tool from its Schema, not its body:
  name        — what the tool is called (from the function name)
  description — what it can do (from the docstring)
  parameters  — which args and what types (from the type hints)

After @function_tool decorates it, all of this is generated for you.
This lesson prints it out so you can see "the manual the model reads".

★ Single course theme: the ResuMatch job-hunt assistant. We take the job tool
  get_role_keywords and look at its auto-generated Schema (the level param is
  pinned to a fixed set of values via Literal).
"""

from agents import function_tool
from typing import Literal


@function_tool
def get_role_keywords(role: str, level: Literal["junior", "senior"] = "junior") -> dict:
    """Look up the hard skills a target role values, to compare against a resume and find gaps.

    Args:
        role: target job title, e.g. "Data Analyst".
        level: seniority, "junior" or "senior"; defaults to "junior".
    """
    return {"status": "ok", "role": role, "level": level, "skills": ["SQL", "Python"]}


print("=== 工具对象本身 ===")
print(get_role_keywords)

# The @function_tool object carries the metadata the model uses.
# Attribute names vary by version, so try each one and print whatever resolves.
print("\n=== 关键字段 ===")
for attr in ("name", "description"):
    if hasattr(get_role_keywords, attr):
        print(f"{attr:12} : {getattr(get_role_keywords, attr)}")

# The parameter schema is usually a JSON Schema (dict).
for attr in ("params_json_schema", "parameters", "schema"):
    if hasattr(get_role_keywords, attr):
        import json

        print(f"\n{attr} (参数 JSON Schema):")
        value = getattr(get_role_keywords, attr)
        try:
            print(json.dumps(value, ensure_ascii=False, indent=2))
        except TypeError:
            print(value)
        break

print(
    "\n提示：函数签名(role: str, level: Literal[...]) + docstring，"
    "\n就是上面这份 Schema 的来源 —— 这也是为什么这两样要认真写。"
)

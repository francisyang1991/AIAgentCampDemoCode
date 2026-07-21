"""
jobs.py · 本节语料 —— 50 条真实岗位描述（JD）
=================================================
This is the corpus every RAG demo (02-05) retrieves over. Each JD is a short,
realistic Chinese job posting drawn from common tech/product/data roles, tagged
with `role` + `seniority` metadata so demos can show metadata filtering (where=).

Why real JDs (not toy sentences):
  - 真实数据（课程达标线第 ② 条）——不是造三五句糊弄检索。
  - 有噪声：50 条里大部分和某个查询无关，正好练"把不相关的筛掉"。
  - 能验证：召回对不对，一眼就看得出。

Data shape:  JDS = [(id, text, {"role": ..., "seniority": ...}), ...]
Helper:      ids(), texts(), metas() split JDS into ChromaDB's three parallel lists.
"""

from __future__ import annotations

# (id, 岗位描述, {role, seniority})
# role: analyst / backend / frontend / product / algo / data-eng / devops / ...
# seniority: junior / mid / senior
JDS: list[tuple[str, str, dict]] = [
    ("jd_001", "数据分析师：负责业务指标监控、用 SQL 取数、产出周报与看板，熟练 Excel 与 Tableau。", {"role": "analyst", "seniority": "junior"}),
    ("jd_002", "高级数据分析师：主导 A/B 实验设计与分析，用 Python 建模，向业务负责人汇报洞察。", {"role": "analyst", "seniority": "senior"}),
    ("jd_003", "BI 分析师：搭建自助分析看板，维护数据口径，支持运营与市场团队取数需求。", {"role": "analyst", "seniority": "mid"}),
    ("jd_004", "增长数据分析：围绕拉新留存做漏斗分析，定位流失环节，用数据驱动增长实验。", {"role": "analyst", "seniority": "mid"}),
    ("jd_005", "商业分析师：做市场与竞品研究，输出商业模型与财务测算，支撑管理层决策。", {"role": "analyst", "seniority": "senior"}),
    ("jd_006", "Junior data analyst: build dashboards, write SQL, support weekly reporting for the product team.", {"role": "analyst", "seniority": "junior"}),
    ("jd_007", "后端工程师：用 Java / Spring 开发微服务，负责订单系统的高并发接口与数据库设计。", {"role": "backend", "seniority": "mid"}),
    ("jd_008", "高级后端工程师：主导支付核心链路架构，保障一致性与稳定性，熟悉分布式事务。", {"role": "backend", "seniority": "senior"}),
    ("jd_009", "Go 后端开发：构建高性能网关与 RPC 服务，熟悉 gRPC、消息队列与容器化部署。", {"role": "backend", "seniority": "mid"}),
    ("jd_010", "Python 后端工程师：用 FastAPI 搭建 API 服务，对接大模型能力，负责鉴权与限流。", {"role": "backend", "seniority": "mid"}),
    ("jd_011", "初级后端：参与内部管理系统开发，写 CRUD 接口、单元测试，逐步熟悉线上运维。", {"role": "backend", "seniority": "junior"}),
    ("jd_012", "Node.js 后端：负责实时通讯服务，用 WebSocket 处理长连接，优化消息投递延迟。", {"role": "backend", "seniority": "mid"}),
    ("jd_013", "前端工程师：用 React + TypeScript 开发 B 端管理后台，负责组件库与可视化图表。", {"role": "frontend", "seniority": "mid"}),
    ("jd_014", "高级前端：主导前端性能优化与工程化建设，搭建微前端架构，制定团队规范。", {"role": "frontend", "seniority": "senior"}),
    ("jd_015", "初级前端：用 Vue 开发营销活动页，还原设计稿，配合后端联调接口。", {"role": "frontend", "seniority": "junior"}),
    ("jd_016", "全栈工程师：独立负责小型内部工具从前端到后端，熟悉 Next.js 与 PostgreSQL。", {"role": "frontend", "seniority": "mid"}),
    ("jd_017", "产品经理：负责 B 端 SaaS 产品，梳理需求、画原型、写 PRD，数据驱动迭代。", {"role": "product", "seniority": "mid"}),
    ("jd_018", "高级产品经理：主导用户增长产品线，定义北极星指标，协调研发与运营落地。", {"role": "product", "seniority": "senior"}),
    ("jd_019", "数据产品经理：负责数据平台与指标体系，把业务需求翻译成数据能力，懂 SQL。", {"role": "product", "seniority": "mid"}),
    ("jd_020", "AI 产品经理：负责大模型应用产品，设计对话与 Agent 流程，跟进评测与效果优化。", {"role": "product", "seniority": "senior"}),
    ("jd_021", "初级产品助理：整理竞品资料、维护需求池、组织评审会议，输出会议纪要。", {"role": "product", "seniority": "junior"}),
    ("jd_022", "算法工程师：做推荐系统召回与排序，用深度模型优化点击率，熟悉特征工程。", {"role": "algo", "seniority": "mid"}),
    ("jd_023", "高级算法工程师：主导搜索排序算法，负责向量检索与语义匹配的效果与性能。", {"role": "algo", "seniority": "senior"}),
    ("jd_024", "NLP 算法工程师：做文本分类与信息抽取，微调预训练模型，落地到业务链路。", {"role": "algo", "seniority": "mid"}),
    ("jd_025", "机器学习工程师：搭建特征平台与训练流水线，负责模型上线与在线服务。", {"role": "algo", "seniority": "senior"}),
    ("jd_026", "初级算法：参与数据清洗与标注、复现论文基线，在导师指导下做小规模实验。", {"role": "algo", "seniority": "junior"}),
    ("jd_027", "LLM 应用工程师：用 RAG 与向量数据库搭建企业知识问答，负责检索质量与提示工程。", {"role": "algo", "seniority": "mid"}),
    ("jd_028", "数据工程师：负责数据仓库建模与 ETL 管道，用 Spark 处理海量日志，保障数据质量。", {"role": "data-eng", "seniority": "mid"}),
    ("jd_029", "高级数据工程师：主导实时数仓架构，用 Flink 做流式计算，治理数据血缘与成本。", {"role": "data-eng", "seniority": "senior"}),
    ("jd_030", "初级数据开发：编写调度任务、维护离线报表管道，排查数据延迟与断流问题。", {"role": "data-eng", "seniority": "junior"}),
    ("jd_031", "推荐算法工程师：负责信息流推荐的多目标建模，做实时特征与在线学习。", {"role": "algo", "seniority": "senior"}),
    ("jd_032", "DevOps 工程师：维护 CI/CD 流水线与 Kubernetes 集群，负责监控告警与容量规划。", {"role": "devops", "seniority": "mid"}),
    ("jd_033", "SRE 工程师：保障核心服务可用性，做故障演练与容灾，编写自动化运维脚本。", {"role": "devops", "seniority": "senior"}),
    ("jd_034", "初级运维：负责服务器上下线、日常巡检、处理工单，学习云平台基本操作。", {"role": "devops", "seniority": "junior"}),
    ("jd_035", "测试开发工程师：搭建自动化测试框架，写接口与 UI 自动化用例，把关发布质量。", {"role": "qa", "seniority": "mid"}),
    ("jd_036", "高级测试开发：主导性能与稳定性测试体系，做混沌工程，推动质量左移。", {"role": "qa", "seniority": "senior"}),
    ("jd_037", "数据科学家：用统计与机器学习解业务问题，做用户分层与预测建模，讲清结论。", {"role": "data-sci", "seniority": "senior"}),
    ("jd_038", "初级数据科学家：在导师带领下做特征探索与模型验证，产出分析报告。", {"role": "data-sci", "seniority": "junior"}),
    ("jd_039", "UI 设计师：负责移动端界面视觉设计，维护设计规范与组件库，配合前端还原。", {"role": "design", "seniority": "mid"}),
    ("jd_040", "UX 设计师：做用户研究与交互设计，画流程与线框，用可用性测试验证方案。", {"role": "design", "seniority": "senior"}),
    ("jd_041", "运营专员：负责社群与内容运营，策划活动、写文案、盯数据复盘效果。", {"role": "ops", "seniority": "junior"}),
    ("jd_042", "增长运营：负责渠道投放与用户召回，做 ROI 分析，用 SQL 自助拉数据。", {"role": "ops", "seniority": "mid"}),
    ("jd_043", "项目经理：统筹跨团队交付，管理排期与风险，推动需求按里程碑落地。", {"role": "pm", "seniority": "senior"}),
    ("jd_044", "移动端 iOS 工程师：用 Swift 开发 App，负责性能优化与埋点，熟悉发布流程。", {"role": "mobile", "seniority": "mid"}),
    ("jd_045", "Android 工程师：用 Kotlin 开发核心业务模块，处理兼容性与内存问题。", {"role": "mobile", "seniority": "mid"}),
    ("jd_046", "安全工程师：负责应用与网络安全，做渗透测试与漏洞修复，制定安全规范。", {"role": "security", "seniority": "senior"}),
    ("jd_047", "初级前端实习：参与页面开发与 bug 修复，学习团队工程流程与代码规范。", {"role": "frontend", "seniority": "junior"}),
    ("jd_048", "大数据平台工程师：负责 Hadoop / Spark 集群运维与调优，支撑离线计算平台。", {"role": "data-eng", "seniority": "senior"}),
    ("jd_049", "商业数据分析（实习）：协助做经营分析、整理数据、维护业务看板。", {"role": "analyst", "seniority": "junior"}),
    ("jd_050", "解决方案架构师：面向客户设计技术方案，做技术选型与 PoC，衔接售前与研发。", {"role": "architect", "seniority": "senior"}),
]


def ids() -> list[str]:
    """The `ids` list ChromaDB.add wants (one unique id per JD)."""
    return [j[0] for j in JDS]


def texts() -> list[str]:
    """The `documents` list ChromaDB.add wants (the JD text that gets embedded)."""
    return [j[1] for j in JDS]


def metas() -> list[dict]:
    """The `metadatas` list ChromaDB.add wants (role/seniority tags for where= filtering)."""
    return [j[2] for j in JDS]

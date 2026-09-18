# AILA 架构审查报告（Architecture Review）

- **审查日期**：2026-09-18
- **审查对象**：`e:\06_ai_learning_assistant`，HEAD = `4105ac9`（含未提交工作区）
- **审查方式**：**只读**——阅读全部源码/配置/文档，并以只读命令做实证（不修改任何已有文件）
- **Python**：3.13.15（`.venv`）　**OS**：Windows / PowerShell 5.1（控制台代码页 936）

---

## 0. 结论摘要（TL;DR）

| 维度 | 结论 |
| --- | --- |
| 分层职责 | ✅ **清晰**：`config`(配置) / `agent`(组装) / `runtime`(执行) / `tools`(能力) / `prompts`(上下文资产) / `main`(交互) 六层边界明确，符合 AGENTS.md「简单 + 模块化」 |
| 可运行性 | ❌ **当前不可运行**：`agent.py:27` 引用未定义的 `system_prompt`，`python -m aila.main` 立即 `NameError`（exit code 1） |
| 架构正确性 | ✅ 除上述缺口外链路设计**正确**：内存复现实测 `llm + calculator + system.md` 端到端跑通，工具调用成功（`123*456 → 56088`） |
| 主要风险 | ① system prompt 装载缺失（**P0**）② 使用 LangGraph V1 已弃用 API（**P1**）③ 依赖/打包/文档三处与代码脱节（**P1**）④ 评测层 0 字节占位（**P2**，违反 AGENTS.md 原则 5） |
| 最该先做的一件事 | 实现 `src/aila/prompts/loader.py`（现为 0 字节空文件），把 `system.md` 接入 `agent.py` |
| 下一阶段路线 | Step 0 修复 → Step 1 工程地基 → Step 2 运行时(记忆/观测) → Step 3 评测闭环 → Step 4 RAG 最小闭环 → Step 5 MCP/联网 |

---

## 1. 审查范围与方法

### 1.1 已读文件（只读）

| 类别 | 文件 |
| --- | --- |
| 应用代码（8） | `src/aila/{__init__,agent,config,main}.py`、`src/aila/runtime/runner.py`、`src/aila/tools/{__init__,calculator}.py`、`src/aila/prompts/loader.py`(0 B) |
| 上下文资产（1） | `src/aila/prompts/system.md`（845 字符） |
| 工程配置（8） | `pyproject.toml`、`requirements.txt`、`requirements.lock.txt`、`.env`、`.env.example`、`.gitignore`、`.vscode/settings.json`、`src/ai_learning_assistant.egg-info/*` |
| 文档（4） | `AGENTS.md`、`README.md`、`docs/architecture.md`、`docs/product_spec.md` |
| 测试/评测（3） | `tests/test_import.py`、`evals/datasets/basic_questions.json`(0 B)、`evals/graders/answer_quality.py`(0 B) |
| 知识库（37） | `knowledge/01应用开发学习笔记/**/*.md`（结构扫描，非全文） |

### 1.2 实证命令（全部只读；未改动项目文件）

| # | 目的 | 命令要点 |
| --- | --- | --- |
| A1/A2 | 验证入口能否启动 | `from aila.agent import create_agent; create_agent()` / `'hi','exit' \| python -m aila.main` |
| B | 验证所用 API 现状 | `inspect.signature(langgraph.prebuilt.create_react_agent)`、`hasattr(langchain.agents,"create_agent")`、`convert_to_messages([{...}])` |
| C | 验证安装形态 | `pip show ai-learning-assistant`、`List .venv\Lib\site-packages\*.pth` |
| D | 知识库资产扫描 | 逐文件统计编码/BOM/行尾/标题数/字节 |
| E | 端到端内存复现 | `create_react_agent(llm, tools=[calculator], prompt=system.md内容)` + `graph.invoke({"messages":[...]})` |
| G | pip 能否读取 requirements | `pip install --dry-run --no-index --no-deps -r requirements.txt` |
| H | 打包完整性 | 复制到 `%TEMP%` 后 `pip wheel`，解包列 namelist（**项目目录零改动**） |

---

## 2. 项目现状快照

### 2.1 目录结构（已清理 `.venv/.git/__pycache__`）

```
06_ai_learning_assistant/
├─ AGENTS.md                  1322 B   工程契约（原则/技术栈/结构/工作流）
├─ README.md                  1070 B   入门文档（⚠ 仍写旧路径）
├─ pyproject.toml              346 B   打包与依赖声明（⚠ 缺 dev 依赖/脚本入口/包数据）
├─ requirements.txt            108 B   ⚠ UTF-16LE + BOM（git 视为二进制）
├─ requirements.lock.txt        82 B   4 个直接依赖锁定
├─ .env                        355 B   ⚠ 含真实明文 API Key
├─ .env.example                516 B
├─ .vscode/settings.json       162 B
├─ docs/
│   ├─ architecture.md         752 B   概念架构（⚠ 与实际模块图不同步）
│   ├─ product_spec.md         871 B   三阶段产品规划
│   └─ architecture_review.md          ← 本报告（新增）
├─ evals/
│   ├─ datasets/basic_questions.json   0 B  ⚠ 占位
│   └─ graders/answer_quality.py       0 B  ⚠ 占位
├─ knowledge/01应用开发学习笔记/         37 × .md，共 382,453 B（真实笔记资产）
├─ src/
│   ├─ aila/
│   │   ├─ __init__.py          0 B
│   │   ├─ config.py         1139 B   配置层
│   │   ├─ agent.py           524 B   组装层（⚠ 当前有 NameError）
│   │   ├─ main.py            883 B   交互层
│   │   ├─ prompts/
│   │   │   ├─ loader.py        0 B  ⚠ 空文件（本应装载 system.md）
│   │   │   └─ system.md      891 B   system prompt（未提交修改）
│   │   ├─ runtime/runner.py  279 B   执行层（无 __init__.py）
│   │   └─ tools/
│   │       ├─ __init__.py     70 B   工具注册/导出
│   │       └─ calculator.py 1078 B   AST 安全计算器
│   └─ ai_learning_assistant.egg-info/  ⚠ 陈旧（SOURCES 只列 4 个模块）
└─ tests/test_import.py        66 B   仅 1 个 import 冒烟测试
```

### 2.2 技术栈实测版本（`pip list`）

| 包 | 版本 | 说明 |
| --- | --- | --- |
| langchain | 1.4.0 | 与 `requirements.lock.txt` 一致 ✅ |
| langgraph | 1.2.11 | 一致 ✅ |
| langchain-openai | 1.6.2 | 一致 ✅ |
| python-dotenv | 1.2.3 | 一致 ✅ |
| langchain-core | 1.6.3 | 未在 lock 中（间接依赖） |
| langgraph-prebuilt | 1.1.0 | `create_react_agent` 所在包 |
| openai | 3.14.1 | 间接 |
| langsmith | 0.12.5 | **已安装但完全未使用**（无可观测性配置） |
| pytest | 9.1.1 | **已安装但未在任何依赖文件中声明** ⚠ |
| pip | 26.2.1 | 可正常读取 UTF-16 requirements（见 §5.4） |
| setuptools / wheel | **未安装** | ⚠ `pip install -e . --no-build-isolation` 会失败 |

### 2.3 Git 状态

```
4105ac9 (HEAD -> master) feat: add first langgraph agent with calculator tool   ← 已提交
f9be66c refactor: add runtime layer
9950a72 fix: resolve project root path
9b127e1 chore: stabilize project structure

工作区： M src/aila/agent.py          （不含 system_prompt 定义 → 崩溃）
        M src/aila/prompts/system.md  （0 B → 891 B，已写入内容）
        ?? src/aila/prompts/loader.py （0 B 空文件，未实现）
审查期间新出现： D knowledge/01应用开发学习笔记/02基础知识/思考复盘.md
        （未提交的删除；该文件仍存在于 HEAD，可用
          git restore "knowledge/01应用开发学习笔记/02基础知识/思考复盘.md" 恢复）
其它：  69 个跟踪文件；.venv 为 **editable 安装**（.pth → E:\06_ai_learning_assistant\src）
```

---

## 3. 调用链与数据流（实测）

### 3.1 设计意图（代码体现的链路）

```
main.py            交互层：input() → run_agent() → print(response.content)
  ↓
runtime/runner.py  执行层：agent.invoke({"messages":[{"role":"user","content":msg}]})
  ↓                返回 result["messages"][-1]
agent.py           组装层：ChatOpenAI(model/base_url/api_key/temperature)
  ↓                        + create_react_agent(tools=[calculator], prompt=系统提示)
langgraph 图       推理循环：ai → tool_calls → tools/calculator.py → ai
  ↓
ChatOpenAI → DashScope OpenAI 兼容端点（deepseek-v4.1-flash）
```

### 3.2 实测证据

| 验证点 | 结果 |
| --- | --- |
| `create_agent()` | ❌ `NameError: name 'system_prompt' is not defined`（`agent.py:27`） |
| `python -m aila.main`（仓库根，管道输入） | ❌ 同样的 `NameError`，**exit code 1** |
| `create_react_agent` 形状 | ✅ `module=langgraph.prebuilt.chat_agent_executor`，接受 `prompt=` 参数 |
| `runner.py` 的 dict 形状是否合法 | ✅ `convert_to_messages([{"role":"user","content":"hi"}]) → [HumanMessage(content='hi')]`，LangGraph `messages` 通道接受 dict |
| 提示词文件可读 | ✅ `system.md` 读取成功（845 字符） |
| **端到端（内存复现）** | ✅ `state keys=['messages']`、`msg types=['human','ai','tool','ai']`、`tool calls=['calculator']`、`last content='56088'` |
| 弃用警告 | ⚠ `LangGraphDeprecatedSinceV10: create_react_agent has been moved to langchain.agents... Deprecated in LangGraph V1.0, to be removed in V2.0` |

> **关键判断**：链路设计本身**没有问题**；唯一缺口是"系统提示词没有装载进 `create_agent()`"。因此 P0 修复量极小（一个 loader + 一行 import），修好后 `python -m aila.main` 即可正常工作。

---

## 4. 模块职责评估

### 4.1 逐模块判定

| 模块 | 应负职责 | 是否清晰 | 评价 |
| --- | --- | --- | --- |
| `config.py` | 唯一的配置来源：`.env` → 常量 | ✅ 清晰 | 单一职责做得好（路径推导已修正为 `parents[2]`）；`get_required_env()` fail-fast + 报错提示友好。**副作用在 import 期发生**（缺 `.env` 时 import 即抛错），会影响测试与 CI（见 §5.6） |
| `agent.py` | 组装 LLM + 工具 + 提示词 → 可运行体 | ⚠ 基本清晰但有缺陷 | 组装动作正确，但 ① `system_prompt` 未定义（P0）② 工具列表与提示词都**硬编码**在函数体里，缺少注册表/装载器边界 ③ `temperature=0.7` 写死，绕过 config 层 ④ 缩进与包内其它文件不一致（`llm,` 与 `)` 缩进错位） |
| `runtime/runner.py` | 唯一的"执行"入口：调用 + 未来的重试/超时/追踪/流式 | ✅ 职责方向正确 | 位置选得好（这是 harness 的天然接缝）。但 ① 无 docstring/类型注解 ② 代码风格被压平（`def run_agent(agent,message):`、无空行）③ `runtime/` 无 `__init__.py` ④ 返回 `result["messages"][-1]` 把 LangGraph 状态形状泄漏给上层 ⑤ 无异常处理/超时/日志 |
| `tools/` | 能力层：一个工具一个模块 + 统一导出 | ✅ 清晰 | `__init__.py` 转导出 + `__all__` 的写法正确、可扩展；`calculator.py` 用 AST 白名单求值，**避开了 `eval()` 注入**，安全意识好 |
| `prompts/` | 上下文资产：提示词作为数据而非代码 | ⚠ 意图好但未完成 | `system.md` 内容质量高（身份/职责/行为规则/工具使用/学习风格五段式）；但 `loader.py` 是 **0 字节空文件**，导致 P0；且 `prompts/` 无 `__init__.py`、`.md` 未声明为 package-data（P1，见 §5.3） |
| `main.py` | 交互层：只做 I/O | ✅ 清晰 | 已正确做到"不直接调用模型"（上一轮重构的成果）；但仍缺 EOF/中断保护、非交互模式、工具调用可见性 |
| `tests/` | 软件测试 | ⚠ 过薄 | 仅 `test_import()` 一个冒烟断言；无 config/runner/tools/agent 测试；无 pytest 配置 |
| `evals/` | AI 行为评测（AGENTS.md 原则 5） | ❌ 未开始 | 两个文件均为 0 字节占位 |
| `knowledge/` | 知识库资源 | ✅ 资产丰富 | 37 个 md、382 KB 中文笔记，全部 **UTF-8 无 BOM + LF**，编码干净；1 个空文件、`06 驾驭工程` 目录名含空格/全角符号（切片器需容错） |
| `docs/` | 设计文档 | ⚠ 与代码脱节 | `architecture.md` 画的是"User→Agent Runtime→LLM→Tools→Knowledge"概念链，**不是实际模块图**（缺 `aila.*` 命名、缺 `runtime/runner` 真实边界）；`product_spec.md` 仍准确 |

### 4.2 依赖方向检查（是否有环 / 是否越层）

```
main ──► runtime.runner ──► (注入的 agent 对象，运行期)
  │                              ▲
  └──► agent ──► prompts.loader（缺） ──► config
         │  └──► tools.calculator
         └──► config（唯一读 env 处）
```

- ✅ 无循环依赖；`config` 只被下游依赖、不反向依赖任何模块（正确的"最底层"）。
- ✅ `tools/` 不依赖 `agent`/`runtime`（正确：能力层不应知道装配细节）。
- ⚠ `runtime/runner.py` 依赖的是**运行期注入的对象**（鸭子类型），而非 import 具体 agent —— 这是好设计，但**契约未写下来**（返回值形状、异常、是否流式）。
- ⚠ 唯一"越层"风险：`main.py` 直接消费 `response.content`；当 `runner` 未来改返回类型（如字符串或 dataclass）时，`main` 会被动破坏 → 建议把契约固化（§6.3）。

---

## 5. 问题清单（按优先级）

### P0 —— 阻断运行（必须立刻修）

**P0-1　`system_prompt` 未定义，整个应用无法启动**

- 证据：`agent.py:27` → `prompt=system_prompt`，文件内既无定义也无 import；实测 `python -m aila.main` → `NameError`，**exit code 1**。
- 根因：`src/aila/prompts/loader.py` 是 **0 字节空文件**（`git status: ?? loader.py`），"提示词装载"这一步只创建了文件、没写实现。
- 影响：100% 阻断；`tests/` 也测不到（没有测试覆盖 `create_agent()`）。
- 建议：实现 `load_system_prompt()`（优先 `importlib.resources`，回退 `Path(__file__).with_name("system.md")`），在 `agent.py` 顶部 import 并在 `create_react_agent(..., prompt=load_system_prompt())` 使用。
- 最小验收：`python -m aila.main` 可对话；`python -c "from aila.agent import create_agent; print(type(create_agent()))"` 不抛错。

### P1 —— 影响正确性 / 可复现性 / 可维护性

**P1-1　使用了 LangGraph V1 已弃用 API**

- 证据（运行时警告原文）：`LangGraphDeprecatedSinceV10: create_react_agent has been moved to langchain.agents. Please update your import to 'from langchain.agents import create_agent'. Deprecated in LangGraph V1.0 to be removed in V2.0.`
- 另证：`hasattr(langchain.agents, "create_agent") == True`（当前栈已可直接迁移）。
- 影响：升级到 LangGraph V2 时会硬性断裂；且 `create_agent` 的参数形状不同（需迁移 `prompt=`/`tools=` 写法）。
- 建议：迁移到 `from langchain.agents import create_agent`，并把 `prompt` 改为 messages 形式（如 `system_prompt=` 或 `[SystemMessage(...)]`），迁移后删除对 `langgraph.prebuilt` 的直接依赖。

**P1-2　`runtime/runner.py` 的契约与风格不达标**

- 证据：全文 14 行，`def run_agent(agent,message):`（缺空格）、无 docstring、无类型注解、无空行分隔；`runtime/` 无 `__init__.py`；`return result["messages"][-1]`。
- 影响：① 上层 `main.py` 必须知道 LangGraph 状态形状，层间耦合 ② 无超时/重试/日志，出问题时无法定位（违反 `docs/architecture.md` 原则 3「Changes should be observable」）③ 与包内其它文件的风格不一致（`config.py`/`main.py` 有 docstring 与规范缩进）。
- 建议：补 docstring + 类型注解；把返回契约写成 `-> AIMessage`（或自定义 `RunResult`）；在此层加入 logging 与（可选的）异常包装；补 `runtime/__init__.py`。

**P1-3　打包会丢失 system prompt（`.md` 未声明为包数据）**

- 证据（把项目复制到 `%TEMP%` 后 `pip wheel` 并解包，**项目目录零改动**）：

```
wheel 内容：
  aila/__init__.py  aila/agent.py  aila/config.py  aila/main.py
  aila/prompts/loader.py  aila/runtime/runner.py
  aila/tools/__init__.py  aila/tools/calculator.py
  → 没有 aila/prompts/system.md
```

- 说明：`.py` 文件（含无 `__init__.py` 的 `runtime/`、`prompts/`）**会**被打包（更正一种常见误解）；真正丢的是**非 Python 资产**。
- 影响：`pip install .` 后 `load_system_prompt()` 在已安装环境读不到 `system.md` → 又是运行时崩溃（只是从开发环境推迟到安装环境）。
- 建议：`pyproject.toml` 增 `[tool.setuptools.package-data]` 声明 `aila.prompts = ["*.md"]`；同时显式声明 `[tool.setuptools.packages.find] where = ["src"]` 并给 `runtime/`、`prompts/` 补 `__init__.py`，避免依赖隐式自动发现。

**P1-4　依赖有三个真相来源，且 dev 依赖未声明**

- 证据：`pyproject.toml` `dependencies`（4 个，未锁版本）、`requirements.txt`（4 个未锁，**UTF-16LE+BOM**，git 视为二进制）、`requirements.lock.txt`（4 个已锁，与 venv 完全一致 ✅）；**pytest 9.1.1 已安装却未出现在任何依赖文件**；`setuptools`/`wheel` 在 venv 中不存在（`import setuptools` → `ModuleNotFoundError`），因此 `pip install -e . --no-build-isolation` 会失败。
- 更正：`pip install -r requirements.txt` **能正常工作**（实测 `pip 26.2.1` 解析 4 行成功、exit code 0，即 pip 的 BOM 自动识别覆盖 UTF-16），所以这是**卫生/可读性问题而非功能阻断**；但它确实让 `git diff` 显示 `Bin`、编辑器/`Get-Content` 出现乱码。
- 建议：以 `pyproject.toml` 为唯一真相；`requirements.txt` 重写为 UTF-8(no BOM) 或直接删除（README 改指向 `pip install -e .`）；新增 `[project.optional-dependencies] dev = ["pytest", "ruff"]`；把 `setuptools`/`wheel` 纳入构建依赖（`build-system.requires` 已有 `setuptools`，走默认隔离即可，但需文档说明需要联网）。

**P1-5　`main.py` 不利于自动化验证**

- 证据：仅有交互 `input()` 循环；无 `EOFError`/`KeyboardInterrupt` 处理（管道/CI 调用会抛栈）；无 `--message/--once` 非交互入口；只打印 `response.content`，**不显示工具调用轨迹**。
- 影响：① 无法写"一条命令跑通一次对话"的冒烟测试 ② 对"学习型助手"而言，看不到 `tool` 消息与中间推理，学习价值大打折扣 ③ evals 没有可复用的调用入口。
- 建议：`main(argv)` 支持 `--message/-m` 与 `--once`；捕获 `EOFError` 正常退出；打印时区分 `ai` 消息与 `tool` 调用（例如打印 `[tool] calculator(...) -> 56088`）。

**P1-6　`config.py` 的 import 期副作用使测试/CI 需要密钥**

- 证据：`OPENAI_API_KEY = get_required_env("OPENAI_API_KEY")` 在模块导入时执行；`tests/test_import.py` 只 import `aila`（空 `__init__.py`）所以恰好不需要 `.env`。
- 影响：任何 import `aila.agent`/`aila.config` 的测试在没有密钥的机器/CI 上**直接失败**，无法离线跑测试。
- 建议：保留 fail-fast（这是当前设计优点），但在 `tests/conftest.py` 里统一注入测试用环境变量（或提供 `aila.config.load_env()` 供测试先调用），并在文档写明"测试不需要真实密钥"。

### P2 —— 质量与一致性（可排期）

| # | 问题 | 证据 | 建议 |
| --- | --- | --- | --- |
| P2-1 | 安全：`.env` 含**真实明文 API Key**（`sk-ws-…`） | `.env` 355 B；`.gitignore` 已忽略 `.env`、且 `git ls-files` 确认未被跟踪 ✅ | 尽快**轮换该密钥**；`.env.example` 增加 DashScope 示例（现只有 OpenAI/DeepSeek/Ollama 三种） |
| P2-2 | `calculator.py` 表达式覆盖不全 | `operators` 只有 `Add/Sub/Mult/Div`：`2**3` → `KeyError` 被兜底成 `"Error: ..."`；`-5`(UnaryOp) → `"Error: Unsupported expression"` | 显式支持 `Pow`/`USub`，或明确"仅四则运算"并把这个边界写进工具 docstring（LLM 靠 docstring 判断能力）；`operators` 改名 `_OPERATORS` 并冻结 |
| P2-3 | `calculator.py` 错误被吞成字符串 | `except Exception as e: return f"Error: {e}"`（宽泛捕获） | 保留面向 LLM 的字符串返回（合理），但至少 `logging.warning` 记录；不要捕获 `KeyboardInterrupt/SystemExit`（`except Exception` 已避开，OK） |
| P2-4 | 空文件/占位较多 | `aila/__init__.py` 0 B、`prompts/loader.py` 0 B、`evals/*` 0 B、`knowledge/…/Cherry Studio.md` 0 B | `__init__.py` 加一行 docstring；`loader.py` 实现（P0）；evals 落地（Step 3）；空 md 删除或补内容 |
| P2-5 | 无 lint/format/类型检查配置 | venv 未装 ruff/mypy（已确认），无 `[tool.ruff]`/`[tool.mypy]`/`[tool.pytest.ini_options]` | dev 依赖加 `ruff`，`pyproject.toml` 配置 `line-length`/`target-version=py313`；`[tool.pytest.ini_options] testpaths=["tests"]` |
| P2-6 | 无可观测性 | 全仓无 `logging`；`langsmith 0.12.5` 已装但未配置；`docs/architecture.md` 原则 3 要求可见 | `runtime/runner.py` 加结构化日志；`.env.example` 增 `LANGSMITH_TRACING/LANGSMITH_API_KEY/LANGSMITH_PROJECT` 说明（可选启用） |
| P2-7 | 文档与代码漂移 | `README.md` 仍写 `python src/main.py`、`src/config.py`；`AGENTS.md` 结构段未包含 `src/aila/` 包、`tools/`、`prompts/`、`runtime/`、`pyproject.toml`；`docs/architecture.md` 与真实模块图不符 | 三份文档统一更新：入口改 `python -m aila.main`；结构段补全六层；`architecture.md` 换成实际模块图与本报告的 §4.2 |
| P2-8 | `egg-info` 陈旧 | `SOURCES.txt` 只列 `__init__/agent/config/main`（早于 `tools/`、`runtime/`、`prompts/`） | 属构建产物（已被 `.gitignore` 忽略），补完打包配置后重建即可 |

---

## 6. 需要调整的地方（架构层面）

### 6.1 目标结构（在现有六层上"补边界"，不推翻）

```
src/aila/
├─ config.py            [配置]   唯一 env 读取点；PROJECT_ROOT；fail-fast
├─ prompts/
│   ├─ __init__.py      新增：声明包（避免隐式命名空间）
│   ├─ loader.py        实现：load_system_prompt() 带缓存 + importlib.resources
│   └─ system.md        资产：随包分发（package-data）
├─ tools/
│   ├─ __init__.py      改为导出注册表：TOOLS = [calculator]
│   ├─ calculator.py    能力：保持 AST 白名单
│   └─ (future) knowledge_search.py / web_search.py …
├─ agent.py             [组装]   build_llm() + build_agent()，只依赖 config/prompts/tools
├─ runtime/
│   ├─ __init__.py      新增
│   ├─ runner.py        [执行]   run_agent(agent, message) -> AIMessage
│   │                            + logging / timeout / retry / (future) stream
│   └─ (future) memory.py       checkpointer / thread_id 管理
└─ main.py              [交互]   CLI：--message/--once + 工具轨迹展示 + EOF 保护
```

### 6.2 五条关键调整

1. **补齐"上下文资产"这条链（P0）**：`prompts/loader.py` 必须存在实现，`agent.py` 通过它拿 system prompt；提示词继续留在 `.md`（数据化）是正确决策，坚持下去。
2. **把"层间契约"写死**：`runtime/runner.py` 明确 `run_agent(agent, message) -> AIMessage`；`main.py` 只依赖该契约；未来要换执行方式（流式/多轮/带重试）时只改 runtime，不动 main 与 agent。
3. **工具用注册表，别在 agent 里列清单**：`tools/__init__.py` → `TOOLS = [calculator]`，`agent.py` 写 `tools=TOOLS`。这样"加一个工具"= 新增一个文件 + 在注册表加一行，符合 AGENTS.md「Modular design」。
4. **配置面收口**：把 `temperature` 也交给 `config.py`（`TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))`），让"模型行为"全部可从 `.env` 调；`.env.example` 同步补齐。
5. **拆开"组装"以便离线测试**：`build_llm()` 与 `build_agent()` 分离，测试可注入 `langchain_core.language_models.fake_chat_models` 的假模型 → 无网、无 key 也能测试 `runtime` 与 `agent`。

### 6.3 建议的层间契约（可直接照抄）

```python
# runtime/runner.py  （目标形态，示意）
def run_agent(agent, message: str) -> AIMessage:
    """把一条用户消息交给 agent，返回最后一条 AIMessage。"""
```

`main.py` 侧：

```python
response = run_agent(agent, user_input)   # AIMessage
print(response.content)
```

即：**唯一允许知道 LangGraph 状态形状（`state["messages"]`）的地方就是 `runtime/runner.py`。**

---

## 7. 下一阶段开发路线

> 排序原则：**先恢复可运行 → 再补可复现地基 → 再上能力**。每一步都给出"验收标准"，全部可命令化验证（符合 AGENTS.md 「Add evaluation cases」与 product_spec 的 Harness Engineering）。

### Step 0　修复并使项目重新可运行（半天，最高优先）

| 任务 | 产出 |
| --- | --- |
| 实现 `prompts/loader.py::load_system_prompt()` | 带缓存、`importlib.resources` 优先、磁盘回退 |
| `agent.py` 接入 loader（消除 `system_prompt`） | 一行 import + 一处调用 |
| 提交当前 WIP（`agent.py` / `system.md` / `loader.py`） | 一次语义化提交，避免"工作区长期脏" |
| 修正 `agent.py` 缩进与降级为规范风格 | 与 `config.py`/`main.py` 一致 |

**验收**：`cd <repo>` → `python -m aila.main` 进入对话并能回答；`python -c "from aila.agent import create_agent; print(type(create_agent()))"` 无异常。

### Step 1　工程地基（1 天）

| 任务 | 说明 |
| --- | --- |
| 依赖单一真相 | `pyproject.toml` 为唯一来源；`requirements.txt` 重写为 UTF-8(no BOM) 或删除；README 改为 `pip install -e .` |
| dev 依赖 | `[project.optional-dependencies] dev = ["pytest","ruff"]`；`pip install -e ".[dev]"` |
| 打包修复 | `[tool.setuptools.packages.find] where=["src"]` + `package-data aila.prompts=["*.md"]` + `runtime/`、`prompts/` 补 `__init__.py` |
| 入口脚本 | `[project.scripts] aila = "aila.main:main"` → 可直接 `aila` 启动 |
| 测试地基 | `tests/conftest.py`（注入测试环境变量）、`[tool.pytest.ini_options] testpaths=["tests"]` |
| 测试补齐 | `tests/test_config.py`（PROJECT_ROOT/缺变量报错）、`tests/test_tools_calculator.py`（`_evaluate` 与 `@tool` 边界）、`tests/test_runner.py`（用假模型，离线） |
| 文档同步 | 更新 `README.md`、`AGENTS.md`、`docs/architecture.md`（P2-7） |

**验收**：`python -m pytest -q` 通过（≥8 个用例、无网络依赖）；`pip install -e ".[dev]"` 成功；`python -m aila.main -m "1+1"`（Step 2 后）可非交互运行。

### Step 2　运行时增强：可观测 + 记忆 + 好用的 CLI（2–3 天）

| 任务 | 对应价值 |
| --- | --- |
| `runtime/runner.py`：logging、异常包装、（可选）timeout/retry、类型注解 | 可观测（`architecture.md` 原则 3） |
| 多轮记忆：LangGraph `InMemorySaver` + `thread_id`（`graph.invoke(..., config={"configurable":{"thread_id":...}})`），或 `runtime/memory.py` | 让"学习助手"能连续追问（product_spec Phase 1 的自然延伸） |
| `main.py`：`-m/--message`、`--once`、`EOF`/`Ctrl+C` 保护、打印 `tool` 调用轨迹 | 可自动化验证 + 学习可见性 |
| 迁移到 `langchain.agents.create_agent`（P1-1） | 去掉 V1 弃用警告，避免 V2 断裂 |
| `temperature` 入 `config.py` | 配置收口 |

**验收**：可 `python -m aila.main -m "记住我叫X"` 后二次调用仍记得（记忆生效）；日志中能看到一次工具调用的完整轨迹；运行期无弃用警告（`-W error::DeprecationWarning` 下仍通过）。

### Step 3　评测闭环（3–5 天）—— 这是 harness 的核心欠账

| 任务 | 产出 |
| --- | --- |
| `evals/datasets/basic_questions.json` | 15–25 条用例，分三类：知识问答、工具调用（如"123*456 等于几"）、拒答/不确定性（"训练数据截止何时"应承认不确定） |
| `evals/graders/answer_quality.py` | 规则判分器：① 期望数字/关键词 ② 是否调用期望工具（`tool_calls` 轨迹）③ 是否出现禁用词/幻觉声明 |
| `evals/run.py`（或 pytest 参数化） | 一条命令跑全部用例并输出通过率 + 明细（可写入 `docs/eval_report.md`） |
| 基线记录 | 把首次跑分写进 docs，后续每次改动对比（回归测试） |

**验收**：`python -m evals.run`（或 `pytest -m eval`）输出通过率 ≥ 基线，且**不通过时可定位到具体用例**。

### Step 4　RAG 最小闭环：让助手检索自己的笔记（1 周）

> 目标很具体：**用 AILA 检索 `knowledge/` 里自己的学习笔记**（dogfooding），方法与素材都已在笔记里（`04知识库搭建/01_数据解析与递归切片.md`、`02_混合检索与高收益重排.md`）。

| 任务 | 说明 |
| --- | --- |
| 装载器 | 递归扫描 `knowledge/**/*.md`（全部 UTF-8 无 BOM + LF，已实测；注意含空格/全角符号的目录名） |
| 切片 | 递归切片（按 `#` 标题层级 + 长度上限），保留 `source` 与标题路径元数据（笔记 `01_数据解析与递归切片`） |
| 索引 | 向量库选型（Chroma / FAISS / 本地 …）——**新增依赖需按 AGENTS.md 原则说明理由**；先做"最小可用"再谈 rerank |
| 工具化 | `tools/knowledge_search.py` → 注册进 `TOOLS`，让 agent 自己决定何时检索 |
| 评测 | evals 增加"检索命中"类用例（问题→期望文件名/标题） |

**验收**：`python -m aila.main -m "递归切片要注意什么"` 的回答能引用 `04知识库搭建/01_数据解析与递归切片.md` 的内容（并在输出中显示检索到的来源）。

### Step 5　产品化能力（product_spec Phase 2–3，持续）

- MCP 工具接入（AGENTS.md 技术栈已列 "MCP (future)"）
- 联网检索"最新 AI 信息"（product_spec 目标之一）→ `tools/web_search.py`
- 学习计划生成 + 进度管理（product_spec Phase 2/3）
- 可观测性：启用 LangSmith tracing（或本地日志聚合）
- CI：在无密钥环境下跑 `pytest`（靠 conftest 假变量）+ 跑 eval（需密钥时单独 job）

---

## 8. 工程规范建议（对齐 AGENTS.md / Harness Engineering）

| 规范 | 现状 | 建议 |
| --- | --- | --- |
| 简单架构 | ✅ 六层极简，无过度设计 | 保持；新增能力前先问"能不能放进现有层" |
| 模块化 | ✅ `tools/` 已模块化 | 让"注册表"成为唯一扩展点（§6.2-3） |
| 可读 Python | ⚠ 风格不统一（`runner.py` 压平、`agent.py` 缩进错位） | 统一：模块/函数 docstring、类型注解、CRLF 与"函数体首行留空"沿用仓库既有风格；引入 `ruff format` + `ruff check` |
| 文档决策 | ⚠ 三份文档漂移 | 规定：改代码的同一次提交里更新 `docs/`；重大决策追加 ADR（如"为什么 prompt 放 .md"、"为什么 runtime 单独成层"） |
| 避免无谓依赖 | ✅ 直接依赖只有 4 个 | 向量库/检索等新依赖要写理由（ADR） |
| 小函数 | ✅ `_evaluate` 等拆分合理 | `create_agent()` 可再拆 `build_llm()`/`build_agent()` |
| 评测用例 | ❌ 未开始 | Step 3 完成；这是 AGENTS.md 明确要求、也是 docs/architecture.md 的"Every capability should have evaluation" |
| 可复现 | ⚠ dev 依赖未声明、lock 不完整 | Step 1 完成；CI 用 lock 安装 |

**建议的"改代码同提交"检查单**（写进 `AGENTS.md` 的 Workflow 段）：

1. `ruff check .` 与 `ruff format --check .` 通过
2. `python -m pytest -q` 通过
3. 若改了提示词/工具/模型参数 → 跑一次 `evals` 并记录结果
4. 若改了目录结构/入口 → 同步更新 `README.md` + `docs/architecture.md`
5. 不在提交里包含 `.env`、`__pycache__`、`egg-info`

---

## 9. 复现本报告的证据（可复制执行）

```powershell
cd e:\06_ai_learning_assistant
$py = ".\.venv\Scripts\python.exe"

# 1) P0：入口崩溃
'hi','exit' | & $py -m aila.main          # → NameError: name 'system_prompt' is not defined (exit 1)

# 2) 链路各层是否可用
& $py -c "from aila.agent import create_agent; create_agent()"                  # → NameError（P0）
& $py -c "from aila.tools import calculator; print(calculator.invoke({'expression':'123*456'}))"  # → 56088

# 3) P1-1：弃用警告
& $py -W always -c "from langgraph.prebuilt import create_react_agent"          # → LangGraphDeprecatedSinceV10

# 4) P1-3：打包是否含 system.md（对副本构建，项目零改动）
robocopy . $env:TEMP\aila_pkgtest /E /XD .venv .git .pytest_cache | Out-Null
& $py -m pip wheel $env:TEMP\aila_pkgtest --no-deps -w $env:TEMP\aila_pkgtest\dist
& $py -c "import zipfile,glob;print([n for n in zipfile.ZipFile(glob.glob(r'$env:TEMP\aila_pkgtest\dist\*.whl')[0]).namelist()])"

# 5) P1-4：依赖与 dev 环境
& $py -m pip install --dry-run --no-index --no-deps -r requirements.txt   # pip 26 可读 UTF-16（exit 0）
& $py -c "import setuptools"                                              # → ModuleNotFoundError（venv 未装）

# 6) 知识库资产扫描（编码/行尾/标题）
& $py -c "import os;print(sum(1 for r,d,f in os.walk('knowledge') for x in f if x.endswith('.md')))"
```

**本轮审查的只读性声明**：以上命令均未写入项目目录（第 4 项在 `%TEMP%` 的副本上构建）；`pytest` 也以 `-p no:cacheprovider` 运行以避免写缓存。唯一新增文件是本报告 `docs/architecture_review.md`。

---

## 10. 结论

1. **模块职责总体是清晰的**：`config / agent / runtime / tools / prompts / main` 六层划分正确、无循环依赖、无越层 import，方向完全符合 AGENTS.md 的"简单 + 模块化"。上一轮把"模型调用"收口到 `runtime/runner.py`、把"工具"独立成 `tools/` 的两步重构，是本项目目前最重要的架构成果。
2. **但当前处于"不可运行"状态**：`agent.py` 引用了从未装载的 `system_prompt`，而承担装载职责的 `prompts/loader.py` 是 0 字节空文件。这是唯一的功能性阻断，属于"半成品 WIP"，修复量是分钟级。
3. **架构本身已被证明可行**：内存复现实测 `llm + calculator + system.md` 端到端跑通（`human→ai→tool→ai`，结果 `56088`）。也就是说，**问题在装配，不在设计**。
4. **需要调整的重点不在"拆更多层"，而在"把已有的层补完整"**：① 补 prompt 装载 ② 把层间契约写成签名与文档 ③ 工具走注册表 ④ 打包声明 package-data ⑤ 依赖单一真相 + dev 依赖 ⑥ 文档与代码同提交。
5. **下一阶段的正确顺序**：Step 0 修复 → Step 1 地基 → Step 2 运行时(记忆/观测/CLI) → **Step 3 评测（当前最大欠账，AGENTS.md 原则 5 与 Harness Engineering 的硬要求）** → Step 4 用 `knowledge/` 做 RAG 最小闭环（素材与方法都已经在自己的笔记里）→ Step 5 MCP/联网/学习计划。
6. **两条安全事项请优先处理**：`.env` 中的真实 API Key 应尽快轮换；`.env.example` 补 DashScope 示例，避免后续误提交。

> 报告结束。如需把本报告合并进 `docs/architecture.md`（使其成为唯一的架构文档），或直接按 Step 0 开始实施修复，请告知。
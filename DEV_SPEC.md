# Prime Code Agent Runtime MVP Development Specification

## 1. 项目概述

**项目定位**

Prime Code Agent Runtime MVP 是一个本地 CLI-first 的 Fake Runtime 验证项目。用户在任意项目文件夹中打开 shell，输入 `prime` 后进入类似 Claude Code / Codex 的交互式 REPL。用户输入自然语言任务后，系统通过 FakeModel 固定产生 JSON 格式的 `AgentDecision`，依次调用 FakeTools，完成一个可观测、可测试、可回放的 single agent runtime 闭环。

本项目不是完整的 Claude Code / Codex，也不是通用代码生成产品。MVP 的目标是验证 agent runtime 的骨架，而不是验证真实模型能力、真实代码修改能力或复杂多智能体协作能力。

**MVP 目标**

- 验证从 REPL 输入到最终回答的 agentic loop。
- 验证模型到 Runtime 之间只通过 JSON `AgentDecision` 交互。
- 验证工具系统抽象，包括 `BaseTool`、`ToolSpec`、`ToolRegistry`、`ToolExecutor`、`PermissionPolicy`。
- 验证 FakeTools 的调用顺序、Observation 回填和停止条件。
- 验证 checkpoint、trace、turn report 的最小闭环。
- 验证非法 JSON、未知工具、权限拒绝等基础失败路径。

**MVP 明确非目标**

- 不调用真实大模型。
- 不实现真实文件读取、真实补丁应用、真实测试运行或真实 shell 命令执行。
- 不读写用户真实项目文件。
- 不实现 Multi-Agent、SubAgent、AgentTeam、CoderAgent、VerifierAgent 或 SequentialAgentTeam。
- 不实现 VS Code 插件。
- 不实现 MCP Server。
- 不实现 Dashboard。
- 不实现真实远程服务、账号系统或云端同步。

**开发守则**

- Thinking：每轮任务必须能记录用户目标、决策摘要、工具观察和停止原因；不要保存模型完整隐藏思维，只保存面向调试的摘要。
- Framework：所有能力必须落到明确模块，不把路由、模型、工具执行、checkpoint 和输出格式混在同一个函数里。
- Checkpoint：每轮必须覆盖 `turn_start`、`pre_tool`、`post_tool`、`turn_end` 四类 checkpoint。
- Debugging：即使是 fake demo，也必须能通过 trace 和 JSONL 记录复盘基本过程。
- Context：只装配最小必要上下文；MVP 不扫描真实项目，不读取真实文件树，不把真实代码内容放入模型上下文。

## 2. 核心特点

- `prime` 是唯一 CLI 入口。用户先进入某个项目文件夹，然后在 shell 中输入 `prime`。
- `prime` 启动后进入 REPL，并展示当前 workspace，例如：

  ```text
  Prime Code Agent
  workspace: /current/folder

  >
  ```

- REPL MVP 只支持 `/exit` 内置命令，用于退出交互循环。
- 暂不实现 `/help`、`/status`、`/trace`、`/resume`、`/config`。
- `SessionRouter` 负责识别 REPL 输入是内置命令还是普通任务。
- `InputProcessor` 将用户自然语言输入转换为 `TaskSpec`。
- `ContextAssembler` 只装配 fake runtime 所需的最小上下文，不读取真实项目文件。
- `FakeModel` 对任意非 `/exit` 输入走同一个固定脚本：

  ```text
  fake_read_file
  -> fake_apply_patch
  -> fake_run_tests
  -> final_answer
  ```

- `FakeModel` 每一步输出必须是 JSON 字符串，Runtime 再解析为 `AgentDecision`。
- MVP 支持的 `AgentDecision.decision_type` 只有 `tool_call` 和 `final_answer`。
- MVP 不支持 `ask_user` 或 `delegate_to_subagent`。
- Tool 层先实现抽象骨架和 FakeTools：`FakeReadFileTool`、`FakeApplyPatchTool`、`FakeRunTestsTool`。
- `PermissionPolicy` 在 MVP 中仍必须存在，用于证明真实工具接入前已经有权限检查位置。
- `Agentic Loop` 负责按 FakeModel 决策驱动工具执行、Observation 回填、停止条件判断和最终回答。
- `Checkpoint` 必须按顺序记录：

  ```text
  用户输入任务
  -> turn_start checkpoint
  -> fake_read_file 前 pre_tool checkpoint
  -> fake_read_file 后 post_tool checkpoint
  -> fake_apply_patch 前 pre_tool checkpoint
  -> fake_apply_patch 后 post_tool checkpoint
  -> fake_run_tests 前 pre_tool checkpoint
  -> fake_run_tests 后 post_tool checkpoint
  -> final_answer
  -> turn_end checkpoint
  ```

- `Trace` 用 JSONL 保存关键 runtime 事件，便于调试和 replay 基础过程。
- `TurnReport` 汇总每轮任务的输入、工具调用、checkpoint id、最终回答和停止原因。
- MVP 只实现 Single Agent Runtime，明确不实现 Multi-Agent。

## 3. 技术选型

- 语言版本：Python 3.11+。
- CLI：Typer，用于定义 `prime` 命令入口。
- 终端输出：Rich，用于 REPL banner、状态提示和错误展示。
- 数据校验：Pydantic，用于 `TaskSpec`、`AgentDecision`、`ToolResult`、`Checkpoint`、`TurnReport` 等数据契约。
- 配置格式：YAML。
- 测试框架：pytest。
- 存储格式：JSONL，用于 checkpoint、trace 和 turn report。
- 模型客户端：`FakeModelClient`。真实模型客户端只保留 Future 设计，不进入 MVP 实现排期。
- 包管理工具不强行指定；如果项目已有 `pyproject.toml`、锁文件或虚拟环境约定，则遵循现有项目。
- 建议配置文件：`config/settings.yaml`。
- 建议 prompt 文件：
  - `config/prompts/router.txt`
  - `config/prompts/agent_decision.txt`
  - `config/prompts/finalizer.txt`
- 建议数据目录：
  - `data/checkpoints/checkpoints.jsonl`
  - `data/traces/traces.jsonl`
  - `data/reports/turn_reports.jsonl`
- MVP 禁止引入真实模型 SDK 作为必需依赖。
- MVP 禁止引入执行真实 shell、修改真实文件或访问真实项目内容的工具实现。

## 4. 测试方案

**单元测试**

- `settings`：验证 YAML 配置加载、默认值、缺失字段和非法字段。
- `router`：验证 `/exit` 被识别为退出命令，普通文本被识别为任务。
- `input_processor`：验证自然语言输入转换为 `TaskSpec`，并包含 workspace、turn id、原始输入。
- `context_assembler`：验证只装配最小 fake context，不读取真实文件。
- `fake_model`：验证任意任务都返回固定脚本中的下一步 JSON。
- `agent_decision_parser`：验证合法 JSON 被解析，非法 JSON 被拒绝。
- `decision_validator`：验证只允许 `tool_call` 和 `final_answer`，未知工具或缺失字段被拒绝。
- `tool_registry`：验证 FakeTools 注册、查找、重复注册和未知工具错误。
- `tool_executor`：验证执行前调用权限策略，执行后返回标准 `ToolResult`。
- `permission_policy`：验证 fake 工具默认允许，未知或未来真实工具默认拒绝。
- `fake_tools`：验证 `fake_read_file`、`fake_apply_patch`、`fake_run_tests` 返回固定 observation。
- `checkpoint_store`：验证四类 checkpoint 写入 JSONL，字段完整且顺序可检查。
- `trace_logger`：验证关键事件以 JSONL 追加写入。
- `stop_conditions`：验证 final answer、最大步数和错误状态的停止判断。
- `turn_finalizer`：验证生成 `TurnReport`，并记录最终回答和停止原因。

**集成测试**

- FakeModel + FakeTools 跑完整固定脚本。
- 每一步 checkpoint 是否完整，包括 `turn_start`、每个工具前后的 `pre_tool` / `post_tool`、`turn_end`。
- `AgentDecision` 非法 JSON 是否被拒绝并转为可诊断错误。
- 未注册工具是否被拒绝。
- 权限策略拒绝时是否停止工具执行并记录 trace。
- `/exit` 是否能退出 REPL，不生成普通任务 turn。

**E2E 测试**

- 启动 `prime`。
- 输入任意非 `/exit` 任务。
- 完成 `fake_read_file -> fake_apply_patch -> fake_run_tests -> final_answer`。
- 生成 turn report、checkpoint 和 trace。
- 输入 `/exit` 后进程正常退出。

**测试边界**

- 所有测试不允许访问真实模型。
- 所有测试不允许修改真实项目文件。
- 所有测试不允许执行真实 shell 命令。
- E2E 测试如需验证文件输出，只能写入测试隔离目录下的 fake JSONL 数据。
- 测试命令统一使用 `pytest`，具体任务可按模块范围收敛到 `pytest tests/unit/...`、`pytest tests/integration/...`、`pytest tests/e2e/...`。

## 5. 系统架构与模块设计

**整体架构图**

```text
shell
  |
  v
prime CLI
  |
  v
REPL
  |
  v
SessionRouter
  |---------------------> /exit -> exit
  |
  v
InputProcessor -> TaskSpec
  |
  v
CheckpointStore(turn_start)
  |
  v
ContextAssembler
  |
  v
FakeModelClient -> JSON string
  |
  v
AgentDecisionParser -> DecisionValidator
  |
  v
AgentLoop
  |
  +--> CheckpointStore(pre_tool)
  +--> ToolExecutor -> PermissionPolicy -> ToolRegistry -> FakeTool
  +--> CheckpointStore(post_tool)
  +--> TraceLogger
  +--> StopConditionChecker
  |
  v
TurnFinalizer -> TurnReport -> REPL output
  |
  v
CheckpointStore(turn_end)
```

**建议目录结构**

```text
prime-code-agent/
|-- config/
|   |-- settings.yaml
|   `-- prompts/
|       |-- router.txt
|       |-- agent_decision.txt
|       `-- finalizer.txt
|
|-- src/
|   `-- prime/
|       |-- __init__.py
|       |-- cli/
|       |   |-- __init__.py
|       |   `-- main.py
|       |-- core/
|       |   |-- __init__.py
|       |   |-- settings.py
|       |   |-- types.py
|       |   `-- errors.py
|       |-- routing/
|       |   |-- __init__.py
|       |   `-- session_router.py
|       |-- input_processing/
|       |   |-- __init__.py
|       |   `-- input_processor.py
|       |-- context/
|       |   |-- __init__.py
|       |   `-- context_assembler.py
|       |-- model/
|       |   |-- __init__.py
|       |   |-- base_client.py
|       |   `-- fake_model.py
|       |-- runtime/
|       |   |-- __init__.py
|       |   |-- agent_loop.py
|       |   |-- decision.py
|       |   |-- decision_validator.py
|       |   |-- observation.py
|       |   |-- stop_conditions.py
|       |   `-- turn_finalizer.py
|       |-- tools/
|       |   |-- __init__.py
|       |   |-- base_tool.py
|       |   |-- registry.py
|       |   |-- executor.py
|       |   |-- permissions.py
|       |   `-- fake_tools.py
|       |-- checkpoint/
|       |   |-- __init__.py
|       |   |-- checkpoint_models.py
|       |   `-- checkpoint_store.py
|       `-- observability/
|           |-- __init__.py
|           |-- trace_context.py
|           |-- jsonl_logger.py
|           `-- trace_reader.py
|
|-- data/
|   |-- checkpoints/
|   |-- traces/
|   `-- reports/
|
|-- tests/
|   |-- unit/
|   |-- integration/
|   `-- e2e/
|
|-- pyproject.toml
|-- README.md
`-- DEV_SPEC.md
```

**核心数据契约**

- `TaskSpec`：表示一轮用户任务，至少包含 `turn_id`、`workspace`、`raw_input`、`created_at`。
- `RouteResult`：表示 REPL 输入路由结果，至少包含 `route_type`、`command`、`payload`。
- `AgentDecision`：表示模型给 Runtime 的动作决策，至少包含 `decision_type`、`thought_summary`、`action`、`expected_observation`、`final_answer`。
- `ToolCall`：表示一次工具调用，至少包含 `tool_name`、`args`。
- `ToolResult`：表示工具结果，至少包含 `tool_name`、`success`、`observation`、`error`。
- `ToolSpec`：表示工具元数据，至少包含 `name`、`description`、`args_schema`、`is_fake`。
- `Checkpoint`：表示持久化检查点，至少包含 `checkpoint_id`、`turn_id`、`checkpoint_type`、`step_index`、`payload`、`created_at`。
- `TurnReport`：表示一轮任务报告，至少包含 `turn_id`、`user_input`、`tool_calls`、`checkpoint_ids`、`final_answer`、`stop_reason`。
- `RuntimeState`：表示 agent loop 内部状态，至少包含 `turn_id`、`step_index`、`task`、`observations`、`last_decision`、`stop_reason`。

**模块职责**

- `prime.cli.main`：定义 `prime` CLI 入口，启动 REPL。
- `prime.routing.session_router`：识别 `/exit` 和普通任务。
- `prime.input_processing.input_processor`：生成 `TaskSpec`。
- `prime.context.context_assembler`：生成 FakeModel 所需最小上下文。
- `prime.model.base_client`：定义模型客户端协议和 `ModelResponse`。
- `prime.model.fake_model`：实现固定脚本 JSON 决策。
- `prime.runtime.decision`：定义 `AgentDecision`、`ToolCall` 和 parser。
- `prime.runtime.decision_validator`：校验决策类型、工具名和参数。
- `prime.runtime.agent_loop`：编排模型、工具、checkpoint、trace 和停止条件。
- `prime.runtime.observation`：统一工具 observation 回填结构。
- `prime.runtime.stop_conditions`：判断 final answer、最大步数和错误停止。
- `prime.runtime.turn_finalizer`：生成 `TurnReport`。
- `prime.tools.base_tool`：定义 `BaseTool` 和 `ToolSpec`。
- `prime.tools.registry`：注册和查找 FakeTools。
- `prime.tools.permissions`：提供权限检查位置。
- `prime.tools.executor`：执行工具并返回 `ToolResult`。
- `prime.tools.fake_tools`：提供三个 fake 工具实现。
- `prime.checkpoint.checkpoint_store`：写入 checkpoint JSONL。
- `prime.observability.jsonl_logger`：写入 trace 和 report JSONL。

**架构限制**

- 不加入 SubAgent / AgentTeam 数据结构。
- 不加入真实文件工具的数据契约。
- 不加入 MCP Server 数据契约。
- 不让 FakeTools 访问真实文件系统、真实 shell 或真实测试命令。

## 6. 项目排期

**阶段 A：工程骨架与 CLI REPL**

| 状态 | 任务 | 目标 | 修改文件 | 实现类 / 函数 | 验收标准 | 测试方法 |
| --- | --- | --- | --- | --- | --- | --- |
| [x] | A1 | 初始化 Python 项目骨架和基础目录 | `pyproject.toml`, `src/prime/__init__.py`, `tests/unit/`, `tests/integration/`, `tests/e2e/`, `config/settings.yaml` | 项目包声明和基础配置 | `src/prime` 可被导入，pytest 可发现测试目录 | `pytest` |
| [ ] | A2 | 实现 `prime` CLI 入口 | `src/prime/cli/main.py`, `pyproject.toml` | `app`, `main()` | 安装后可执行 `prime`，启动时显示产品名和 workspace | `pytest tests/unit/cli` |
| [ ] | A3 | 实现 REPL 与 `/exit` | `src/prime/cli/main.py`, `src/prime/routing/session_router.py` | `run_repl()`, `SessionRouter.route()` | 输入 `/exit` 正常退出；普通输入进入任务路径占位 | `pytest tests/unit/routing`; `pytest tests/e2e/test_exit.py` |

**阶段 B：核心类型与配置**

| 状态 | 任务 | 目标 | 修改文件 | 实现类 / 函数 | 验收标准 | 测试方法 |
| --- | --- | --- | --- | --- | --- | --- |
| [ ] | B1 | 定义核心 Pydantic 类型 | `src/prime/core/types.py`, `src/prime/runtime/decision.py`, `src/prime/tools/base_tool.py`, `src/prime/checkpoint/checkpoint_models.py` | `TaskSpec`, `RouteResult`, `AgentDecision`, `ToolCall`, `ToolResult`, `ToolSpec`, `Checkpoint`, `TurnReport`, `RuntimeState` | 数据契约字段完整，非法字段或缺失字段能被测试覆盖 | `pytest tests/unit/core tests/unit/runtime` |
| [ ] | B2 | 实现 settings 加载 | `src/prime/core/settings.py`, `config/settings.yaml` | `Settings`, `load_settings()` | 默认路径可加载，缺失配置有明确错误 | `pytest tests/unit/core/test_settings.py` |
| [ ] | B3 | 实现错误类型 | `src/prime/core/errors.py` | `PrimeError`, `DecisionParseError`, `DecisionValidationError`, `ToolExecutionError`, `CheckpointError` | Runtime 可用统一异常表达错误状态 | `pytest tests/unit/core/test_errors.py` |

**阶段 C：路由、输入处理、上下文装配**

| 状态 | 任务 | 目标 | 修改文件 | 实现类 / 函数 | 验收标准 | 测试方法 |
| --- | --- | --- | --- | --- | --- | --- |
| [ ] | C1 | 完成 SessionRouter | `src/prime/routing/session_router.py` | `SessionRouter.route()` | `/exit` 返回 command route；其他内容返回 task route | `pytest tests/unit/routing/test_session_router.py` |
| [ ] | C2 | 实现 InputProcessor | `src/prime/input_processing/input_processor.py` | `InputProcessor.process()` | 为普通输入生成 `TaskSpec`，包含 workspace、turn id、原始输入 | `pytest tests/unit/input_processing/test_input_processor.py` |
| [ ] | C3 | 实现 ContextAssembler | `src/prime/context/context_assembler.py` | `ContextAssembler.assemble()` | 只包含 fake runtime 所需字段，不读取真实项目文件 | `pytest tests/unit/context/test_context_assembler.py` |

**阶段 D：FakeModel 与 JSON 决策**

| 状态 | 任务 | 目标 | 修改文件 | 实现类 / 函数 | 验收标准 | 测试方法 |
| --- | --- | --- | --- | --- | --- | --- |
| [ ] | D1 | 定义模型客户端协议 | `src/prime/model/base_client.py` | `BaseModelClient`, `ModelResponse` | AgentLoop 可通过抽象调用模型 | `pytest tests/unit/model/test_base_client.py` |
| [ ] | D2 | 实现 FakeModel 固定脚本 | `src/prime/model/fake_model.py` | `FakeModelClient.next_decision()` | 任意任务按 step 返回 `fake_read_file`、`fake_apply_patch`、`fake_run_tests`、`final_answer` JSON | `pytest tests/unit/model/test_fake_model.py` |
| [ ] | D3 | 实现 AgentDecisionParser | `src/prime/runtime/decision.py` | `AgentDecisionParser.parse()` | 合法 JSON 转为 `AgentDecision`；非法 JSON 抛出 `DecisionParseError` | `pytest tests/unit/runtime/test_decision_parser.py` |
| [ ] | D4 | 实现 DecisionValidator | `src/prime/runtime/decision_validator.py` | `DecisionValidator.validate()` | 只允许 `tool_call` 和 `final_answer`，未知工具或缺失 action 被拒绝 | `pytest tests/unit/runtime/test_decision_validator.py` |

**阶段 E：工具系统与 FakeTools**

| 状态 | 任务 | 目标 | 修改文件 | 实现类 / 函数 | 验收标准 | 测试方法 |
| --- | --- | --- | --- | --- | --- | --- |
| [ ] | E1 | 实现工具抽象 | `src/prime/tools/base_tool.py` | `BaseTool`, `ToolSpec` | 每个工具能暴露 spec 并接收 args 返回 `ToolResult` | `pytest tests/unit/tools/test_base_tool.py` |
| [ ] | E2 | 实现 ToolRegistry | `src/prime/tools/registry.py` | `ToolRegistry.register()`, `ToolRegistry.get()` | 可注册 FakeTools，重复注册和未知工具有明确错误 | `pytest tests/unit/tools/test_registry.py` |
| [ ] | E3 | 实现 PermissionPolicy | `src/prime/tools/permissions.py` | `PermissionPolicy.check()` | fake 工具允许，未知或未来真实工具默认拒绝 | `pytest tests/unit/tools/test_permissions.py` |
| [ ] | E4 | 实现 ToolExecutor | `src/prime/tools/executor.py` | `ToolExecutor.execute()` | 执行前检查权限，执行后返回标准 `ToolResult` | `pytest tests/unit/tools/test_executor.py` |
| [ ] | E5 | 实现三个 FakeTools | `src/prime/tools/fake_tools.py` | `FakeReadFileTool`, `FakeApplyPatchTool`, `FakeRunTestsTool` | 三个工具返回固定 observation，不读写真实文件，不执行真实命令 | `pytest tests/unit/tools/test_fake_tools.py` |

**阶段 F：Checkpoint 与 Trace**

| 状态 | 任务 | 目标 | 修改文件 | 实现类 / 函数 | 验收标准 | 测试方法 |
| --- | --- | --- | --- | --- | --- | --- |
| [ ] | F1 | 定义 Checkpoint 模型 | `src/prime/checkpoint/checkpoint_models.py` | `Checkpoint`, `CheckpointType` | 支持 `turn_start`、`pre_tool`、`post_tool`、`turn_end` | `pytest tests/unit/checkpoint/test_checkpoint_models.py` |
| [ ] | F2 | 实现 CheckpointStore | `src/prime/checkpoint/checkpoint_store.py` | `CheckpointStore.save()` | checkpoint 追加写入 JSONL，返回 checkpoint id | `pytest tests/unit/checkpoint/test_checkpoint_store.py` |
| [ ] | F3 | 接入 turn_start / turn_end | `src/prime/runtime/agent_loop.py`, `src/prime/runtime/turn_finalizer.py` | `save_turn_start()`, `save_turn_end()` | 每轮任务开始和结束都有 checkpoint | `pytest tests/integration/test_turn_checkpoints.py` |
| [ ] | F4 | 接入 pre_tool / post_tool | `src/prime/runtime/agent_loop.py` | `save_pre_tool()`, `save_post_tool()` | 每次 FakeTool 调用前后都有 checkpoint | `pytest tests/integration/test_tool_checkpoints.py` |
| [ ] | F5 | 实现 TraceContext / JSONL Logger | `src/prime/observability/trace_context.py`, `src/prime/observability/jsonl_logger.py`, `src/prime/observability/trace_reader.py` | `TraceContext`, `JsonlLogger.write()`, `TraceReader.read_turn()` | 关键 runtime 事件可追加写入并按 turn 读取 | `pytest tests/unit/observability` |

**阶段 G：Agentic Loop 与 TurnReport**

| 状态 | 任务 | 目标 | 修改文件 | 实现类 / 函数 | 验收标准 | 测试方法 |
| --- | --- | --- | --- | --- | --- | --- |
| [ ] | G1 | 实现 RuntimeState 与停止条件 | `src/prime/runtime/stop_conditions.py`, `src/prime/core/types.py` | `RuntimeState`, `StopConditionChecker.should_stop()` | final answer、错误状态、最大步数均能停止 | `pytest tests/unit/runtime/test_stop_conditions.py` |
| [ ] | G2 | 实现 AgentLoop 固定脚本闭环 | `src/prime/runtime/agent_loop.py` | `AgentLoop.run_turn()` | 能驱动 FakeModel 和 FakeTools 完成完整闭环 | `pytest tests/integration/test_agent_loop.py` |
| [ ] | G3 | 实现 Observation 回填 | `src/prime/runtime/observation.py`, `src/prime/runtime/agent_loop.py` | `Observation`, `append_observation()` | 每次工具结果进入下一步模型上下文 | `pytest tests/unit/runtime/test_observation.py` |
| [ ] | G4 | 实现 TurnFinalizer | `src/prime/runtime/turn_finalizer.py` | `TurnFinalizer.finalize()` | 生成包含工具调用、checkpoint id、最终回答、停止原因的 `TurnReport` | `pytest tests/unit/runtime/test_turn_finalizer.py` |
| [ ] | G5 | 完成完整集成测试 | `tests/integration/test_fake_runtime_flow.py` | `test_fake_model_fake_tools_full_loop()` | `fake_read_file -> fake_apply_patch -> fake_run_tests -> final_answer` 顺序稳定 | `pytest tests/integration/test_fake_runtime_flow.py` |

**阶段 H：E2E 与文档收口**

| 状态 | 任务 | 目标 | 修改文件 | 实现类 / 函数 | 验收标准 | 测试方法 |
| --- | --- | --- | --- | --- | --- | --- |
| [ ] | H1 | E2E 验证 `prime` 启动与 `/exit` | `tests/e2e/test_prime_exit.py` | `test_prime_exit()` | 子进程启动后输入 `/exit` 正常退出 | `pytest tests/e2e/test_prime_exit.py` |
| [ ] | H2 | E2E 验证任意任务完成 fake loop | `tests/e2e/test_prime_fake_loop.py` | `test_prime_fake_loop()` | 输入任意任务后输出最终回答并生成 JSONL 记录 | `pytest tests/e2e/test_prime_fake_loop.py` |
| [ ] | H3 | 更新 README 运行说明 | `README.md` | 文档示例 | README 包含安装、启动、运行测试、MVP 边界说明 | 人工检查；`pytest` |
| [ ] | H4 | 全链路验收 | `tests/e2e/`, `data/` 测试隔离目录 | 验收脚本或 pytest fixtures | CLI、FakeModel、FakeTools、checkpoint、trace、turn report 全部通过 | `pytest tests/unit tests/integration tests/e2e` |

## 7. 可扩展性与未来展望

以下能力只作为 Future，不进入 MVP 实现范围。

**真实工具集合**

- `read_file`
- `search_text`
- `apply_patch`
- `run_tests`
- `git_diff`
- `git_status`

真实工具接入时必须重新设计权限策略、工作区边界、变更预览、失败回滚和审计记录。MVP 只保留工具抽象位置，不实现这些真实工具。

**真实模型接入**

- OpenAI-compatible API。
- DeepSeek。
- Claude。
- 本地模型。

真实模型接入时必须补充模型配置、密钥管理、超时重试、token 预算、输出修复和更严格的 JSON schema 约束。MVP 只实现 `FakeModelClient`。

**Multi-Agent**

- `SubAgent`
- `AgentTeam`
- `CoderAgent`
- `VerifierAgent`
- `SequentialAgentTeam`
- Manager-Worker 模式。

Multi-Agent 会引入任务分解、上下文隔离、子任务生命周期、跨 agent trace 和结果合并问题，全部放入 Future。

**后续 REPL 命令**

- `/help`
- `/status`
- `/trace`
- `/resume`
- `/config`

MVP 只实现 `/exit`，其余命令等 checkpoint replay 和 trace reader 稳定后再设计。

**后续可观测与产品化能力**

- checkpoint replay。
- trace 查询和可视化。
- VS Code 插件。
- MCP Server。
- Dashboard。
- 真实项目文件索引。
- 长任务恢复。
- 用户确认和权限审批交互。

这些能力都不是 MVP。MVP 的成功标准是本地 `prime` REPL 可以在完全 fake 的环境中稳定跑通 single agent runtime 闭环，并留下足够的 checkpoint、trace 和 turn report 供后续演进。

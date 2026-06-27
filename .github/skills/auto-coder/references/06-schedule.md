## 6. 项目排期

**阶段 A：工程骨架与 CLI REPL**

| 状态 | 任务 | 目标 | 修改文件 | 实现类 / 函数 | 验收标准 | 测试方法 |
| --- | --- | --- | --- | --- | --- | --- |
| [ ] | A1 | 初始化 Python 项目骨架和基础目录 | `pyproject.toml`, `src/prime/__init__.py`, `tests/unit/`, `tests/integration/`, `tests/e2e/`, `config/settings.yaml` | 项目包声明和基础配置 | `src/prime` 可被导入，pytest 可发现测试目录 | `pytest` |
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

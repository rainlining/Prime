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

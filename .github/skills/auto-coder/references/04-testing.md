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

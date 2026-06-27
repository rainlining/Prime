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

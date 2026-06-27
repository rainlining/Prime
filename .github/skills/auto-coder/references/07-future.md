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

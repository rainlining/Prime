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

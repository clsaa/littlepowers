# Littlepowers

[English](README.md)

Littlepowers 是一个同时面向 Codex 与 Claude Code 的“按风险规划 + 任务恢复 + 工程纪律”协议。它帮助 Agent 在编码前固定重要决策，在中断后恢复最后一个可靠 checkpoint，并按证据调试、审查重要改动、按实际影响面完成验证。

它受 [Superpowers](https://github.com/obra/superpowers) 启发，但不是 fork、没有运行时依赖，也不隶属于 Superpowers 或 obra。

## 工作深度

Littlepowers 根据未解决的决策和失败风险选流程，不根据文件数量或模型推理档位选流程：

| 路径 | 适用情况 | 产物 |
| --- | --- | --- |
| Direct | 目标和实现方式都明确 | 无；长任务可只创建执行 ledger |
| Compact | 有少量相关决策需要固定 | 一份 shape brief |
| Full | 用户明确要求，或仍有实质性的架构、安全、迁移、跨系统、不可逆操作或高回滚成本决策 | brainstorm → spec → design → plan |

持久产物默认写入 `docs/littlepowers/...`。只有最新用户请求或当前仓库规则明确指定“新 workflow artifact”的根目录时才使用其他路径；已有目录、反向链接、历史文件或带旧工具品牌的路径不会自动覆盖默认值。

另有三个按条件触发的能力：

- **系统化调试**：先复现和定位最早偏差，再一次验证一个假设；仅要求诊断时不修改代码；
- **按影响面验证**：完成声明必须有最新证据；局部回滚单元只跑 focused checks，共享契约或发布边界才补 broad checks，不因小改动默认跑全量测试；
- **轻量审查**：在用户要求、集成 worker 结果、共享行为里程碑或高回滚成本时，分别给出需求符合性与代码质量结论；孤立小改动可只做结构化自审。

这些能力不会自动创建 Agent、选择模型、强制 TDD 或要求输出隐藏推理；Codex 与 Claude Code 使用同一份实现。

被追踪的任务会写入当前 worktree 下的 `.littlepowers/state.json`。状态包含 workflow ID、单调递增 revision，以及可选的、基于证据的进度；进度应写成里程碑或验收项计数，不能根据时间和文件数量猜百分比。旧 revision 写入会失败，不会覆盖新进度。

三个只读 Hook 负责提供状态：

- `SessionStart`：启动、resume、clear、compact 后提供完整但有上限的快照；
- `UserPromptSubmit`：每个受支持的新提示前提供更短的提醒；
- `SubagentStart`：标记父任务由协调 Agent 写入，worker 只读。

另外两个边界工具平时保持休眠：

- **工作区交接**：只校验显式指定的另一根目录和活跃 workflow，取消源 ledger 并留下目标指针；它不会扫描兄弟 worktree，也不能改变当前任务根目录。后续必须在目标目录新建任务或会话并重新核验；
- **评审快照**：仅在“广泛且未提交”的候选改动需要防止评审对象漂移时显式运行，返回不含文件内容的有界哈希 token。Hook 不扫描 Git、不哈希项目文件。

过大的重要评审可以按信任边界、状态所有权或回滚边界分区，再由一个验收负责人统一汇总共享接口证据一次。Littlepowers 不创建 reviewer、不选择模型或 effort，也不会因此增加测试轮次；普通路径没有交接、快照或额外模型调用成本。

## 能力边界

Littlepowers 能记录并恢复最后一次 checkpoint，但不能强迫模型遵循提醒、阻止同一轮 steering、覆盖最新用户请求，也不能让运行中的任务热加载替换后的插件。Codex 中，如果消息必须等当前运行结束再处理，请使用 Queue。

暂停中的 workflow 不会因为普通实现提示而自动恢复；必须先完成显式 `resume`。超过 30 天未更新的 ledger 会标记为按时间过期，需先与当前代码和最新请求核对，再决定是否继续。

一个 worktree 只支持一个活跃的顶层 workflow。并行的独立目标应使用不同 worktree。Ultra 或 Claude dynamic workflows 中，只有根协调 Agent 写 ledger；worker 返回证据。

真正跨工作区时，应先在目标根目录创建活跃 workflow，再用两端明确的 workflow ID 与 revision 交接源 workflow，随后到目标根目录的新任务或会话继续。普通 phase 变化、状态问题和 compaction 不使用 handoff。

Littlepowers 可独立运行。若把它和 Superpowers 同时设为默认 router，可能产生重复或冲突的规划指令。并排评估时应显式调用其中一个带 namespace 的 router，不要在同一仓库同时加入两套持久规则片段。

完整边界见[能力矩阵](docs/capability-matrix.md)。

## 环境要求

- Codex 或 Claude Code
- Python 3.9+
- Windows 上安装 Git Bash
- 仓库保持私有期间，需要可读取该仓库的 Git 凭据

## 安装到 Codex

```bash
codex plugin marketplace add clsaa/littlepowers --ref v0.4.0-alpha.1
codex plugin add littlepowers@littlepowers
```

新建任务后，用 `/hooks` 检查并信任 Hook。显式调用：

```text
$littlepowers:using-littlepowers 请使用完整的 brainstorm、spec、design、plan 流程设计并实现这个功能。
```

检查状态：

```text
$littlepowers:managing-littlepowers 运行 doctor，并显示当前 workflow。
```

Codex 的 Queue 用于延迟消息，`/side` 或 `/btw` 用于无关问题。Littlepowers 不再推荐 `/goal`，避免出现两个目标事实源。

## 安装到 Claude Code

```bash
claude plugin marketplace add clsaa/littlepowers
claude plugin install littlepowers@littlepowers
```

重启会话或执行 `/reload-plugins`，检查并启用 Hook。显式调用：

```text
/littlepowers:using-littlepowers 请使用完整的 brainstorm、spec、design、plan 流程设计并实现这个功能。
```

检查状态：

```text
/littlepowers:managing-littlepowers 运行 doctor，并显示当前 workflow。
```

可选的持久规则分别在 [AGENTS.md 片段](assets/agents-snippet.md)和 [CLAUDE.md 片段](assets/claude-snippet.md)。只想在当前项目生效时，请写入项目文件，不要写入全局配置。

## 更新与回滚

不要在正在执行 tracked workflow 的 Codex 任务中替换 Littlepowers。cachebuster 重装可能删除该任务启动时记录的缓存路径。应先让活跃任务 checkpoint 并完成或暂停，再安装更新并新建任务。若路径已经被替换，Littlepowers 会通过宿主的 JSON 插件列表解析唯一启用的安装，重新读取当前技能后再继续；解析缺失或不唯一时必须停止。

Codex 的 tag 安装需要先删除现有插件和 marketplace，再把 `--ref` 改成目标版本并重新安装。Claude Code 使用：

```bash
claude plugin marketplace update littlepowers
claude plugin update littlepowers@littlepowers
```

随后重启或执行 `/reload-plugins`。更新前查看 [CHANGELOG](CHANGELOG.md)。

## 隐私与安全

- 无遥测、无运行时网络访问、无对话 transcript 解析；
- Hook 只读 ledger，错误时 fail-open；
- 统一拒绝 Git tracked state、链接/reparse point、异常所有权或写权限、非普通文件，以及读取或序列化后超过 64 KiB 的 state；
- POSIX 写事务逐级固定 workspace 路径和已验证的 state 目录，再相对该目录执行 lock、state 和 archive I/O；中间路径或最终目录被并发替换也不会把写入导向外部；
- artifact 只接受规范化的 Markdown 相对路径，并通过绑定 workflow ID/revision 且有大小上限的安全读取命令加载；链接、特殊文件会被拒绝，内容始终标为不可信项目数据；
- 可选 review snapshot 只读并受路径数、Git 输出、文件字节数和超时限制，只返回哈希与计数，Hook 永远不会调用它；
- 写入使用跨进程锁、workflow ID、预期 revision、原子替换和替换前归档；
- Littlepowers 本身不会请求 commit、push、PR、部署、公开仓库或启动 subagent。

详见[安全模型](docs/security-model.md)和[模型兼容报告](docs/model-compatibility.md)。

## 模型兼容性

Littlepowers 不选择模型或 effort。调试、审查与验证只要求可观察证据和简洁结论，不要求输出 chain-of-thought；它们按条件触发，不会在每个提示里重复整套流程。

- GPT-5.6 Sol xhigh 在一轮预发行评估中通过了场景 1 至 9；这还不是三轮重复运行后的可靠性结论；
- GPT-5.6 Sol max 完成 v0.3 对抗审查，43 项测试通过，没有遗留 P0/P1；
- Codex Ultra 通过根协调 Agent 加两个只读 worker 的并发场景，但 coordinator-only 仍是协作协议，不是操作系统权限隔离；
- Claude Fable 5 与 Opus 4.8 没有模型参数冲突，Claude Code 严格插件校验通过；本机未登录 Claude，因此尚未记录认证后的 v0.4 模型端到端运行。

## 卸载

```bash
codex plugin remove littlepowers@littlepowers
codex plugin marketplace remove littlepowers
```

```bash
claude plugin uninstall littlepowers@littlepowers
claude plugin marketplace remove littlepowers
```

同时删除你手工复制到 `AGENTS.md` 或 `CLAUDE.md` 的片段。卸载不会删除 `.littlepowers`；只有在不再需要恢复记录并确认准确 workspace 后，才清理该目录。

## 名称说明

专家评审更推荐长期公开品牌 **Planthread**，因为它更准确表达“让计划跨提示和会话保持连续”，也不会让人误解为 Superpowers 的官方轻量版。本次 v0.4 不擅自改名；在仓库公开前由项目所有者最终决定。

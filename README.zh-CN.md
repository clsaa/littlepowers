# Littlepowers

[![CI](https://github.com/clsaa/littlepowers/actions/workflows/test.yml/badge.svg)](https://github.com/clsaa/littlepowers/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/clsaa/littlepowers)](https://github.com/clsaa/littlepowers/releases)

[English](README.md)

Littlepowers 是一个同时面向 Codex、Claude Code、Qoder 与 OpenCode 的“按风险规划 + 任务恢复 + 工程纪律”协议。它帮助 Agent 在编码前固定重要决策，在中断后恢复最后一个可靠 checkpoint，并按证据调试、审查重要改动、按实际影响面完成验证。

它受 [Superpowers](https://github.com/obra/superpowers) 启发，但不是 fork、没有运行时依赖，也不隶属于 Superpowers 或 obra。

**为什么不选 Superpowers？** Superpowers 对工作普遍施加完整流程礼仪；Littlepowers 按风险伸缩礼仪：一行修复仍是一行修复，小而有决策的改动走 brainstorm → plan，只有存在重大未决问题时才走 brainstorm → spec → design → plan。带规划的路径会在阶段边界等你审核。30 秒上手：

```text
使用 Littlepowers 先 brainstorm 这个边界明确的 API 变更，直接写 plan，然后实现并验证。
```

## 工作深度

Littlepowers 根据未解决的决策和失败风险选流程，不根据文件数量或模型推理档位选流程：

| 路径 | 适用情况 | 产物 |
| --- | --- | --- |
| Direct | 目标和实现方式都明确 | 无；长任务可只创建执行 ledger |
| Lean plan | 小而边界明确，但仍需做一个真实决策并形成可执行计划 | brainstorm → plan |
| Compact | 有少量相关决策需要固定 | 一份 shape brief |
| Full | 用户明确要求，或仍有实质性的架构、安全、迁移、跨系统、不可逆操作或高回滚成本决策 | brainstorm → spec → design → plan |

持久产物默认写入 `docs/littlepowers/...`。只有最新用户请求或当前仓库规则明确指定“新 workflow artifact”的根目录时才使用其他路径；已有目录、反向链接、历史文件或带旧工具品牌的路径不会自动覆盖默认值。

Lean 与 Full 路径的每个阶段产物都是审核门禁：Agent 会展示产物并等待批准后才进入下一阶段，除非你明确授权“端到端无人值守执行”。

所有路径都会把最新请求以及已批准的 PRD、交互稿、原型、截图集或契约绑定为完整结果。Agent 不得自行拆成更小的产品切片或技术切片；任何 `Added / Changed / Deferred / Removed` 范围变化都必须突出展示并单独获得批准，没有变化则明确记录 `No scope delta`。实现过程是同一个完成定义下的连续工作流；任务、checkpoint、回滚单元和小提交只负责顺序与安全恢复，不是分期交付。UI 一致性必须对比用户批准的基线，实现自己生成的截图只能用于防回归。

被追踪的工作使用 Outcome Lock 1.2：经审核的 Contract 记录稳定 `OUT-###` ID 和显式父来源摘要；Plan Map 必须在执行前把每个活跃 ID 映射到任务与证据；Verification Record 分别保存工作单元符合性、批准结果一致性和代码质量。Schema 3 会在来源漂移或覆盖不完整时阻止执行，并在所有当前门禁通过前阻止完成。它无法推断经审核 Contract 本身遗漏的语义，因此阶段审核仍负责契约的语义完整性。

在 Codex 中，任务清单还会镜像到原生 `update_plan` 工具（在 OpenCode 中镜像到其 todo 工具），让计划显示在宿主界面上；Markdown 计划文件仍是持久事实源。

另有三个按条件触发的能力：

- **系统化调试**：先复现和定位最早偏差，再一次验证一个假设；仅要求诊断时不修改代码；
- **按影响面验证**：完成声明必须有最新证据；局部回滚单元只跑 focused checks，共享契约或发布边界才补 broad checks，不因小改动默认跑全量测试；
- **轻量审查**：在用户要求、集成 worker 结果、共享行为里程碑或高回滚成本时，分别给出工作单元符合性、完整目标一致性与代码质量结论；孤立小改动可只做结构化自审。

这些能力不会自动创建 Agent、选择模型、强制 TDD 或要求输出隐藏推理；Codex、Claude Code、Qoder 与 OpenCode 使用同一份实现。

被追踪的任务会写入当前 worktree 下的 `.littlepowers/state.json`。Schema 3 状态包含协议版本、Outcome Lock 摘要、workflow ID、单调递增 revision，以及可选的、基于证据的进度；进度应写成里程碑或验收项计数，不能根据时间和文件数量猜百分比。旧 revision 写入会失败，不会覆盖新进度。

三个只读 Hook 负责提供状态：

- `SessionStart`：启动、resume、clear、compact 后提供完整但有上限的快照；
- `UserPromptSubmit`：每个受支持的新提示前提供更短的提醒；
- `SubagentStart`：标记父任务由协调 Agent 写入，worker 只读。

另外两个边界工具平时保持休眠：

- **工作区交接**：只校验显式指定的另一根目录和活跃 workflow，取消源 ledger 并留下目标指针；它不会扫描兄弟 worktree，也不能改变当前任务根目录。后续必须在目标目录新建任务或会话并重新核验；
- **评审快照**：仅在“广泛且未提交”的候选改动需要防止评审对象漂移时显式运行，返回不含文件内容的有界哈希 token。Hook 不扫描 Git、不哈希项目文件。

过大的重要评审可以按信任边界、状态所有权或回滚边界分区，再由一个验收负责人统一汇总共享接口证据一次。Littlepowers 不创建 reviewer、不选择模型或 effort，也不会因此增加测试轮次；普通路径没有交接、快照或额外模型调用成本。

## 能力边界

Outcome Lock 能确定性拒绝来源漂移、已声明 ID 缺失、无效范围状态、不完整 fidelity 和虚假完成转换；但它不能强迫模型从自由文本中提取全部语义、阻止同一轮 steering、覆盖最新用户请求，也不能让运行中的任务热加载替换后的插件。Codex 中，如果消息必须等当前运行结束再处理，请使用 Queue。

暂停中的 workflow 不会因为普通实现提示而自动恢复；必须先完成显式 `resume`。超过 30 天未更新的 ledger 会标记为按时间过期，需先与当前代码和最新请求核对，再决定是否继续。

Qoder IDE 目前只支持部分 Hook 事件，因此 SessionStart 快照和 SubagentStart 标记在 IDE 中不会触发，UserPromptSubmit 提醒仍可用。

一个 worktree 只支持一个活跃的顶层 workflow。并行的独立目标应使用不同 worktree。Ultra 或 Claude dynamic workflows 中，只有根协调 Agent 写 ledger；worker 返回证据。

真正跨工作区时，应先在目标根目录创建活跃 workflow，再用两端明确的 workflow ID 与 revision 交接源 workflow，随后到目标根目录的新任务或会话继续。普通 phase 变化、状态问题和 compaction 不使用 handoff。

Littlepowers 可独立运行。若把它和 Superpowers 同时设为默认 router，可能产生重复或冲突的规划指令。并排评估时应显式调用其中一个带 namespace 的 router，不要在同一仓库同时加入两套持久规则片段。

完整边界见[能力矩阵](docs/capability-matrix.md)。

## 环境要求

- Codex、Claude Code、Qoder CLI（或 Qoder IDE）、OpenCode 之一
- Python 3.9+
- Windows 上安装 Git Bash

## 安装到 Codex

`v1.2.0-alpha.1` 发布后按 tag 安装：

```bash
codex plugin marketplace add clsaa/littlepowers --ref v1.2.0-alpha.1
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

## 安装到 Qoder

Qoder CLI 与 Qoder IDE 共用同一套插件结构。

```bash
qodercli plugins marketplace add clsaa/littlepowers
qodercli plugins install littlepowers
```

本地检出可用 `qodercli plugins install /path/to/littlepowers` 安装。重启会话或执行 `/skills reload`，并先检查插件 Hook 再信任。Qoder IDE 通过 Marketplace 面板安装，或导入本地插件目录。

显式调用：

```text
/using-littlepowers 请使用完整的 brainstorm、spec、design、plan 流程设计并实现这个功能。
```

检查状态：

```text
/managing-littlepowers 运行 doctor，并显示当前 workflow。
```

仓库级默认规则可复制 [AGENTS.md 片段](assets/agents-snippet.md)，Qoder 会自动读取 `AGENTS.md`。Qoder IDE 目前只触发部分 Hook 事件，SessionStart 快照与 SubagentStart 标记暂不可用；IDE 也未文档化为插件 Hook 注入 `QODER_PLUGIN_ROOT`，因此在宿主提供该变量之前，IDE 中的 Hook 命令可能无法解析插件根目录。

## 安装到 OpenCode

在 `opencode.json`（全局或项目级）的 `plugin` 数组中加入：

```json
{
  "plugin": ["littlepowers@git+https://github.com/clsaa/littlepowers.git"]
}
```

重启 OpenCode。插件会把 skills 目录注册给 OpenCode 原生 skill 工具，并注入与其他宿主相同的只读 ledger 快照。验证安装：让模型列出它的技能，应能看到十一个 Littlepowers 技能。OpenCode 只在插件加载失败时才在日志里打印插件名，因此 `opencode run --print-logs "hello" 2>&1 | grep -i littlepowers` 用作失败排查：有输出表示加载出错，无输出表示正常。

通过技能名显式调用：

```text
使用 using-littlepowers 技能，按完整的 brainstorm、spec、design、plan 流程设计并实现这个功能。
```

仓库级默认规则可复制 [AGENTS.md 片段](assets/agents-snippet.md)，OpenCode 会自动读取 `AGENTS.md`。OpenCode 没有与 SubagentStart 对应的事件，worker 只读标记不会注入；根协调 Agent 独占写入仍是协议约定。

## 使用方式

说明你想要的结果和规划深度：

```text
使用 Littlepowers 实现这个明确的迁移脚本。它可能跨多轮，请跟踪进度，但不要创建规划文档。
```

```text
使用 Littlepowers 先 brainstorm 这个边界明确的小改动，跳过独立 spec/design，直接写 plan，然后实现并验证完整结果。
```

```text
使用 Littlepowers 的 compact shaping 处理这个 API 变更，然后实现并验证。
```

```text
使用完整的 Littlepowers 流程：brainstorm 备选方案、写 spec、做 design、写 plan，然后实现并验证。
```

工程纪律能力也可以单独调用：

```text
使用 Littlepowers 只诊断这个失败的测试，不要修改代码：先复现，定位最早的偏差，给出有证据支持的原因。
```

```text
只读审查这个已集成的改动，然后按它实际的回滚边界验证每一条完成声明。
```

被跟踪的任务进行期间：

- 相关的更正会更新当前 workflow 并继续；
- 对近期活跃 workflow 的状态或旁路问题，先回答再回到记录的下一步（停在审核门禁处时例外：回答后继续等待批准）；
- 无关工作保留 ledger，移到旁路任务或独立 worktree；
- 替换目标会归档旧 ledger；
- 暂停和恢复都是显式状态转换。

真正的跨工作区转移：先在目标根目录创建活跃 workflow，再用两端明确的 workflow ID 与 revision 交接源 workflow，然后从目标根目录的新任务或会话继续。普通 phase 变化、状态问题和 compaction 不使用 handoff。

暂停的 workflow 不会从普通实现提示中恢复；超过 30 天的 ledger 按时间过期，需先核对后才能继续。router 始终服从最新用户请求，意图明确时不需要特殊的取消用词。

## 更新与回滚

不要在正在执行 tracked workflow 的 Codex 任务中替换 Littlepowers。cachebuster 重装可能删除该任务启动时记录的缓存路径。应先让活跃任务 checkpoint 并完成或暂停，再安装更新并新建任务。若路径已经被替换，Littlepowers 会通过宿主的 JSON 插件列表解析唯一启用的安装，重新读取当前技能后再继续；解析缺失或不唯一时必须停止。

第一次成功写入 schema 3 前，会在 `.littlepowers/archive/` 下创建一个带
`pre-schema3-v<schema>` 后缀的原始 ledger 归档。1.1 runtime 不能读取
schema-3 当前 ledger；若要回退 runtime，应先暂停或完成任务，把该精确归档恢复为
`state.json`，再安装旧版本，不能直接手改或降级活跃 ledger。

Codex 的 tag 安装需要先删除现有插件和 marketplace，再把 `--ref` 改成目标版本并重新安装。Claude Code 使用：

```bash
claude plugin marketplace update littlepowers
claude plugin update littlepowers@littlepowers
```

随后重启或执行 `/reload-plugins`。更新前查看 [CHANGELOG](CHANGELOG.md)。

Qoder CLI 使用：

```bash
qodercli plugins marketplace update littlepowers
qodercli plugins update littlepowers
```

随后重启会话或执行 `/skills reload`。OpenCode 需要刷新 git 方式安装的插件（清理包缓存或重新安装）并重启；需要固定版本时在 git URL 中指定 tag。

## 隐私与安全

- 无遥测、无运行时网络访问、无对话 transcript 解析；
- Hook 只读 ledger，错误时 fail-open；
- 统一拒绝 Git tracked state、链接/reparse point、异常所有权或写权限、非普通文件，以及读取或序列化后超过 64 KiB 的 state；
- POSIX 写事务逐级固定 workspace 路径和已验证的 state 目录，再相对该目录执行 lock、state 和 archive I/O；中间路径或最终目录被并发替换也不会把写入导向外部；
- 协议 artifact 只接受规范化的 Markdown 相对路径；显式父来源和证据仅在生命周期门禁通过有上限的安全 reader 加载，路径越界、链接、特殊文件、替换竞态和超限输入都会被拒绝，Hook 不会打开或哈希这些文件；
- 可选 review snapshot 只读并受路径数、Git 输出、文件字节数和超时限制，只返回哈希与计数，Hook 永远不会调用它；
- 写入使用跨进程锁、workflow ID、预期 revision、原子替换和替换前归档；
- Littlepowers 本身不会请求 commit、push、PR、部署、公开仓库或启动 subagent。

详见[安全模型](docs/security-model.md)和[模型兼容报告](docs/model-compatibility.md)。通过[安全政策](SECURITY.md)报告漏洞。

## 模型兼容性

Littlepowers 不选择模型或 effort。调试、审查与验证只要求可观察证据和简洁结论，不要求输出 chain-of-thought；它们按条件触发，不会在每个提示里重复整套流程。

Outcome Lock 只在 bind、阶段转换、resume/readiness、verification 与 completion 边界增加本地 JSON 校验和 SHA-256；不会增加模型轮次、Agent、后台扫描、自动测试或 effort 覆盖。运行成本与显式绑定文件和声明行数成正比，与仓库大小无关，因此协议层不会与 GPT-5.6 Sol xhigh/max/Ultra、Fable 5 或 Opus 4.8 冲突。高 effort 的耗时仍由宿主和模型决定，不是 Littlepowers 新增的工作。

- GPT-5.6 Sol xhigh 在一轮预发行评估中通过了场景 1 至 9；这还不是三轮重复运行后的可靠性结论；
- GPT-5.6 Sol max 完成 v0.3 对抗审查，43 项测试通过，没有遗留 P0/P1；
- Codex Ultra 通过根协调 Agent 加两个只读 worker 的并发场景，但 coordinator-only 仍是协作协议，不是操作系统权限隔离；
- Claude Fable 5 与 Opus 4.8 没有模型参数冲突，Claude Code 严格插件校验通过；本机未登录 Claude，因此尚未记录认证后的 v0.4 模型端到端运行；
- Qoder CLI、Qoder IDE 与 OpenCode 加载同一套技能、Hook 与 state CLI，但这三个宿主尚未记录认证后的端到端模型运行。

## 故障排查

先运行管理技能的 `doctor` 流程。常见原因：

- 插件或 Hook 未被信任、被禁用，或被组织策略拦截；
- Python 3 不可用，或 Windows 上缺少 Git Bash；
- 提示运行的 worktree 或非 Git 目录与 ledger 不一致；
- ledger 被 Git 跟踪、是链接、格式损坏、超过大小上限，或 artifact 路径越界；
- 另一个协调者推进了 revision——重新加载，不要用旧 revision 重试；
- 活跃任务期间插件缓存被替换——解析唯一启用的安装，重读当前技能，之后的更新换到新任务边界；
- Claude Code 仍在使用旧缓存的插件——更新并 reload；
- Codex 中计划没有出现在界面里——计划清单视图只渲染原生 `update_plan` 工具的调用；确认写完 artifact 后已镜像。单独的 Markdown 文件永远不会显示在该视图中；
- Qoder IDE 不触发 SessionStart 与 SubagentStart Hook；OpenCode 需要确认 `opencode.json` 中的插件条目指向刷新后的安装。

[能力矩阵](docs/capability-matrix.md)区分预期限制与故障。

## 开发与验证

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts hooks tests
claude plugin validate --strict .
qodercli plugins validate .
```

发布检查还会运行随附的 Codex 技能与插件校验器。GitHub Actions 在 Linux、macOS、Windows 上运行 state 与 Hook 测试套件，并在 Linux 上运行固定版本的 Claude Code 校验。

提交 PR 前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 卸载

```bash
codex plugin remove littlepowers@littlepowers
codex plugin marketplace remove littlepowers
```

```bash
claude plugin uninstall littlepowers@littlepowers
claude plugin marketplace remove littlepowers
```

Qoder CLI：在 `settings.json` 的 `enabledPlugins` 中禁用，或执行 `qodercli plugins marketplace remove littlepowers` 移除插件与 marketplace。

OpenCode：从 `opencode.json` 的 `plugin` 数组中删除 `littlepowers@git+...` 条目并重启。

同时删除你手工复制到 `AGENTS.md` 或 `CLAUDE.md` 的片段。卸载不会删除 `.littlepowers`；只有在不再需要恢复记录并确认准确 workspace 后，才清理该目录。

## 许可与灵感

Littlepowers 以 MIT 许可发布。设计参考了同为 MIT 许可的 Superpowers v6.1.1。Littlepowers 不是 fork，未获得 Superpowers 或 obra 的认可，是一份专注于按风险规划与有界恢复的独立实现。详见[灵感与出处](docs/inspiration.md)。

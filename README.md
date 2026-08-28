# Codex Project Dev Skills

一套面向长期 AI 开发的轻量 Codex Skills，解决多会话上下文不断增长后出现的进度丢失、任务漂移、Git 混乱和测试策略失控问题。

它不依赖一个永远不结束的对话，而是把可信进度保存在项目仓库中：

```text
AGENTS.md + 项目设计文档 + STATE.md + 任务卡 + Git + 测试证据
```

## 包含的 Skills

| Skill | 用途 |
| --- | --- |
| `project-dev` | 初始化或接管项目，管理跨会话状态、任务范围、Git 分支、提交、拉取、合并、文档同步与安全恢复 |
| `tdd-workflow` | 在合适的任务中执行经过验证的 Red → Green → Refactor 流程 |

`project-dev` 是主入口。它根据项目和任务风险决定测试模式；只有确定性规则、回归缺陷或高风险数据行为真正适合测试先行时，才使用 `tdd-workflow`。

## 安装

### 让 Codex 安装

在 Codex 中发送：

```text
使用 $skill-installer 从 GitHub 仓库 CatsDoNotEatFish/codex-project-dev-skills 安装 skills/project-dev 和 skills/tdd-workflow
```

安装后在下一次交互中即可使用。

### Windows 手工安装

```powershell
git clone https://github.com/CatsDoNotEatFish/codex-project-dev-skills.git
Set-Location codex-project-dev-skills

$skillRoot = if ($env:CODEX_HOME) {
    Join-Path $env:CODEX_HOME "skills"
} else {
    Join-Path $env:USERPROFILE ".codex\skills"
}

New-Item -ItemType Directory -Path $skillRoot -Force | Out-Null
Copy-Item -Recurse -LiteralPath ".\skills\project-dev" -Destination $skillRoot
Copy-Item -Recurse -LiteralPath ".\skills\tdd-workflow" -Destination $skillRoot
```

### macOS / Linux 手工安装

```bash
git clone https://github.com/CatsDoNotEatFish/codex-project-dev-skills.git
cd codex-project-dev-skills

SKILL_ROOT="${CODEX_HOME:-$HOME/.codex}/skills"
mkdir -p "$SKILL_ROOT"
cp -R skills/project-dev "$SKILL_ROOT/"
cp -R skills/tdd-workflow "$SKILL_ROOT/"
```

如果目标 Skill 已存在，请先确认需要升级的版本并备份已有修改，不要直接混合复制两个版本。

## 使用

### 空项目

```text
$project-dev 初始化一个库存管理系统，支持商品、采购、出入库和库存预警
```

Agent 会先形成精简设计基线、项目规则、状态文件和首个任务，然后初始化 Git。影响产品方向的关键决策未确认前，不会直接堆积大量业务代码。

### 接管已有项目

```text
$project-dev 初始化并接管当前项目
```

有代码但没有文档时，Agent 会先基于现有实现生成 as-is 基线；已有文档和规则时则保留原有约定，只补充缺失的协调层。

### 新会话继续开发

```text
$project-dev 继续开发
```

新会话从仓库中的 `docs/ai/PROJECT.md`、`STATE.md`、活动任务卡、Git 状态和测试证据恢复进度，不依赖旧会话聊天记录。

### 修改或新增功能

```text
$project-dev 修改功能 A：增加批量导出，并保持现有权限规则
```

Agent 会把需求收敛为一个可观察任务，在独立任务分支完成、验证、提交并按项目策略合并。

### 明确使用 TDD

```text
$tdd-workflow 用 TDD 修复重复导入覆盖人工审核值的问题
```

## 什么时候使用 TDD

| 任务特征 | 建议模式 |
| --- | --- |
| 确定性业务规则、算法、解析、状态机、权限、隐私、金额、数据完整性、可复现 Bug、稳定 API 契约 | `tdd` |
| 页面或适配器同时包含确定性核心逻辑与视觉、浏览器或外部系统行为 | `mixed` |
| 行为明确，但必须依赖完整浏览器、真实框架生命周期、数据库或外部沙箱验证 | `test-after` |
| 可行性、接口或需求仍然未知的限时调研 | `exploratory` |
| 纯文档、任务元数据或无可执行行为的资源变更 | `none` |

TDD 任务必须真实观察到测试因目标行为缺失而失败。语法错误、环境损坏或测试本身无效不能算 Red 阶段证据。

## Git 默认行为

- 项目初始化时建立 `main` 和安全基线提交。
- 每个活动任务使用 `task/<task-id>-<slug>` 短分支。
- 在可审查节点自动创建本地提交。
- 只在干净默认分支执行 `pull --ff-only`。
- 合并前重新运行任务检查和状态校验。
- 不自动执行强推、硬重置、丢弃用户修改、自动 stash 或语义冲突猜测。
- 是否推送由项目 `push_policy` 和用户授权共同决定。

登录 GitHub 不等于已经选择远程仓库。首次远程绑定、公开发布和部署仍需要明确目标。

## 项目结构

```text
skills/
├── project-dev/
│   ├── SKILL.md
│   ├── assets/
│   ├── references/
│   ├── scripts/
│   └── tests/
└── tdd-workflow/
    ├── SKILL.md
    └── references/
```

## 验证

```powershell
python -B -m unittest discover -s skills/project-dev/tests -p "test_*.py" -v
```

首版包含 14 项状态、任务、TDD、Git、安全路径和空项目基线测试。

## 版本

当前稳定版本：`v1.0.0`

详细内容见 [CHANGELOG.md](CHANGELOG.md) 和 [GitHub Releases](https://github.com/CatsDoNotEatFish/codex-project-dev-skills/releases)。

## License

[MIT](LICENSE)

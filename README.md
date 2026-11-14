# skills

我的 AI Agent Skills 合集，兼容 [npx skills](https://github.com/vercel-labs/skills)（Vercel Labs 的开源 Agent Skills 生态）。

每个 skill 是 `skills/` 目录下的一个独立文件夹，内含一份带 YAML frontmatter 的 `SKILL.md`。内容不绑定特定 Agent，具体发现和加载方式取决于所用工具。

## 安装

无需克隆本仓库，在任意项目目录下运行：

```bash
# 安装本仓库的全部 skills
npx skills add minorcell/skills

# 只安装其中一个 skill
npx skills add minorcell/skills --skill writing-proposals

# 全局安装（写入 ~/.agents/skills/）
npx skills add minorcell/skills --skill writing-proposals --global
```

`-y` 可跳过确认提示；`--agent` 可指定要安装的 Agent 工具（如 `claude-code`、`cursor`），不指定则自动检测已安装的工具。

## Skills 列表

| Skill | 说明 |
|---|---|
| [writing-proposals](./skills/writing-proposals) | 起草、改写和评审技术提案、RFC、API、语言、工具、协议设计及实施计划。从真实用户场景出发，以小步推进、减法设计和明确边界形成可评审、可实现、可验证的方案，按风险选择简短模板、标准模板或完整规范。 |

## 使用示例

安装 `writing-proposals` 后，可在支持 skill 的 Agent 中提出以下请求；显式调用方式以所用工具为准：

```text
使用 writing-proposals，把以下 API 改造想法整理成中文技术提案：……
使用 writing-proposals，评审这份 RFC，指出边界、兼容性和错误处理中的缺项。
使用 writing-proposals，为这个协议变更编写提案，说明消息格式、版本协商和重试行为。
```

该 skill 提供中文写作指导，输出语言和格式遵循用户要求及项目规范。不需要额外脚本、运行时或专用工具。

## 目录规范

```
skills/
├── README.md
├── LICENSE
└── skills/
    └── writing-proposals/
        ├── SKILL.md         # 中文指导、工作流程、模板和评审检查项
        └── LICENSE          # 随 skill 分发的 MIT 许可证副本
```

## 许可证

本仓库使用 [MIT 许可证](./LICENSE)。`writing-proposals` 在 frontmatter 中声明 `license: MIT`，并附带[许可证副本](./skills/writing-proposals/LICENSE)，便于单独安装和分发。

更多 skill 会持续加入，欢迎 Star ⭐

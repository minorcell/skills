# skills

我的 AI Agent Skills 合集，兼容 [npx skills](https://github.com/vercel-labs/skills)（Vercel Labs 的开源 Agent Skills 生态）。

每个 skill 是仓库根目录下的一个独立文件夹，内含一份带 frontmatter 的 `SKILL.md`，可被 Claude Code、Cursor、Codex 等 75+ 种 Agent 工具识别。

## 安装

无需克隆本仓库，在任意项目目录下运行：

```bash
# 安装本仓库的全部 skills
npx skills add minorcell/skills

# 只安装其中一个 skill
npx skills add minorcell/skills --skill make-video-package

# 全局安装（写入 ~/.agents/skills/）
npx skills add minorcell/skills --skill make-video-package --global
```

`-y` 可跳过确认提示；`--agent` 可指定要安装的 Agent 工具（如 `claude-code`、`cursor`），不指定则自动检测已安装的工具。

## Skills 列表

| Skill | 说明 |
|---|---|
| [make-video-package](./make-video-package) | 给一个主题，通过提问把需求问清楚，然后产出一整包可发布的视频交付物：1080p 成片 MP4、封面、SRT 字幕、平台发布用的标题/简介/标签。画面由 Python 逐帧绘制，配音由 TTS 合成并按句子节拍对齐。 |

## 目录规范

```
skills/
├── README.md
└── make-video-package/      # 每个 skill 一个目录，目录名 = SKILL.md 的 name
    ├── SKILL.md             # 必需：frontmatter 含 name、description
    ├── scripts/             # 可选：skill 引用的脚本
    ├── templates/           # 可选：模板文件
    └── reference/           # 可选：补充参考文档
```

更多 skill 会持续加入，欢迎 Star ⭐

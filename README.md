# trpg-fvtt-skills

星尘制作的，面向桌面角色扮演游戏（TRPG）与 Foundry VTT（FVTT）的 AI 技能集合，涵盖 PF2e 内容制作、规则自动化、视觉资源和社区内容维护。

## 技能一览

| Skill | 功能 |
| --- | --- |
| [fvtt-vfx-prompt-optimizer](fvtt-vfx-prompt-optimizer/SKILL.md) | 将特效想法或已有提示词优化为完整的特效Skills Prompt，明确锚点、动画时序、视觉层次与 FVTT 交付要求；可独立使用，也可交给 fvtt-webm-vfx 渲染。 |
| [fvtt-webm-vfx](fvtt-webm-vfx/SKILL.md) | 制作或修改斩击、闪电、爆炸、光环等透明 2D 特效，输出可用于 FVTT / Sequencer 的 VP9 Alpha 透明WebM、预览图和元数据。需要高性能前端模型。 |
| [pf2-wiki-maintenance](pf2-wiki-maintenance/SKILL.md) | 维护 PF2 灰机 Wiki 的页面、模板、Lua 模块与 Data 数据页，支持依赖分析、候选内容验证和带版本冲突保护的更新。需要 [huijimcp](https://github.com/kagangtuya-star/huijiwiki-api-mcp) 。 |
| [pf2e-fvtt-automation](pf2e-fvtt-automation/SKILL.md) | 面向 Foundry VTT v14 的 PF2e 规则自动化：编写 Rule Elements、效果、行内检定、宏与模块，并提供排错和文档环境维护流程。 |
| [pf2e-fvtt-statblock-author](pf2e-fvtt-statblock-author/SKILL.md) | 将中英文 PF2e 怪物、NPC、危害或单项能力转为 FVTT 可导入的 JSON，配套统一导入宏，支持完整 Actor 创建与同步。 |
| [trpg-circular-token](trpg-circular-token/SKILL.md) | 基于角色原图或已有 Token 设计圆形棋子，保留角色外观，加入边框、圆内背景及适度出框效果，输出外部透明的方形图片。同时，也支持单独设计框体与根据文本描述设计Token框。 |
| [trpg-forum-layout-designer](trpg-forum-layout-designer/SKILL.md) | 为纯美苹果园（GoddessFantasy）/ SMF 论坛排版招募帖、战报、模组介绍与手册，输出以 `[font=;css]` 为核心的 BBCode。 |

## 使用方式

将所需技能目录放入所用 AI 工具支持的 skills 位置，或让 AI 读取对应的 `SKILL.md`，再提供任务说明与素材。目录内的 `references/`、`scripts/`、`assets/`（如有）应一并保留。

使用前注意对应环境要求：

- **WebM 特效**：运行脚本需要 Python 3、Pillow、FFmpeg / ffprobe。
- **Wiki 维护**：在线核验与写入需要兼容的 MediaWiki 连接；无连接时仅进行本地分析或草稿制作。
- **PF2e 自动化与数据导入**：需核对实际安装的 Foundry / PF2e 版本；脚本检查不能替代游戏内验证。
- **圆形 Token**：需要角色原图或图像描述，及 ChatGPT 图像能力，先提供文字设计方案，用户选定后再生成。
- **论坛排版**：默认使用 GF/SMF 严格兼容模式，也可明确要求“创意突破模式”。

具体流程、输出格式和限制以各技能的 `SKILL.md` 为准。

# nnu-thesis-style-2026

南京师范大学（NNU）理工科学位论文 2026 版排版与格式审查 Skill。

A source-traceable Agent Skill for formatting and reviewing Nanjing Normal University science and engineering theses against the supplied 2026 guide.

本项目将用户提供的 17 页《附件4理工科学位论文格式规范（2026版）》整理为 **105 条可追溯记录：50 条明确要求、55 条样张观察**，另列原文未规定的参数。适用于使用该附件的论文规范查询、格式审查与文稿排版；本项目由个人整理，不代表学校官方。

## 使用

Skill 入口：[skills/nnu-thesis-style-2026/SKILL.md](skills/nnu-thesis-style-2026/SKILL.md)。可直接让支持本地 Skill 的 Agent 读取该目录；也可复制到客户端支持的技能目录。以 Codex 的用户技能目录为例：

```bash
git clone https://github.com/Hongxuan-Wu/nnu-thesis-style-2026.git
mkdir -p ~/.codex/skills
test ! -e ~/.codex/skills/nnu-thesis-style-2026 && cp -R nnu-thesis-style-2026/skills/nnu-thesis-style-2026 ~/.codex/skills/
```

目标目录已经存在时，上述命令保留原目录；请先比较版本再自行选择安装位置。客户端可能需要重启或重新发现技能。安装目录由所用客户端的当前支持情况决定，不依赖本仓库的校验脚本。

调用示例：

```text
使用 $nnu-thesis-style-2026，检查这篇理工科专业学位硕士论文的格式。
按规则 ID、附件物理页码和文稿位置列出需修改、待确认和未检查项。
```

```text
按 $nnu-thesis-style-2026 的来源规范调整这份 Word 文稿并另存新文件。
保留科学内容，区分原文明示、样张复刻和本次实施选择，交付修改说明。
```

## 规范内容

| 内容 | 入口 |
| --- | --- |
| 四类封面、声明、摘要、目录、三级标题、正文、图表、附录、参考文献、成果、致谢 | [全量规范台账](skills/nnu-thesis-style-2026/references/requirements.md) |
| 原文未规定、样张观察局限及处理方式 | [边界与未决项](skills/nnu-thesis-style-2026/references/uncertainties.md) |
| 字号、Word 行/磅单位、样式、分节及验证 | [Word 实施映射](skills/nnu-thesis-style-2026/references/word-mapping.md) |
| 附件身份、SHA256、17 页逐页索引与提取方法 | [来源记录](skills/nnu-thesis-style-2026/references/source.md) / [JSON](skills/nnu-thesis-style-2026/references/source.json) |
| 实际论文格式审查的交付结构 | [检查报告模板](skills/nnu-thesis-style-2026/assets/audit-report.md) |

例如：声明正文是宋体四号、28 磅行距，普通正文是宋体小四号、20 磅行距；专业学位硕士封面明示双导师；图题与表题的段间距相反。这些有直接批注支持。英文摘要完整样式、页边距、目录的连续页码方案、公式编号和参考文献国家标准版本没有被附件明文规定，项目不会用通用惯例补成学校要求。

## 项目结构

```text
skills/nnu-thesis-style-2026/
  SKILL.md
  agents/openai.yaml
  references/
  assets/audit-report.md
scripts/check_project.py
tests/test_check_project.py
ci/check.yml                 GitHub Actions 模板，当前未启用
README.md
LICENSE
NOTICE
CONTRIBUTING.md
CHANGELOG.md
```

## 验证

项目自检只使用 Python 标准库，Python 3.8+ 即可，无需安装项目依赖。请使用已有隔离环境。

```bash
python scripts/check_project.py
python -m unittest discover -s tests -v
```

自检检查台账行结构、规则 ID 唯一性、证据标签、来源页码范围与 17 页覆盖、元数据、Skill 基本入口及本地 Markdown 链接。单元测试包含重复规则、错误证据标签、越界页码和缺页等反例。这些结果不能证明规则解释没有语义遗漏，也不能判断任意论文的格式是否合格。

已附 [GitHub Actions 模板](ci/check.yml)，当前未启用。首次发布使用的令牌缺少 `workflow` 权限，GitHub 拒绝上传 `.github/workflows/check.yml`。本项目因此将该文件作为普通模板保存；需要启用时，由有相应权限的维护者将模板放入 `.github/workflows/check.yml` 后提交。公开提交不包含任何已激活工作流，不能将本地测试结果表述为云端 CI 通过。

本版已完成原 PDF 全文提取及 17 页图片核读，并按官方 Skill 结构校验器检查入口。项目没有实现 DOCX 自动排版程序或任意论文自动评分器，没有在 Microsoft Word 中验收一份实际论文。PDF 中部分未嵌入字体导致本地预览出现方框，具体记录见来源页。

## 来源与许可

固定附件 SHA256：`255f26e20ac794b3df5363ea091325ea9f3d53b487c42dcc4cdc27007ae757fb`。原 PDF、原文全文、校徽、样张截图与用户论文均未随公开仓库发布。持有同一附件的使用者可以按物理页码逐条复核；未持有附件者可以审阅整理内容，但无法仅凭本仓库独立核验全部原文。

原创 Skill 指令、脚本及整理说明按 [MIT License](LICENSE) 提供；原学校规范、名称和标识的权利边界见 [NOTICE](NOTICE)。版本变更见 [CHANGELOG.md](CHANGELOG.md)，补充或纠错方法见 [CONTRIBUTING.md](CONTRIBUTING.md)。

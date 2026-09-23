# 仓库整理记录 · 2026-09-23

基线提交：`bac30f0e33a1759e0276317ae0a58f31daee9ebb`。

## 实际问题

仓库已有 22 份 PDF，但根 README 漏掉 `doc/`，`paper/README.md` 仍称正文尚未加入，文献索引仍称没有 PDF。正文/书目/文献台账分散在 `doc/` 与 `paper/references/`。此外一份 PDF 被错标为 Bourgault 2003，首页实际是 Du 等人的约束 Voronoi 论文。

## 归位结果

| 旧路径 | 新路径 |
|---|---|
| `doc/main.tex`、`doc/ieeeconf.cls`、`doc/references.bib` | `paper/manuscript/` 同名文件 |
| `doc/main_test.tex` | `paper/manuscript/template_reference/main_test.tex` |
| `doc/template_reference/` | `paper/manuscript/template_reference/` |
| `doc/SCIENTIFIC_WRITING_GUIDE.md` | `paper/SCIENTIFIC_WRITING_GUIDE.md` |
| `doc/literature/` | `literature/` |
| `paper/references/*.pdf` | `literature/pdfs/<原有引用键>.pdf` |

逐文件原路径、新路径及 SHA-256 见 [migration-2026-09-23.json](migration-2026-09-23.json)。PDF 与 Zotero 本地附件逐一哈希匹配（22/22），没有增加重复副本。四条仍缺 PDF，见[文献索引](../literature/INDEX.md)。

原有研究决策、开放问题、平台源码、算法源码、VRX 上游版本和补丁没有修改。旧文献台账的科学主张与阅读标签保留原样，不将本次文件整理冒充重新完成查新。历史环境交接文档中的旧目录树是当时快照，当前目录以根 README 为准。

## 验证

- `python scripts/check_literature.py`：验证 26 条目录记录、22 个 PDF 的头部/大小/SHA-256、缺失清单及 26 个书目键对应关系。
- `git diff --check`：检查补丁格式。
- `platform/` 与 `algo/` 对基线无差异；本轮不涉及 ROS 构建或实验运行。

这是 Windows 上针对 GitHub 仓库的整理副本，不代表 `/home/cyz/vrx_ws` 运行工作区已自动同步。

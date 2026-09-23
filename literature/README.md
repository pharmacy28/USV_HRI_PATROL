# 文献库

**从 [INDEX.md](INDEX.md) 打开论文。** 26 条核心记录中，22 份 PDF 已在仓库内；缺失项明确列出。

- `pdfs/`：按现有 citekey 命名的 PDF 实体。
- `catalog.json` / `catalog.csv`：题名、DOI、文件状态、Zotero 条目键及校验信息。
- `LITERATURE_LEDGER.md`：原有证据台账；阅读标签保留其原始含义，本次搬迁不代表重新精读。
- `reading-priorities.md`：本轮筛选与阅读范围，独立于历史标签。
- `metadata/`：原 RIS、DOI 和元数据索引。
- `related_work_notes/`：带出处与阅读范围的综合笔记。
- `novelty_boundary.md`：原有创新边界材料；研究决策仍以 [研究决策状态](../idea/研究决策状态.md) 为准。

唯一正式 BibTeX 是 [paper/manuscript/references.bib](../paper/manuscript/references.bib)。不要在多个目录维护相互漂移的 `.bib`。

增补 PDF 时先核对首页题名、作者与 DOI，再按引用键命名，并更新 catalog 和 INDEX。不要凭下载文件名判断论文归属。运行 `python scripts/check_literature.py` 可校验哈希、文件数量及 BibTeX 键对应关系。

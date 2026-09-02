# Zotero 导入说明（USV_HRI_PATROL）

本目录包含：
- `USV_HRI_core_literature.ris`：**推荐的 Zotero 主导入文件**。
- `USV_HRI_core_literature.bib`：给 LaTeX / Better BibTeX 使用。
- `doi_list.txt`：用于 Zotero “Add Item(s) by Identifier” 二次核验。
- `literature_ledger.md`：论文作用、创新威胁、可安全对比点。
- `recommended_collections.md`：建议的 Zotero 分类方式。
- `innovation_boundary_v2.md`：本轮文献压缩后的创新边界。
- `platform_audit_roadmap.md`：针对 GitHub 平台的实验平台改进路线。

## 最推荐的导入方法

1. 打开 Zotero。
2. 新建 Collection：`ICRA_USV_HRI`。
3. 选择 **File → Import…**。
4. 选择 “A file (BibTeX, RIS, Zotero RDF, etc.)”。
5. 选择 `USV_HRI_core_literature.ris`。
6. 将导入结果放入 `ICRA_USV_HRI` collection。
7. 导入完成后按 `FULLY_READ`、`closest_prior_art`、`bayesian_search` 等标签筛选。
8. 对最关键文献，打开条目核对 DOI、页码和正式 venue；若 Zotero 能找到正式 metadata，可用 DOI/网页抓取结果校正。

## 用 DOI 批量二次核验

1. 打开 `doi_list.txt`，复制若干 DOI（可以一次粘贴多行）。
2. Zotero 顶部点击魔杖图标 **Add Item(s) by Identifier**。
3. 粘贴 DOI。
4. Zotero 会从 Crossref/出版社元数据创建条目。
5. 与 RIS 导入条目比对后执行 **Duplicate Items → Merge**。
6. 合并时优先保留正确 DOI、正式 venue、卷期页码和附件。

这个步骤适合在写论文前做最后的 bibliographic hygiene。

## Better BibTeX（推荐）

安装 Zotero 的 Better BibTeX 后：
- 将 `ICRA_USV_HRI` collection 导出为 Better BibTeX；
- 勾选 Keep updated，输出到项目：
  `paper/references/references.bib`
- 这样 Zotero 是唯一的 bibliographic source of truth，LaTeX 的 `.bib` 自动同步。

建议 citekey 统一成：
`AuthorYearKeyword`，例如 `Xie2011Intention`、`Heintzman2021Anticipatory`。

## PDF 管理

不要把来源不明或无再分发许可的论文 PDF 直接提交到公开 GitHub。
推荐：
- PDF 留在 Zotero 本地 / Zotero Storage / WebDAV；
- GitHub 提交 `.bib`、RIS、DOI、literature ledger、阅读状态和公开链接；
- 对明确 open-access 的 PDF，可只保存官方 URL，除非确认许可证允许再分发。

## 关于 HMPCC

当前正式 MRS 2025 会议元数据已核验，但此目录保守地把 arXiv DOI
`10.48550/arXiv.2512.12717` 写入 DOI 字段，避免在未再次核对 IEEE DOI 的情况下写入可能错误的 conference DOI。

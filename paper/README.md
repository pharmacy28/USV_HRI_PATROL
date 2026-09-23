# 论文写作入口

正式正文工作目录：[manuscript/](manuscript/)。原 `doc/` 内容已归位，正文与书目的字节保持不变。本轮是文件整理，没有产生新实验结果或修改研究结论。

| 内容 | 位置 |
|---|---|
| 当前正文（仍含占位内容） | [main.tex](manuscript/main.tex) |
| 唯一正式书目，26 条原引用键 | [references.bib](manuscript/references.bib) |
| IEEE 类文件 | [ieeeconf.cls](manuscript/ieeeconf.cls) |
| 官方模板与最小测试稿 | [template_reference/](manuscript/template_reference/) |
| 写作规范 | [SCIENTIFIC_WRITING_GUIDE.md](SCIENTIFIC_WRITING_GUIDE.md) |
| 参考论文与阅读证据 | [文献索引](../literature/INDEX.md) |

## Overleaf 与本地编辑

将 `manuscript/` 内文件及 `template_reference/` 上传到 Overleaf，设 `main.tex` 为主文件。`template_reference/main_test.tex` 是旧的最小测试，不是第二篇正文。当前正文是否已经配置 bibliography，以实际 LaTeX 源码为准；目录整理不会自动插入引用或改变模板。

在本地编译时先进入 `paper/manuscript/`，以保留类文件和资源的相对路径。参考 PDF 放在 `literature/pdfs/`，不必随正文上传 Overleaf。探索性新想法继续放在 `idea/`，确认之后再进入论文。

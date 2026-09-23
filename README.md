# USV_HRI_PATROL

面向海上区域概率搜索的多无人艇人机协同研究。这里分别维护仿真平台、算法实现、研究决策、论文正文和参考文献。

## 我现在要做什么？

- **找论文、打开 PDF** → [文献总索引](literature/INDEX.md)：26 条核心文献，22 份 PDF，4 条待补全文。
- **看研究边界与未决问题** → [研究决策状态](idea/研究决策状态.md)。候选想法不等于确认的实现要求。
- **修改论文 / 上传 Overleaf** → [论文入口](paper/README.md)，正文在 `paper/manuscript/main.tex`。
- **运行 VRX 平台** → [平台说明](platform/README.md)。
- **查看 Unity 算法的实际实现** → [算法说明](algo/README.md)。
- **查旧路径搬到哪里** → [整理记录](docs/repository-organization.md)。

## 目录约定

| 目录 | 唯一职责 |
|---|---|
| `platform/` | ROS 2 / Gazebo / VRX 工程、配置、上游补丁及运行文档 |
| `algo/` | Unity 算法实现规格与独立参考代码 |
| `idea/` | CONFIRMED / CANDIDATE / OPEN 决策、研究备忘录与探索方案 |
| `paper/manuscript/` | 正文、IEEE 类文件、唯一正式 `references.bib` 与模板 |
| `literature/` | 文献 PDF、条目索引、阅读证据、RIS 与元数据 |
| `docs/` | 仓库维护与路径迁移记录 |
| `scripts/` | 文献文件完整性检查 |

`doc/` 与 `paper/references/` 只保留旧路径说明。请从以上入口继续维护，避免重新建立第二套正文或文献库。

## 获取与核验

```bash
git clone --recurse-submodules https://github.com/pharmacy28/USV_HRI_PATROL.git
cd USV_HRI_PATROL
python scripts/check_literature.py
cd platform
./scripts/setup_vrx.sh
```

阅读文献不需要初始化 VRX 子模块，直接打开 `literature/INDEX.md` 即可。PDF 是普通 Git 二进制文件；索引提供直接文件链接，无需从 Zotero 再下载。

平台基于 [OSRF VRX](https://github.com/osrf/vrx) Humble，固定上游提交 `dc30ed8d17aa1083fd872edad9c77c69896d2b07`；本项目改动由 `platform/patches/vrx-humble.patch` 与设置脚本复现。

原作者论文的权利归其作者和出版方；本仓库没有为这些文献重新授予许可证。除各组件原有许可证外，项目尚未声明统一开源许可证。

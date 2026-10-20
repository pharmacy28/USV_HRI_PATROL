# main增量审阅：RF合同、第一周准备与Xie证据

- reviewer=main；2026-10-20，Asia/Shanghai。
- 结论：**ACCEPTED（当前方法/协议稿增量）**。原PAPER-20261020-001/R1 ACCEPTED保留；不是最终投稿、线上Overleaf同步或工程/科研实验验收。
- 审阅paper commit：214b2cc96bfb4fec68388322d46b901ed8378b4a；正文提交2d25d26ad029924f6cbb04a5dc0cb69368feca5f，审计88c96f19。
- main.tex SHA256：7292c1a6315aac002ad1214161ba1b1e71aea251742ca427cffd1151ed4a56fc。已比较f8de4da1至该报告提交的三文件增量；不改overleaf母稿或旧review。

## 内容结论

RF对象、真实到达的因果输入、源身份/年龄、同段连续SEARCH标签资格、仅标签双端受限插值、participant/session先分组、同样本RF/保持/CV比较、全尝试/coverage/回退/部署输出均与RF-DATA-CONTRACT-v1一致。未来标签资格未被写成线上准入条件；RF仍为开发候选，无训练成绩、数值冻结或正式协同结果。

Xie新增P/P′/SAD路径、录制轨迹组合对照、漏检后抑制到访的限制与EX-XIE-01—05一致。main另核同hash原PDF第5页对应段，不做本轮全篇重审；没有把组合失败归为孤立预测误差，也未宣称本稿保留belief/full-domain必然及时回访或generator已优于inhibition。

UI/按键/硬件/源记录/导出只写准备要求；004离线与最终runtime、历史API工程验收、正式实验分开。报告快照中004R2尚未运行不当作永久状态；后续constructor预检PASS仍不构成runtime验收。Windows桥接细节留工程计划，不要求为每条通信状态追加论文正文。

## main独立验证

采用精确正文及既有IEEEtran.cls（SHA256 65419311f0bbc0aece1da7ffeddd42736f09c250fedeaa6c7b4ebd062522c352），latexmk/pdflatex关闭shell escape编译PASS。当前**7页**，0 undefined、0 Overfull、9条Underfull；17条引文首次顺序与bibitem一致，无缺失refs或重复label。初次编译因审阅目录缺IEEEtran.cls停止，复用此前同模板类后成功；不归因为正文故障。

7页逐页渲染目视检查：新RF段落/公式/引用可读，无截断、文字重叠或越界；第3/5页有竖向间距，第7页参考文献为左栏且余白较多。保留为终稿压缩/分页优化，不为本次增量重开返修或缩小字体。7页是否满足最终投稿页限尚未裁决。此次PDF SHA256=aa135fcf1eca6998e6b7947a788241ca563aa6aec221b31854984eb63893c00c；不借旧6页检查替代新版证据。

## 后续与停止点

本增量无阻断性内容返修。overleaf在下一次实质更新中合并ACK本review即可，无需另开完整审查。后续只有新工程/数据证据、用户论文修改或投稿目标要求才推进相应修订；不重复全篇审计、文献搜集或编译。线上Overleaf同步仍UNKNOWN。H/年龄/gap/阈值、R/tau/B/人数等保持OPEN，第一周准备与原工程预算不变。

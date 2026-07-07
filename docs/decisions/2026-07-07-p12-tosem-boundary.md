# Decision — P12 (Defect4MR) 与 P3 TOSEM 稿的贡献切分

Date: 2026-07-07 · Status: ADOPTED · Owner: Meng Li

## 背景

P3 TOSEM 稿（SMS 度量论文）的两个最大接收风险是 (a) 外部效度（12 个自建
紧凑核）与 (b) 预注册假设 H1–H4 全部未达标后缺少确认性实证锚点。
P12 仓库（`meng004/P12-Defect4MR`，Zenodo DOI 10.5281/zenodo.21203424）
提供了 35 个 `verified_full` 工业真实缺陷、34 案 × 1124 变异体的预注册
四组研究（T1>B1 过 Holm 校正）以及"KR ≠ MR 质量"的逐案反例。若无明确
切分，把 P12 数据全量并入 TOSEM 稿会掏空 P12 的独立发表价值，并引入
salami-slicing / 自我重叠质疑。

## 决定

**TOSEM 稿（P3）只消费 P12 的结果级产出；benchmark 构建方法学归 P12。**

| 归属 | 内容 |
|---|---|
| **P3 TOSEM 稿可用** | 34 案四组研究的组级统计（Holm p、Cliff's δ、Wilson CI）；30/30 real-defect face 总量；非嵌套反例的**结论级**描述（KR 与真实缺陷检出可给出相反排序）；工业 SMS pilot 的 SSOT（`data/sms_pilot/sms_pilot_ssot.json`，待 P12 侧完成后引用） |
| **P3 TOSEM 稿不得用** | 缺陷挖掘协议、rejected cases、状态治理（phase gates / ledger policy）、复现工具链细节、逐案 verification 报告全文——这些是 P12 论文的贡献主体 |
| **P12 独立贡献** | benchmark 构建与治理方法学（evidence-gated promotion、负面证据登记、两臂复现协议）、数据集本体、kappa 评者材料、工业 SMS pilot（作为 P12 产出之一） |

## 引用与披露契约

1. P3 引用 P12 一律通过 **archived artifact 引用**（Zenodo DOI
   10.5281/zenodo.21203424 + 版本号），不引 GitHub 活动分支；正文数字
   只允许来自 P12 已冻结的报告 / SSOT 文件，并注明版本。
2. references.bib 待补条目（source/references.bib 目前未入库，需在
   作者本机主 bib 中添加）：

   ```bibtex
   @misc{defect4mr2026,
     author       = {Li, Meng and Yang, Xiaohua and Liu, Jie and Yan, Shiyu},
     title        = {Defect4MR: An industrial-grade benchmark of real,
                     reproduced software defects for metamorphic-relation
                     research},
     year         = {2026},
     publisher    = {Zenodo},
     doi          = {10.5281/zenodo.21203424},
     note         = {Dataset and evidence ledgers}
   }
   ```
3. TOSEM cover letter 披露：本稿使用同组维护的 Defect4MR 数据集的
   结果级统计；benchmark 构建方法学将另文投稿（planned P12 paper）；
   两稿贡献不重叠（metric/construct paper vs. benchmark/artifact paper）。
4. 若 P12 论文先进入审稿，P3 修回时同步更新披露状态；反之亦然。
5. 工业 SMS pilot 完成后，P3 只引用其 SSOT 字段与 `generated_at` +
   commit hash（契约见 P12 `docs/sms_pilot/TASK.md` §0），中间日志与
   prompt 记录不进入 P3 正文或附录。

## 边界检查（投稿前自检）

- [ ] P3 正文没有出现 P12 的治理/挖掘/工具链叙述（grep：`phase gate`、
      `candidate mining`、`ledger policy`）
- [ ] P3 中每个 Defect4MR 数字可在 P12 冻结报告或 SSOT 中逐一命中
- [ ] cover letter 含两稿切分披露段
- [ ] references.bib 已含 defect4mr2026 条目且 DOI 可解析

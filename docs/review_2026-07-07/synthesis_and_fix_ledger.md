# C2 模拟评审综合报告与修复台账（2026-07-07）

评审对象：`source/main.tex`（分支 `claude/tosem-submission-review-jjlffi`，
含工业臂重构、amsthm 定理、RQ 重排之后的状态）+ `venues/tosem/` 配套文件。
附录基线：2026-07-06 打包副本（`source/supplementary.tex` 未入库，存在版本滞后）。

五个角色（EIC、方法学 R1、领域 R2、统计 R3、Devil's Advocate）的完整意见
存于本目录 `r0_eic.md` ~ `r4_devils_advocate.md`。五份综合判定：
**Major Revision**（无 desk-reject 级硬伤；诚实基础设施被一致好评）。

## 一、已修复（本轮 commit，全部有 SSOT/数据集冻结文件溯源）

| # | 问题（提出者） | 修复 |
|---|---|---|
| 1 | 陈旧 CI [0.127, 0.740]（R3-B1/DA-4）：误引带 MP 后移的 v4 变体 | 改为 v4_mp5 SSOT 值 [0.014, 0.622]，重写比值评注 |
| 2 | 有效 n "18 (12+6)" 与自报零格数矛盾（R1/DA-3） | 改为 15 (9 aligned 非零 + ≈6 cross 非零) |
| 3 | C1_share 0.164→0.209 双重归因（R1-B4/DA-1） | LRCA SSOT 重算证实为源轴（v3≈0.156→v4≈0.204）；tab:p2-13 行标签改为 v3/v4 pool，校准行单独标注（校准 best=0.200，与 0.209 仅巧合接近） |
| 4 | 工业臂统计不可复现（R3-B2）| 补齐：四组身份（T1/B1/B2/A1）、单侧 Wilcoxon、Holm 家族枚举（T1>B1, T1>A1, B1>B2）、bootstrap CI [+0.029,+0.179]、四组杀伤率 + Wilson CI、敏感性重跑、census 先于比较固定 |
| 5 | 30/30 与 34 案不调和（R3-B3/R1-B5/DA-6） | 数据集 face 表 2026-07-06 已扩至 **34/34**（`REALDEFECT-FACE.md` Totals），论文数字系陈旧；全文 5 处更新为 34/34 并同步 permissions 表 |
| 6 | face 的循环性未言明（R3-B4/R2-B7/R1） | 明确"34/34 为 selection-conditioned，非证据"；证据量改述为同案对照：B1 27/34 全盲、B2 26/34 全盲、A1-a 19/34 丢失 |
| 7 | p=0.046 无脆弱性说明（R3-B5） | 补：效应随 30→34 收窄、敏感性重跑结论不变、census 固定声明 |
| 8 | Abstract "opposite orders/confirming" 超许可（R3-B6/R1-B6/DA-5/EIC-M1） | 两版 Abstract 降格为 "related but distinct constructs / supporting"；"pre-registered" 限定 "in the dataset protocol"（正文、双 Abstract、cover letter 四处） |
| 9 | 结构化 Abstract 只列两个失败阈值（DA-s2） | 改为四阈值全列 |
| 10 | 49.1% 功效误框架（R3-M1） | 三处改述：≈50% 通过率是点估计规则的内禀属性 + 备择形状依赖声明；permissions 行改引小节 |
| 11 | Friedman 标签不一致（R3-M4） | rq3 判定加 "exploratory inferential per permissions 表"；口径统一 |
| 12 | OR 判据退化（R3-M2） | 补非预注册二值化敏感性：nonzero-SMS odds aligned 9/12 vs cross 6/48 → OR≈21，明确标注不作裁决 |
| 13 | "confirming c/d classes"（R3-M5） | → "consistent with" |
| 14 | sign test (df=3) 误称（R3-m1） | pipeline 表改 "directional consistency count (no p-value attached)" |
| 15 | Spearman/Kendall p 值越权（R3-m2） | 删 p 值，标注 descriptive |
| 16 | E1∧E2 偏置方向写反（R1-B7） | "biases high" → "biases low"（等价体误判滞留分母 → 低估充分性），保留 conservative 定性 |
| 17 | Hoeffding 悬空指针（R1-B8） | 指向 supplementary Appendix F.1（与 threats 表一致）；**需 U1 核实附录确有该 bound** |
| 18 | AVP 版本占位符（R1-B9） | 删除 `<AVP-vX.Y>`，改为 frozen dependency + 嵌入源码表述 |
| 19 | LLMorpheus 无中生有句（R2 major/R1-m） | 整段删除（L1893-1901 的 cross-MP 声称）；保留有 estimand 声明的 medium-effect 对照句 |
| 20 | 退化定理定义性（R2-B1） | 补读法声明：替换下为恒等式，a.e. 限定仅涉 E2 分类器；定位为 backward-compatibility characterisation 而非独立数学贡献 |
| 21 | 不可判定性 folklore（R2-B3） | 补 "routine consequence of Rice… not as a novel result"；Budd & Angluin 引用待 U2 |
| 22 | 弱 MR 假阳性不进 SMS（R2 major） | Prop boundary 证明后补 operational 调和段：mode (i) 上游拒斥，仅 (ii) 直接进入 SMS 运算 |
| 23 | certificate ≠ proof（R2 major） | 首个实质使用处加 evidence-record 声明 |
| 24 | HP "categorically unreachable" 过强（R2-B6） | fig3 caption/alt 改为：SI/TF 结构性跨函数，HP 零重叠反映默认值菜单 |
| 25 | 算子族边界渗漏（R2-B5/DA-s6） | decoupling 例子处补 labelling-slack 告知段 |
| 26 | S5 纯度未验证（R2-B4） | 同段补 S5 purity 未经五不变量验证的声明 |
| 27 | 反证标准缺失（R1-B2） | Hypotheses 末补 "What would count against the construct (stated post hoc)" 四条判据，(i) 未测试如实标注 |
| 28 | 24.3 per cell/PUT 混标（DA-7/R1-m） | RQ3 表行改 "Mean mutants / PUT (v4)"【见 wave 校验，若表行未命中已列 U 项】 |
| 29 | 12 vs 13 default operators（DA-s1） | 统一为 13 |
| 30 | Appendix G 指针漂移（DA-s7） | G.2/G.3/G.4 分列 |
| 31 | 0.997 vs 0.996（DA-s3） | 补独立仿真运行说明 |
| 32 | declarations 漏第二 DOI、anonymized mirror、IST 陈旧头注、自引小节（EIC） | 已在 round-1 commit d4ef9ff 修复 |

误报甄别：EIC-B1 "用错模板"（elsarticle 母稿→build.py→acmart 是设计）；
EIC-m6 "Claude Opus 4.6 / GPT-5.4 是虚构版本"（实际使用的真实模型）；
R2 对 Theorem 编号的引用基于旧包（amsthm 转换已完成）。

## 二、需要作者裁决/本机执行（U 台账）

| # | 项 | 来源 | 动作 |
|---|---|---|---|
| U1 | **主/附录失同步**：附录 "verifying H1" vs 正文 H1 不达标；V1-V6 vs V1-V4；D.1 BH-FDR vs 正文无 cell 级校正；B.2 12 vs 13 operators；C1_share 0.200 vs 0.209；G.1-G.3 引理重命名；F.1 Hoeffding bound 是否真实存在；Appendix I face 30→34 | R1 major | supplementary.tex 逐项同步后入库 |
| U2 | references.bib：defect4mr2026 条目；补 Chen 1998/2018、Segura et al. 2016、Liu-Kuo-Towey-Chen 2014、Kanewala & Bieman、Budd & Angluin 1982、DeMillo-Lipton-Sayward 1978；hash 键更名为可读键 | R2-B8/EIC-M4 | bib 入库 + 正文引用点补 \citep |
| U3 | **覆盖矩阵数据冲突**：表体实测 32●●/19●/9○ vs caption 30/24/6 与 "24+18+6=48" 句 | DA-2 | 对照 MR 覆盖设计记录裁决哪侧错，同步下游句子（涉 6 空格进 48 cross 的统计口径） |
| U4 | 预注册可追溯性：正文引用 EXPERIMENT_DESIGN.md@commit-hash 或 Zenodo 冻结件 | R1-B1 | 决定披露形式并加引 |
| U5 | v4 无评审池上 L0/C5 归因如何执行 | R1-B11 | 正文补一句实际流程 |
| U6 | 空格敏感性：排除 6（或 9）个 vacant cells 重算 δ | R1-B10 | 本机跑脚本，结果进 Appendix |
| U7 | Δδ=−0.009 的 CI 端点打印（三处 "CI covers zero"） | R3-M3 | 从分析日志取端点写入 |
| U8 | 37 operators vs 36 对（+CF?）核对 | DA-s4 | 一句话调和 |
| U9 | fig2/fig3 重新生成（MP 轴名 + caption 措辞已改） | — | 本机 matplotlib |
| U10 | primary-MP 撤回分析的 permutation-null 细节补 Appendix 指针 | R1 major | 补指针或数字 |
| U11 | Romano 2006 vs Vargha-Delaney 作为 0.474 锚（决策） | R2-m | 作者定夺 |
| U12 | 是否把逐案反例（如 mutant 面 B1>T1 而真实缺陷面反转的案例）写进正文（决策） | 我方建议 | 若写，从 Appendix I 案名中取 |
| U13 | Results 冗余合并：mixed-effects 三处、H3 两处、protocol-asymmetry 三处 | EIC-M3 | 页数预算内合并 |
| U14 | 重建 + 双遍 xelatex + 页数复核（本轮加了约 1 页文字） | — | CLAUDE.md §3 流水线 |

## 三、Reviewer 2 视角的最严苛审稿意见（ARS 强制输出）

- [致命问题 1] 预注册声明不可追溯（U4）：全文以 "pre-registered" 为论证支点却无一处可验证的注册工件引用；在 U4 关闭前构成 publication blocker。
- [致命问题 2] 主/附录在假设判定上直接矛盾（U1 的 "verifying H1" 项）：若按当前附录提交，审稿人将读到 H1 同时"验证"与"不达标"，属一票否决级内部矛盾。
- [致命问题 3] 覆盖矩阵表体与 caption 的 60 格三分类不一致（U3）：涉及 48-cell cross 口径的构成，未裁决前 H2/H4 的分母叙述不可信。

（其余四维度——外部效度、统计选择偏差、benchmark 公正性、霍桑效应——经本轮修复后无新增 blocker；外部效度的 SMS×工业空格由 P12 pilot 关闭中。）

## 四、状态

- 本轮修复 commit：见 git log（quick-fix d4ef9ff + 本 synthesis commit）。
- U1–U3 关闭前不满足投稿条件；U4–U14 属修回弹药与打磨。
- C1（SMS pilot 段落接入）待 P12 SSOT 通知。

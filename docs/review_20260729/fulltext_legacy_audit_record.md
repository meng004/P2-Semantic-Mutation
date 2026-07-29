# 全文旧版本残留独立审计与修复记录（2026-07-29）

- 触发：作者指令“针对老版本残留问题，请全文独立审计”，随后指令
  “以 source/main.tex 及 supplementary.tex 为唯一可信来源，立刻修复”。
- 审计架构：三个互相隔离的只读审计线程（形式链 / 实证叙事 / 机械残留），
  主线程逐条取证复核后合并裁定；三线程初裁均为 **BLOCKED**。
- 根因裁定：仓库存在**三个失同步的“真源”**——`source/*.tex`（含
  2026-07-07 评审修复、缺理论层）、`submission/TOSEM_regular_20260706/*.tex`
  （含 T6 理论、实证口径停在 07-06）、以及更陈旧的已编译 PDF；
  `venues/tosem/build.py` 从 source 再生会回灌全部旧符号与旧命题。

## 一、修复策略（作者裁定）

`source/main.tex` + `source/supplementary.tex` = SSOT。全部修复落 source，
再由 `venues/tosem/build.py --track regular --date 20260729` 重建投稿包
`submission/TOSEM_regular_20260729/`（xelatex×3+bibtex，acmart）；
被污染的 `TOSEM_regular_20260706/` 整目录移除（git 历史可恢复）。

## 二、发现与处置总表

数字类更正一律由 `scripts/audit_fix_numbers.py` 从冻结 SSOT 重算
（`data/results/audit_fix_numbers.json`），不采信任何人工转抄。

### 形式链（初裁 BLOCKED；最小 blocker 集 4 项 + majors）

| 发现 | 处置（source 落点） |
|---|---|
| 二态 admission 与三态并存（E1∧E2 既入 equiv 又称 unresolved） | 词汇区改四分解（certified/killed/survive/unresolved）+ strict/cons 双读法；E1∧E2 程序步改“Status routing→UNRESOLVED”；向后兼容声明改“三态为 equiv 的细化”；A.1 骨架同步 |
| semantic mutant 三套定义 | S1–S5 定为规范定义；(a)–(c) 降为生成期启发；E1/E2 定位为等价状态证据（三处声明句） |
| Lemma G.2 接口偷换（identity MR 无跨程序 oracle） | L4 重定义为 **reference-anchored** 身份关系 MP_eq^{S_i}（r=id ∧ R≡= ∧ 对照原程序记录输出）；G.2 表、G.3 证明、主稿 bullet 三处同步；Lemma G.1 的 E1 论证随之改为“同一等式检验”而非“平凡恒真” |
| Lemma G.1 量词域不闭合 | 支撑假设 supp(𝒟_P)⊇X_adm 入引理与定理陈述；例外集改名 𝒩_exc；有限域 a.s. 穷尽 / 连续域 a.e. 两支分开；补支撑假设不可去反例；退化等价明确读在 X_adm∖𝒩_exc |
| 语义-effect fiber 与 kill set 同名冲突 | F(MR) 改名 detection/kill set 𝒦(MR)，fiber 保留给 eff 原像 |
| eff 非全函数（多重违规/ψ6 无值） | eff 值改为“翻转 strata 集合”；singleton=ψj-viol；多重违规不属任何单类（入 ξ 偏差质量）；按 Ψ 参数化 |
| Theorem 2 过强（"exactly"）+ 缺有效性前提 | “supported only on” + 陈述加 valid-MR 前提 + 单侧性注记 |
| 窗口定理承重假设缺失、2η̄ 硬编码 | Prop(boundary) 原位升级为 detection-window 定理：H-a/R1/H-d 入陈述、P⋆=原程序、预算参数化为 p·η̄（p=2 成对、p=4 收敛关系）、REM-FPOS 分层化（μ_r<−pη̄ 存在性条件）、REM-FNEG 侧条件；G.8 全套假设/regime/证明 |
| 区间/缺口定理缺失于 SSOT | 新增 §interval（witness 引理 + n≥1 区间定理）与 §gap（exact checker、closure 引理、block 定理、cross-zero 推论、ξ 定义含 NA+单侧、辨识 Remark）；G.6/G.7 完整证明；G.5 独立审计说明 |
| Hoeffding 悬空引用 | 正文 E1∧E2 段内联给出 (1−p0)^K≤e^{−K·p0} 界并指向 F.1（F.1 原有推导保留，𝒟_P 改名） |
| N 符号冲突（重复次数 vs 例外集） | 例外集 → 𝒩_exc |
| AVP 三参数声明 vs 两参调用 | A.1 增加缩写约定 AVP(s,mr):=AVP(s,mr,ε^k_AVP) |
| E1∧E2 偏置方向正文/附录相反 | 统一为 biases **low**（误判非等价滞留分母为不可杀幸存者）；A.3 表同步 |

### 实证叙事（初裁 BLOCKED；最小 blocker 集 6 项 + majors）

| 发现 | 处置（重算值） |
|---|---|
| 60-cell 无 operator 轴，(i,k,j)/j=k 不可识别 | 评估单元改 (i,k)+混合池分母；j=每 mutant 生成期 fiber 标签；aligned ⇔ k=k⋆(i)（class-primary）；align(j)=j 保留为设计映射并加“标签非轴”说明；SMS_{i,k,j} 全文清除 |
| H2 表拼接 MP1/MP5 口径 | 表改冻结 MP5 口径 0.213/0.100 vs 0.077/0.000；zero 结构 6/12 与 39/48；有效 n=15（6+9）；二值化 OR 21→4.3；0.275/0.061 标注为已撤回配置 |
| H1 表为 pilot 口径（4/5/9/5/1，“仅 HP 过线”） | v4 确认非等价口径 CE7/OS7/HP8/TF6/SI4 → **0/5 过线**（HP 最高 8/12）；旧表明示废止；applicability 视图改 7/8·7/7·8/9·6/6·4/6 |
| H3 倒置类写错（b） | 改 **c 类**（v3 −0.058 / v4 −0.028；a/b/d 为正）；CV 1.36/1.10 落数 |
| H4 estimand 未定义（zero-kill 强置 suspect=1 得 0.791） | 判定改 **not evaluable as pre-registered**：45/60 格 NA；敏感区间宏 0.163–0.186 / pooled 0.188–0.235 跨阈值两侧；0.791 明示撤回；12/15 可评估格 ≤0.20（5 aligned+7 cross）；D.2 扫描表重基；permissions 行、结论、Abstract 同步 |
| ξ 被宣称报告但不存在 | 实测并报告：ξ_pooled=117/153=0.765（aligned 0.723 / cross 0.795；45 格 NA；对角质量集中 CE/OS）——作为 block 定理的模型检验结果诚实呈现，并解释与 LRCA C1=81% 的互补性（fiber 标签失配 ≠ 非语义 kill）；SSOT `xi_exactness_defect_v4.json` |
| Friedman/PC/类内例子混 v3 | Friedman 主报 v4 16.76/0.0022（v3 15.30/0.0041 并列）；秩均值/每类校正 p/W 换 v4；PC mean 0.750、类内模式改“b 反向、c 正向，不稳定”；E.2/stakeholder 基线 0.275→0.213 |
| PINN 案例与弱-MR 语义矛盾 | 重述为 MR-validation reject（不入 kill 计数），表格 verdict 同步；RNG 案例接 window 定理 (ii)+repeat 处方 |
| “operator-MP alignment 必要” 超证据 | 改为本设计内的关联性结论 + 引 ξ 审计明示理想前提不成立 |
| LOC 表虚（60–400/50–400） | 实测 19–35 LOC（0.6–1.2 KB）落表；B.1(d) 同步 |
| u=0 无版本限定 | v4 限定；v3 补 10 格/80 起 unresolved census（全零杀格，端点重合） |
| SMS_unfiltered 恒等变体 | D.1 删除并说明；主稿 pipeline 句改写 |
| B.2 “12 default operators” | 统一 13（与 B.6 清单一致） |

### 机械残留（初裁 BLOCKED）

| 发现 | 处置 |
|---|---|
| source/ 会再生全部旧符号/旧命题（build 回灌） | source 即本轮修复对象；重建后包内 grep 全零 |
| 附录双重编号（A A. / B.2 B.1.5） | source 标题本就无手写字母，重建自愈；PDF 抽查单字母 ✓ |
| 陈旧 PDF（旧 RQ1/D_S/Proposition 2 可见） | 重建生成新 PDF；pdftotext 抽查旧标记 0 命中 |
| 跨行 `Proposition\n2(ii)` 漏检 | 修复后以 multiline grep 复验 = 0 |
| 失效节引用/图号 | source 全 \ref 化（0 undefined references） |

## 三、重建验证（submission/TOSEM_regular_20260729）

- xelatex×3 + bibtex：**0 errors，0 Missing character，0 undefined references**；
  main.pdf + supplementary.pdf（25 pp）+ clean.zip 产出。
- 包内 tex 与 PDF 文本：`Proposition 2`（含跨行）、`D_S`、语义 α/σ、
  `SMS_{i,k,j}`、双重附录编号 —— 全部 0 命中；
  新标记（detection-window 定理、not-evaluable H4、ξ=0.765、
  reference-anchored oracle、soundness/monotonicity RQ1）全部在位。
- 定理编号由 acmart 自动分配（Theorem 3.1–3.11 系列），交叉引用零失效。

## 三-b、独立复核（修复关闭验证）

修复后由全新只读验证线程按 18 项清单复核（agent 702f13cf）：首轮 17/18
CLOSED，揪出两处残余——M:3044 的 b-class 残句、附录小节层级致实编与主稿
硬写指针漂移（B.1.5/C.4 系）——以及 MR_eq/MP_eq 记号一处不一致；三处均已
修复（子小节降级使实编 B.1–B.6 / C.1–C.3 与指针逐一对应）并重建包复验。
终裁：**FIX-VERIFICATION PASS**（0 error / 0 Missing character /
0 undefined reference；唯一告警为良性 TU/inconsolata 斜体字形替换；
提交 PDF 已收敛，49 页）。

## 四、遗留与边界

- `submission/` 下其余历史包（arxiv-*、IST/JSS、TOSEM_regular_20260705、
  TOSEM_fastimpact_20260707）为带日期历史快照，含同源旧口径，
  不在本轮修复范围；任何再投稿必须从 source 重建。
- `theory_drafts/*.md` 为理论线历史工作底稿（含旧标签与旧行号注记），
  权威版本以 source 为准；registry 已加 SSOT 切换注记。
- H4 的重新预注册 estimand、ξ 的 dose-response 消费、operator 分层重跑
  （恢复真 (i,k,j) 轴）列为后续工作。

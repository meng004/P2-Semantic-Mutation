# P2 实验详细说明

**项目**: When Same-Prompt LLM Source Diversity Doesn't Help — Semantic Mutation Operator Ablation in Metamorphic Testing for Single-Output Scientific Computing Kernels
**当前阶段**: IST submission ready (v4 cross-source primary)
**最后更新**: 2026-05-02
**作者**: Meng Li (mlemon@usc.edu.cn)

> 本文档面向"理解实验全貌"的读者。复现操作请读 `QUICK_START.md`；原始数据清单请读 `DATA_README.md`。

---

## 1. 研究问题（Research Questions）

| RQ | 内容 | 操作化定义 | SSOT 字段 |
|----|------|-----------|-----------|
| **RQ1** | 60 个单元格上 inst_rate / equiv_rate / C1_share / survive_rate 的分布 | 每个 (PUT, MR-pattern) 单元格的 4 项描述统计 | `paper_numbers_v4.json::rq1` |
| **RQ2** | 算子-MR 对齐切片（j=k）vs 交叉切片（j≠k）的 SMS 差异结构 | MP5 frozen-primary Cliff's δ + 95% CI；MP1/data-driven contrast retained as sensitivity | `paper_numbers_v4.json::rq2_primary_mp5`（H2 verdict）; `::rq2`（sensitivity） |
| **RQ3** | 12 个 PUT × 5 个 MP 的 MP-rank 差异 | Friedman χ² MP-rank 检验 + per-class Bonferroni × 4 多重校正；不是 H4 verdict | `paper_numbers_v4.json::rq3` |
| **RQ4** | SMS 与简单模式覆盖率（pattern coverage）的实证关系 | Spearman ρ + Kendall τ 排序相关 | `paper_numbers_v4.json::rq4` |

## 2. 评价指标（Evaluation Metrics）

### 2.1 主指标 — Semantic Mutation Score (SMS)

```
SMS_{i,k,j} := |killed_{i,k,j}| / (|mut_j(S_i)| − |equiv_{i,k,j}|)
            =  |killed_{i,k,j}| / (|killed_{i,k,j}| + |survive_{i,k,j}|)
            ∈ [0, 1]
```

- `i ∈ I` PUT 索引（|I|=12）
- `k ∈ {1,...,5}` MR 模式（MP_1 ... MP_5：守恒/单调/收敛/轨迹/偏序）
- `j ∈ {1,...,5}` 算子（mut_C/mut_M/mut_G/mut_T/mut_F）
- `equiv` 由 E1（AVP-coherent）∧ E2（K_eq=1000 输入下输出等价）双重判定

SMS 与 Jia & Harman (2011) 经典 MS 的退化关系：在 §9.1-§9.4 形式化的退化极限 `L = L_equiv ∧ L_killed ∧ L_mut` 下，SMS 几乎处处（modulo D_S 测度零集）退化为 MS（Theorem 9.1 + Corollary 9.1）。

### 2.2 辅助指标（LRCA Engineering Attribution Layer）

| 指标 | 定义 | v4 实测值 | 含义 |
|------|------|-----------|------|
| `C1_share` | 真语义错误占 killed 的比例 | mean=0.2092 | 算子-MR 对齐质量 |
| `suspect_share` | C2/C3/C4/C5 占 killed 的比例 | mean=0.7908 | 噪声水平 |
| `equiv_rate` | E1 ∧ E2 等价占总 mutant 的比例 | per-cell variable | 等价 mutant 率 |
| `inst_rate` | 实例化 mutant 占 generated 的比例 | per-cell variable | LLM 产出有效率 |

LRCA 三层分类器（layered_root_cause_analysis）：

- **L0 prescreen**: lint + type check + unit self-test + AVP-baseline-failed → 排除 mutator artifact
- **L1 statistical**: ε_AVP 容忍带内 → C2 tolerance perturbation
- **L2 OOD**: D_S 外采样触发 → C3 OOD
- **L3 distribution-violation**: C4 statistical-assumption violation
- **leftover** → C1 真语义错误

实现：`scripts/run_lrca.py`，校准：`scripts/calibrate_lrca.py`，输出：`data/results/lrca_60cell_v4.json`。

### 2.3 效应量指标

- **Cliff's δ**: 非参排序效应量，阈值 0.147 / 0.330 / 0.474（Romano 2006 small/medium/large）
  - 95% CI 用 BCa bootstrap (B=10000)
  - 实现：`scripts/compute_rq2.py`
- **Vargha-Delaney Â₁₂** = δ/2 + 0.5（参考报告，未作主指标）
- **Friedman χ²**: MP-rank 差异（n=12 PUT × 5 MP treatments；exploratory, not H4 verdict）
  - 实现：`scripts/compute_rq3_friedman.py`
- **Spearman ρ / Kendall τ**: 排序相关（RQ4）

### 2.4 受规约外指标（不入主表，仅 §6.2 描述）

- **零质量比例**（zero-mass cells）：60 单元格中 SMS=0 的比例 = 45/60 = 75%（v4）
- **C3_MP1 vs C3_MP5 不对称**：post-hoc v3b primary MP shift 的判定锚点

---

## 3. 实验对象（Experimental Subjects）

### 3.1 12 个 PUT（Programs Under Test）

按四类切分（`cls : I → {A, B, C, D}`），每类 3 个 PUT：

| 类 | PUT | 长度 | 信号语义 | 文件 |
|----|------|------|---------|------|
| **A** numeric | A1 | < 2 KB | Gaussian elimination (det) | `src/puts/a1.py` |
|   | A2 | < 2 KB | Newton's method scalar root | `src/puts/a2.py` |
|   | A3 | < 2 KB | Trapezoidal integral | `src/puts/a3.py` |
| **B** probabilistic | B1 | < 2 KB | Reservoir sampling | `src/puts/b1.py` |
|   | B2 | < 2 KB | Geometric distribution sampler | `src/puts/b2.py` |
|   | B3 | < 2 KB | Welford running variance | `src/puts/b3.py` |
| **C** surrogate | C1 | < 2 KB | Polynomial fit predictor | `src/puts/c1.py` |
|   | C2 | < 2 KB | RBF kernel surrogate | `src/puts/c2.py` |
|   | C3 | < 2 KB | Cubic spline interpolation | `src/puts/c3.py` |
| **D** ML | D1 | < 2 KB | Logistic regression `predict_proba` | `src/puts/d1.py` |
|   | D2 | < 2 KB | k-NN single-prediction | `src/puts/d2.py` |
|   | D3 | < 2 KB | Linear SVM scalar projection | `src/puts/d3.py` |

PUT 选取原则（详 §3.1.1 of paper）：

1. **Numerical Recipes 章节锚定** —— A/B/C 三类映射到 NR 第 2/7/9 章主题
2. **Single-output `float → float` 标量映射** —— 排除多输出耦合，控制 SMS 公式分母维度
3. **< 2 KB / 函数** —— 控制 LLM context window，保证 mutant generation 一致性
4. **公开标准库可重现** —— 不依赖企业代码或闭源数据集

### 3.2 5 个 MR 模式（Meta-Patterns，由 P1 提供）

| MP | 名称 | 验证方法 |
|----|------|---------|
| MP_1 | Conservation 守恒 | `‖f(x) - f(T(x))‖ ≤ ε` |
| MP_2 | Monotonicity 单调性 | `(x ≤ y) ⇒ f(x) ≤ f(y)` 双向 |
| MP_3 | Convergence 收敛阶 | `f(refined_x) - f(coarse_x)` 收敛阶估计 |
| MP_4 | Trajectory 轨迹 | `f(x_seq)` 时间序列形状不变量 |
| MP_5 | Partial-order 偏序 | 用例 lattice 上 monotonicity |

每个 PUT 由 P1 提供 5 个 MP 的实例化 MR 集 `MR_{i,k}`，60 个 (PUT, MP) 对应 60 个单元格。

### 3.3 5 个语义算子（mut_C/M/G/T/F = CE/OS/HP/TF/SI）

5 个 meta-mutation operator classes（§3.2 of paper）：

| 算子 | 简称 | 含义 | 跨函数边界？ | 携带领域知识？ | 改算法类？ |
|------|------|------|-------------|---------------|-----------|
| mut_C | CE | Conservation Erosion | △ | ✓ | △ |
| mut_M | OS | Operator Substitution | ✓ | ✓ | △ |
| mut_G | HP | High-order Perturbation | ✓ | ✓ | ✓ |
| mut_T | TF | Trajectory Flip | ✓ | ✓ | ✓ |
| mut_F | SI | Sign Inversion / Stability injection | ✓ | △ | ✓ |

定义来自 §3.2.0 必要条件 (a) 跨函数边界替换 / (b) 携带领域知识 / (c) 改变算法类（详 paper Layer 1）。

### 3.4 比较基准（Baselines）

| 基准 | 工具 | 算子集 | 用途 |
|------|------|--------|------|
| **B0 — 经典语法变异** | cosmic-ray (Bingham 2015-) | AOR/SDL/COR/ROR 等 first-order syntactic | §3.2.6.3 AST overlap 对比 |
| **B0' — 备选语法变异** | mutmut (Hovmöller 2016-) | first-order syntactic | §5.10 计划对照（未实施，列为 R12 残余威胁） |
| **B1 — v3 same-source LLM** | Claude Opus | 5 个语义算子 | 主要预注册基准 |
| **B2 — v3b same-source + data-driven primary MP** | Claude Opus | 5 个语义算子 | 探索性消融 |
| **B3 — v4 cross-source LLM pool** | Claude + GPT + DeepSeek | 5 个语义算子（同 prompt） | 主要本文实验 |

---

## 4. 实验方法（Experimental Method）

### 4.1 Pipeline 五步骤

```
Step 1. operator_campaign  → 60 cells × N_avp=20 trials × 3 LLMs = ~10,800 候选 mutants
Step 2. mutant prescreen   → V1-V4 mechanical-validation gate（语法/类型/单元自测/AVP-baseline）
Step 3. equivalence detect → E1 (AVP-coherent) ∧ E2 (K_eq=1000 output-equivalent)
Step 4. SMS computation    → killed / (mut_total - equiv) per cell
Step 5. LRCA classification → C1/C2/C3/C4/C5 attribution
```

**v4 cross-source 实施细节**（`scripts/cross_source_campaign.py`）：

- 每个 (PUT, operator) 在 Claude Opus 4.6 / GPT-5.4 / DeepSeek-chat 上分别运行 K=3 trials
- **prompt 完全一致**（temperature=0.7, identical template, no source-specific tuning）
- 总 attempts: 37 operators × 3 sources × 3 trials = 333；V1-V4 通过率 89%；最终 confirmed mutants = 298（Claude 101 / GPT 98 / DeepSeek 99）
- API 经 BLTCY 代理 + DeepSeek 直连（详 `MEMORY.md::project_api_config.md`）

### 4.2 三阶段消融（Three-Stage Ablation）

| 变体 | LLM 源 | Primary MP（c-class） | 主要变量 | SSOT 文件 |
|------|--------|---------------------|---------|-----------|
| **v3** | Claude Opus only | MP_5（c-class，预注册）| 同源 baseline | `paper_numbers_v3.json` |
| **v3b** | Claude Opus only | MP_1（数据驱动 post-hoc）| 隔离 MR-MP 设计贡献 | `paper_numbers_v3b.json` |
| **v4** | Claude + GPT + DeepSeek | MP_1 | 隔离 LLM-source diversity | `paper_numbers_v4.json` |

**关键约束（§3.4）**: v3b 的 c-class MP shift 是 selection-on-the-response（post-hoc），用 cross-cell exchangeability permutation null + Bonferroni × 5 quantification 报告，仅作 exploratory，不作主要 verdict。

### 4.3 等价性判定（Equivalence Detection — E1 ∧ E2）

```
E1 AVP-coherent:  ∀ mr ∈ MR_{i,k}: AVP(S_i, mr) = AVP(s', mr)
E2 Output-equiv:  ∀ x ∈ X_{K_eq} ~ D_S: ‖S_i(x) − s'(x)‖ ≤ ε_eq
                  K_eq = 1000, ε_eq = 1e-9 (科学计算缺省)
```

E1 单独（保守）/ E2 单独（激进）/ E1∧E2（折衷）的三方权衡见 paper Appendix A.3。本文采用 E1∧E2 作为「conservative complete instantiation of necessary conditions」。

实现：`scripts/probe_equiv.py`。

---

## 5. 实验结果（Experimental Results）

### 5.1 RQ1 描述统计（v4 primary）

```
n_cells                = 60
mean_sms               = 0.104
median_sms             = 0.000
std_sms                = 0.213
n_zero_sms             = 45     ← 75% 零质量
mean_c1_share          = 0.2092
mean_suspect_share     = 0.7908
H5 (suspect ≤ 0.20)    = 12/60 cells pass (20%)
```

### 5.2 RQ2 算子-MR 对齐（v4 primary MP5）

```
n_aligned (j=k)        = 12
n_cross (j≠k)          = 48
mean_aligned           = 0.2133
mean_cross             = 0.0767
Cliff's δ              = 0.3142
95% CI                 = [0.0138, 0.6215]
H2 threshold (δ≥0.474) = NOT MET (point estimate)
MP1 sensitivity δ      = 0.4392, 95% CI = [0.1267, 0.7396]
```

**Stipulated-alternative power simulation**（`scripts/compute_rq2_power_stipulated.py`）:

- 给定 MP1 sensitivity δ_truth = 0.474（large-effect boundary），用 mixture-weight 构造 calibrated alternative
- (n_aligned, n_cross) = (12, 48) 设计在该真值下的 MP1 sensitivity point-estimate power = **49.9%**
- CI-lower power = 86.8%
- 论文表述: "H2 not met under point-estimate criterion" 是事实判定，不是 effect-size claim

### 5.3 RQ3/RQ5 MP-rank analysis（v4 primary）

```
class_mean_a (numeric)        = 0.0667
class_mean_b (probabilistic)  = 0.1478  ← 最高
class_mean_c (surrogate)      = 0.0894
class_mean_d (ML)             = 0.1122
sign_test_aligned > cross     = 4/4
Friedman χ²                   = 16.76
Friedman p                    = 0.0022 (MP-rank effect; not H4 verdict)
Per-class p:
  a = 0.406, b = 0.035, c = 0.231, d = 0.287
```

主模型 mixed-effects（`scripts/compute_rq3.py`）汇报「Singular matrix」失败，回退 fallback 模型 `sms ~ C(class) + C(operator) + (1|put)` 报告。Friedman 检验作为 robustness check 显著。

### 5.4 RQ4 SMS vs pattern coverage（v4 primary）

```
n_puts                 = 12
Spearman ρ             = 0.1628
Spearman p             = 0.6133  ← 不显著
Kendall τ              = 0.1357
Kendall p              = 0.5677
mean pattern coverage  = 0.75
```

**保守表述**（§5.7.3）: SMS 与 pattern coverage 显示近乎零的排序相关，统计 power 不足以支持 "orthogonal" claim。

### 5.5 §3.5 AST overlap 实证（语义 vs 语法）

```
P2 mutants total    = 292    (12 PUTs × ~24.3 mean)
Cosmic-ray total    = 1,250  (12 PUTs，AOR/SDL/COR 混合)
Overlap             = 15
Overall overlap rate = 5.14%

Per-class overlap:
  CE: 5/64  =  7.81%   ← 部分重合（最简单替换）
  OS: 7/60  = 11.67%   ← 部分重合（API substitution 边界）
  HP: 0/72  =  0.00%   ← 语法工具不可达
  TF: 0/54  =  0.00%   ← 语法工具不可达
  SI: 0/33  =  0.00%   ← 语法工具不可达
  CF: 3/9   = 33.33%   ← 类特化算子（不在主 5）

Categorically unreachable (HP+TF+SI): 159/292 = 54.5% of P2 pool
```

证据强度：5 类中 3 类 (HP/TF/SI) 0/0/0 完全不可达，构成 §3.2.6 "P2 mutant pool 不是语法 mutant pool 子集" 的实证 witness。

实现：`scripts/p2_vs_syntactic_ast_diff_batch.py`，AST 归一化用 `ast.dump(annotate_fields=False, include_attributes=False)`。

---

## 6. 多轮迭代与核心指标变化（Iteration Trajectory）

### 6.1 五轮迭代时间线

| 轮次 | 时间 | 数据集 | 核心动作 |
|------|------|--------|---------|
| **R0 pilot** | 2026-04 | 4 PUT × 5 MP 手工 | pipeline validation only（不入论文，DEPRECATED） |
| **R1 v3** | 2026-04-25 | 12 PUT × 5 MP × 1 LLM (Claude) | 主要预注册基准 |
| **R2 v3b** | 2026-04-28 | 同 v3, c-class primary MP shifted (MP_5 → MP_1) | post-hoc data-driven |
| **R3 v4** | 2026-04-29 ~ 04-30 | 12 PUT × 5 MP × 3 LLMs (Claude+GPT+DeepSeek) | cross-source 消融 |
| **R4 IST trim** | 2026-05-01 ~ 05-02 | 同 v4 数据，论文 26k → 9.5k+6k 字 | IST 投稿包 + 5 reviewer revision |

### 6.2 核心指标轨迹

| 指标 | v3 | v3b | v4 | Δ(v3→v3b) | Δ(v3b→v4) |
|------|----|----|----|-----------|-----------|
| **mean_c1_share** | 0.1643 | 0.1643 | **0.2092** | 0 | +0.045 |
| **mean_sms** | 0.0875 | 0.0875 | **0.1040** | 0 | +0.017 |
| **rq2 primary MP5 Cliff's δ** | 0.323 | — | **0.314** | — | — |
| **rq2 MP1 sensitivity Cliff's δ** | 0.323 | 0.446 | **0.439** | +0.123 | −0.007 |
| **rq2 primary MP5 mean_aligned** | 0.183 | — | **0.213** | — | — |
| **class_mean_c** | 0.0467 | 0.0467 | **0.0894** | 0 | **+0.0427 (+91.4%)** |
| **rq4 spearman_p** | 0.741 | 0.741 | **0.613** | 0 | −0.128 |

**关键观察**：

1. **MR-design 是主驱动**: v3 → v3b 仅做 c-class primary MP 数据驱动切换（MP_5 → MP_1，同源数据）就把 δ 从 0.323 拉到 0.446（+0.123）。
2. **LLM-source diversity 不是主驱动**: v3b → v4 加 3 个 LLM 池 cross-source（同 prompt），δ 反而掉 0.007（CI 覆盖零），但提高 c-class SMS +91.4% 与 c1_share +27%。
3. **结论**（§5.7.2 / §6.1）: 在相同 prompt 下，**MR-design 而非 LLM source diversity 是 aligned-vs-cross 效应量的主导杠杆**。

### 6.3 5-Reviewer Revision 轮次（IST submission tailoring）

| 轮次 | 关注点 | 变化 |
|------|--------|------|
| **Round 1** | 5 reviewers full review | Major Revision，roadmap 28 items |
| **Round 1.5** | 15/28 items closed | Minor Revision tier reached |
| **Round 2** | re-review B/C/D groups | All Minor closed except R3 Perspective D-6 |
| **Round 3** | R3 D-6 verification | D-6 score 3/10 → 6/10，dissent withdrawn |
| **Stage 4.5** | final integrity (3 P0 found) | Tip 2024 / DeepCrime / cosmic-ray total fixed |
| **Stage 4.5 round-2** | re-verify | PASS_WITH_NITS（0 P0 / 0 P1） |
| **ROI-3 ref audit** | reference forensic | 3 软件工具作者捏造 → fixed |

详见 `docs/review_2026-05-{01,02}/*.md` 全套 review reports。

---

## 7. 方法、实验的优势与局限性（Discussion）

### 7.1 优势

1. **退化定理保证向后兼容**: SMS → MS 在严格定义的退化极限（§9.1-§9.4 + Theorem 9.1 + Corollary 9.1）下几乎处处成立，因此 SMS 不是另起炉灶的 ad-hoc metric，而是 Jia & Harman 经典 MS 的严格推广。
2. **三层方法骨架解耦**: Layer 1 定义性（§3.2.0 必要条件）/ Layer 2 操作性（§2.3 E1∧E2）/ Layer 3 应用性（§3.5 12-PUT 实证）三层独立验证；§5 60-cell 实证只是 Layer 3 的展示样本，不是论文主贡献。
3. **AST 实证锚定不可达性**: §3.2.6.3 实测 5.14% overall AST overlap；HP/TF/SI 3 类（54.5% pool）0/0/0 完全不可达，为 "P2 不是语法 mutant pool 子集" 提供阳性实证。
4. **三阶段消融分离 MR-design 与 LLM diversity**: v3 → v3b → v4 三套数据，独立报告 v3 → v3b（+0.123）与 v3b → v4（−0.007）两个 contrast，避免被合并为单一 ratio claim。
5. **Stipulated power 校准敏感性表述**: 49.9% point-estimate power 直接量化 "(n_a=12, n_c=48) 设计在 MP1 sensitivity δ_truth=0.474 真值下的检出概率"，避免把 "not met" 误解为 effect-size 否决；它不是 frozen-primary MP5 的 H2 功效。
6. **诚实承认 selection-on-response**: §3.4 v3b c-class primary MP shift 用 cross-cell exchangeability permutation null + Bonferroni × 5 量化披露，不为切换 primary 做事后辩护。
7. **LRCA 三层分类降噪**: C1/C2/C3/C4/C5 attribution 把 "killed" 进一步分解，避免把 tolerance perturbation / OOD / noise 混入 SMS 分子。
8. **Reproducibility-first**: 60-cell 全 SSOT JSON 持久化（`data/results/*.json`），全 mutant pool 提交（`data/mutants/*_pool_v4/`），cosmic-ray sqlite 备份（`data/results/cosmic_ray_*.sqlite`）。

### 7.2 局限性

1. **范围受限于 single-output `float→float`** (§7.1, R-1)：12-PUT 全部是科学计算 toy kernel，工业级（NPP / 航空 V&V）转移留 P5。
2. **5-MP 集闭合假设** (§7.1, R-3)：Open-extensible 但未实证 6th MP 的边际收益。
3. **K_eq=1000 / ε_eq=1e-9 为科学计算缺省**：不同领域可能需要不同 ε（§7.2, R-7）。
4. **HOM 等价性未实证** (§7.4, R-12 NEW)：Jia & Harman (2009 IST) HOM 在原则上可能模拟部分 OS/HP/TF/SI 效果，本文 §3.5 AST overlap 严格限于 first-order syntactic tools，HOM 测试列残余威胁。
5. **N=20 AVP repetitions** (§7.3, R-9)：power 简化模拟假设，更复杂的 ε_AVP 分布敏感性未做 robustness sweep。
6. **v3b post-hoc selection confound**：尽管用 permutation null + Bonferroni 量化披露，仍是 selection-on-the-response，不能与预注册 v3 verdict 等同视之。
7. **LLM 输出不确定性** (§7.4, R-11)：temperature=0.7 + 3 trials 平均化降低方差，但 LLM 长尾 mode 可能在更大 K 下重新出现。
8. **mutpy 不可比较**：Python 3.10+ 不兼容（科学计算依赖 sklearn/scipy），R12 残余威胁。
9. **Pitest 跨语言不可比较**：Java 工具，本文 12 PUT 全 Python，留 P3 Java port 时再做。
10. **未校准对应于工业实测的 inter-rater 信度**：LRCA 标注由作者一人完成，未做第二评审者 κ 一致性检验（P3 plan）。

### 7.3 与 P1 / P3 / P4 / P5 的边界

| Paper | 贡献 | 状态 |
|-------|------|------|
| P1 (SANER 2027) | MR meta-pattern 实证审计（同 12 PUT 基础设施） | under review |
| **P2 (this paper, IST)** | SMS 度量 + 三层方法骨架 + 60 单元格审计 + 三阶段消融 | IST submission ready |
| P3 (planned) | 工业级 Java/C++ port + LLM-mutant inter-rater κ + Pitest 对照 | TBD 2026Q3 |
| P4 (TOSEM-aimed) | minimal MR-subset existence + reachable adequacy + three-pillar coupling 形式定理 | drafting |
| P5 (Nuclear Power Engineering 中文版) | 核电监管转移 + IEC 60880 / ISO 26262 / DO-178C 概念互补论 | under review |

---

## 8. 关键文档索引

| 文档 | 路径 |
|------|------|
| 主稿 IST trim | `论文初稿P2_IST.md` (9.5k words) |
| 附录 IST | `论文初稿P2_IST_appendix.md` (6.0k words) |
| 中文母稿 | `论文初稿P2.md` |
| 英文母稿 | `论文初稿P2_EN.md` |
| LaTeX submission | `submission/p2_ist_v2.tex` / `.pdf` |
| Cover letter | `submission/cover_letter_v2.md` |
| 文献验证审核 | `docs/review_2026-05-02/reference_verification_audit.md` |
| Stage 4.5 final integrity | `docs/review_2026-05-02/stage_4_5_round2_reverify.md` |
| Replication package | `replication/replication.zip` (2.35 MB, 684 files) |
| Process summary (CN/EN) | `submission/process_summary_{zh,en}.{md,pdf}` |

完整 reproducibility 入口：`replication/REPRODUCIBILITY.md`。

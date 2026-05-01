# P2 Paper Completion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (recommended for inline execution) or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. **All paper text MUST be in Chinese; technical identifiers stay English.**

**Goal:** Finish P2 论文(`论文初稿P2.md`)的实证报告(§5.6-5.9)、讨论(§6)、新增风险条目(§7 R8-R10)、复现性文档与最终自审,把已有 60 单元格 SMS / LRCA / RQ2-4 数据"翻译"为可投稿章节。覆盖 spiral 计划 Rounds 11-14。

**Architecture:** 先写一个数据汇总脚本 `scripts/build_paper_numbers.py`,把所有 JSON 实测数字落到一份 `data/results/paper_numbers.json`(单一事实源),后续所有论文章节直接引用这些数字,避免散落的人工抄写错误。论文章节按 §5.6 → 5.7 → 5.8 → 5.9 → §6 → §7 → §8 → 复现性文档 → 自审顺序追加/重排。

**Tech Stack:** Python 3.12, json, numpy, scipy.stats(已有);手写 Markdown 章节,grep 校验 placeholder。

**Critical caveats reflected in writing:**
- **H2 未达成**(Cliff's δ = 0.321 < 0.474):明确报告为"方向性证据,效应规模未达大效应阈值",列入 §6 讨论与 §7 局限,不掩盖。
- **RQ3 MixedLM 主模型奇异**(Singular matrix;fallback Group Var 边界):章节里如实声明"random intercept term degenerate; reporting fixed-effects estimates as approximate";列入 §7 R6 扩展。
- **median_cross = 0**:多数 cross-MP cell SMS 完全为 0,需在 §5.7 解释,§6.1 解读。

**File map:**
- New: `scripts/build_paper_numbers.py` — 单一数字源生成器
- New: `data/results/paper_numbers.json` — 所有论文章节引用的数字
- Modify: `论文初稿P2.md` — 追加 §5.6-5.9, 重写 §6, 增补 §7, 现有 §6 工作量重编号为 §8
- New: `REPRODUCIBILITY.md` — 复现命令与环境
- New: `DATASET.md` — 数据卡
- New: `LICENSE` — MIT
- New: `requirements-frozen.txt` — 冻结依赖
- Modify: `README.md` — 加入 quick-start 段
- New: `docs/superpowers/notes/2026-05-01-self-review-rq-completion.md` — 自审记录

---

## Task 1: 数据汇总脚本 `build_paper_numbers.py`

**Why first:** 所有论文章节里的数字都来自这一份 JSON,避免重复计算和人工抄写。

**Files:**
- Create: `scripts/build_paper_numbers.py`
- Output: `data/results/paper_numbers.json`

- [ ] **Step 1.1: 写脚本**

Create `scripts/build_paper_numbers.py`:

```python
"""Aggregate all numbers cited in 论文初稿P2.md §5.6-5.9 into a single JSON.

Sources:
  data/results/sms_track2_v2.json   — 60-cell SMS
  data/results/lrca_60cell.json     — LRCA C1/C2/C3/C4 + suspect_share
  data/results/rq2_cliffs_delta.json
  data/results/rq3_mixed_effects.json
  data/results/rq4_pattern_coverage.json

Outputs:
  data/results/paper_numbers.json   — flat, paper-ready
"""
import json
import math
import sys
from pathlib import Path
from statistics import mean, median, stdev

import numpy as np

ROOT = Path(__file__).parent.parent
RESULTS = ROOT / "data/results"
PRIMARY = {"a1": 1, "a2": 1, "a3": 1, "b1": 2, "b2": 2, "b3": 2,
           "c1": 5, "c2": 5, "c3": 5, "d1": 2, "d2": 2, "d3": 2}


def _load(name):
    return json.loads((RESULTS / name).read_text())


def main() -> None:
    sms = _load("sms_track2_v2.json")
    lrca = _load("lrca_60cell.json")
    rq2 = _load("rq2_cliffs_delta.json")
    rq3 = _load("rq3_mixed_effects.json")
    rq4 = _load("rq4_pattern_coverage.json")

    aligned, cross = [], []
    per_class = {"a": [], "b": [], "c": [], "d": []}
    for cell, v in sms.items():
        put_id = cell.split("_")[0].lower()
        mp_k = int(cell.split("MP")[1])
        s = v["sms"]
        if mp_k == PRIMARY[put_id]:
            aligned.append(s)
        else:
            cross.append(s)
        per_class[put_id[0]].append(s)

    all_sms = [v["sms"] for v in sms.values()]
    c1_shares = [r["c1_share"] for r in lrca.values()]
    suspects = [r["suspect_share"] for r in lrca.values()]

    h5_threshold = 0.20  # paper §5.2 H5
    h5_cells_pass = sum(1 for s in suspects if s <= h5_threshold)

    out = {
        "rq1": {
            "n_cells": len(sms),
            "mean_sms": round(float(np.mean(all_sms)), 4),
            "median_sms": round(float(np.median(all_sms)), 4),
            "std_sms": round(float(np.std(all_sms, ddof=1)), 4),
            "n_zero_sms": int(sum(1 for s in all_sms if s == 0.0)),
            "mean_c1_share": round(float(np.mean(c1_shares)), 4),
            "mean_suspect_share": round(float(np.mean(suspects)), 4),
            "h5_threshold_suspect": h5_threshold,
            "h5_cells_pass": h5_cells_pass,
            "h5_pass_ratio": round(h5_cells_pass / len(sms), 4),
        },
        "rq2": {
            "n_aligned": len(aligned),
            "n_cross": len(cross),
            "mean_aligned": round(float(np.mean(aligned)), 4),
            "mean_cross": round(float(np.mean(cross)), 4),
            "median_aligned": round(float(np.median(aligned)), 4),
            "median_cross": round(float(np.median(cross)), 4),
            "cliffs_delta": round(rq2["cliffs_delta"], 4),
            "delta_ci_95_lo": round(rq2["delta_ci_95"][0], 4),
            "delta_ci_95_hi": round(rq2["delta_ci_95"][1], 4),
            "h2_threshold_delta": rq2["h2_threshold_delta"],
            "h2_delta_pass": rq2["h2_delta_pass"],
            "h2_threshold_ratio": rq2["h2_threshold_ratio"],
            "h2_ratio_pass": rq2["h2_ratio_pass"],
            "odds_ratio_inf": math.isinf(rq2["odds_ratio_median"]) if isinstance(rq2["odds_ratio_median"], float) else (rq2["odds_ratio_median"] in ("Infinity", float("inf"))),
        },
        "rq3": {
            "n_observations": rq3["n_observations"],
            "class_mean_a": round(rq3["class_means"]["a"], 4),
            "class_mean_b": round(rq3["class_means"]["b"], 4),
            "class_mean_c": round(rq3["class_means"]["c"], 4),
            "class_mean_d": round(rq3["class_means"]["d"], 4),
            "class_max": max(rq3["class_means"], key=rq3["class_means"].get),
            "class_min": min(rq3["class_means"], key=rq3["class_means"].get),
            "primary_converged": rq3["converged"],
            "fit_error": rq3.get("fit_error", ""),
            "fallback_model": rq3.get("fallback_model", ""),
            "fallback_note": rq3.get("fallback_note", ""),
            "fallback_p_class_b": round(rq3.get("fallback_p_values", {}).get("C(class)[T.b]", float("nan")), 4),
            "fallback_p_class_c": round(rq3.get("fallback_p_values", {}).get("C(class)[T.c]", float("nan")), 4),
            "fallback_p_class_d": round(rq3.get("fallback_p_values", {}).get("C(class)[T.d]", float("nan")), 4),
            "sign_test_aligned_above_cross": int(sum(
                1 for c in "abcd"
                if np.mean([s for cell, v in sms.items() if cell[0].lower() == c
                            and int(cell.split("MP")[1]) == PRIMARY[cell.split("_")[0].lower()]
                            for s in [v["sms"]]])
                > np.mean([s for cell, v in sms.items() if cell[0].lower() == c
                           and int(cell.split("MP")[1]) != PRIMARY[cell.split("_")[0].lower()]
                           for s in [v["sms"]]])
            )),
        },
        "rq4": {
            "spearman_rho": round(rq4["spearman_rho"], 4),
            "spearman_p": round(rq4["spearman_p"], 4),
            "kendall_tau": round(rq4["kendall_tau"], 4),
            "kendall_p": round(rq4["kendall_p"], 4),
            "n_puts": rq4["n"],
            "min_pc": round(min(v["pattern_coverage"] for v in rq4["per_put"].values()), 4),
            "max_pc": round(max(v["pattern_coverage"] for v in rq4["per_put"].values()), 4),
            "mean_pc": round(float(np.mean([v["pattern_coverage"] for v in rq4["per_put"].values()])), 4),
        },
    }

    out_path = RESULTS / "paper_numbers.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"saved -> {out_path}")
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

- [ ] **Step 1.2: 运行脚本**

Run: `cd "/Users/limeng/Library/CloudStorage/OneDrive-个人/0-论文/MR识别/MT完备性" && PYTHONPATH=src python scripts/build_paper_numbers.py`

- [ ] **Step 1.3: 验收**

**验收标准(可量化):**
- [ ] `data/results/paper_numbers.json` 存在且 size > 1KB
- [ ] JSON 顶层 key 恰为 `rq1`、`rq2`、`rq3`、`rq4`(4 个)
- [ ] `rq1.n_cells == 60`,`rq2.n_aligned + rq2.n_cross == 60`
- [ ] `rq3.class_mean_a/b/c/d` 4 个数字均在 [0, 1] 区间内
- [ ] 脚本退出码 0,无 traceback

Run 验证:
```bash
python -c "import json; d = json.load(open('data/results/paper_numbers.json')); assert set(d.keys()) == {'rq1','rq2','rq3','rq4'}; assert d['rq1']['n_cells'] == 60; assert d['rq2']['n_aligned'] + d['rq2']['n_cross'] == 60; print('OK')"
```
Expected: `OK`

- [ ] **Step 1.4: 提交**

```bash
git add scripts/build_paper_numbers.py data/results/paper_numbers.json
git commit -m "$(cat <<'EOF'
feat(paper): single-source aggregator for §5.6-5.9 numbers

build_paper_numbers.py reads sms_track2_v2 + lrca_60cell + rq2/3/4 JSONs
and emits paper_numbers.json. All §5.6-5.9 sections cite this single file,
removing the risk of paper-vs-data drift.
EOF
)"
```

---

## Task 2: §5.6 RQ1 实证结果章节

**Why second:** §5.6 是论文实证部分的入口,引用 figure 1 + figure 4(C1_share),给出 60 单元格描述统计与 H1/H5 判定。

**Files:**
- Modify: `论文初稿P2.md`(§5.5 之后插入 §5.6)

- [ ] **Step 2.1: 读 paper_numbers.json,记下 RQ1 的 6 个关键数字**

Read `data/results/paper_numbers.json`,记下以下变量供下一步替换:
- `N_CELLS` = `rq1.n_cells`
- `MEAN_SMS` = `rq1.mean_sms`
- `MEDIAN_SMS` = `rq1.median_sms`
- `STD_SMS` = `rq1.std_sms`
- `N_ZERO` = `rq1.n_zero_sms`
- `MEAN_C1` = `rq1.mean_c1_share`
- `MEAN_SUSPECT` = `rq1.mean_suspect_share`
- `H5_PASS` = `rq1.h5_cells_pass`
- `H5_RATIO` = `rq1.h5_pass_ratio`

- [ ] **Step 2.2: 在 `论文初稿P2.md` 的 `### 5.5 可视化` 章节末尾之后追加 §5.6**

定位锚点(grep 找出"### 5.5 可视化"之后、"## 第 6 节 · 工作量与时序"之前的位置)。
插入(把上一步的变量替换成实际数字):

```markdown
### 5.6 RQ1 实证结果(60 单元格,Track-2 v2)

#### 5.6.1 数据规模与单元格级 SMS 分布

每 PUT 12 个 mutants(operator-cache 比例采样,Round 2 builder),每个 (mutant, MR) pair 在 N=20 AVP 重复采样下计算 R_kill。60 单元格 SMS 全表见图 1。

主要统计:
| 指标 | 数值 |
|---|---|
| 单元格数 | <N_CELLS> |
| 平均 SMS | <MEAN_SMS> |
| 中位数 SMS | <MEDIAN_SMS> |
| 标准差 SMS | <STD_SMS> |
| SMS = 0 的单元格数 | <N_ZERO> / <N_CELLS> |

> 注:大量 SMS = 0 单元格集中在 cross-MP 切片(j ≠ k),即 PUT 主对齐 MP 之外的 4 个 MP。这是 RQ2 H1(MR-MP 对齐性)在数据层的直接体现,§5.7 进一步用 Cliff's δ 量化。

[图 1:60 单元格 SMS 热力图(rows = PUT, cols = MP,★ 标记 j = k 对齐单元格)]

#### 5.6.2 LRCA C1_share / suspect_share 分布

LRCA 三层诊断对每个被 killed 的 mutant 标注 C1/C2/C3/C4 之一(§4.6)。60 单元格平均统计:
| 指标 | 数值 |
|---|---|
| 平均 C1_share(legit fault 占比) | <MEAN_C1> |
| 平均 suspect_share(C2+C3+C4 之和占比) | <MEAN_SUSPECT> |
| 满足 H5 阈值(suspect_share ≤ 0.20)的单元格 | <H5_PASS> / <N_CELLS>(<H5_RATIO>) |

H5 判定:**<H5_PASS / N_CELLS 是否 ≥ 80%? 据数据填"达成"或"未达成">**。SMS 与 C1_share 的相关图见图 4。

[图 4:SMS vs C1_share 散点(per cell)]
```

(把所有 `<...>` 占位符替换成 Step 2.1 记下的实际数字。)

- [ ] **Step 2.3: 验收**

**验收标准(可量化):**
- [ ] `论文初稿P2.md` 中 `### 5.6 RQ1 实证结果` 章节存在
- [ ] 该章节包含子节 `#### 5.6.1 数据规模与单元格级 SMS 分布` 和 `#### 5.6.2 LRCA C1_share / suspect_share 分布`
- [ ] 章节内出现"图 1"和"图 4"两个图引用
- [ ] 章节内 grep 不到字符串 `<MEAN_SMS>`、`<MEAN_C1>` 等任何 `< >` 包裹的占位符
- [ ] 章节字数 ≥ 300 中文字符

Run 验证:
```bash
grep -A 100 "^### 5.6" 论文初稿P2.md | head -80 | tee /tmp/sec56.txt
grep -c "图 1" /tmp/sec56.txt   # 应 ≥ 1
grep -c "图 4" /tmp/sec56.txt   # 应 ≥ 1
grep -E "<[A-Z_]+>" /tmp/sec56.txt && echo "PLACEHOLDER LEFT" || echo "OK no placeholders"
```
Expected: 最后一行输出 `OK no placeholders`

- [ ] **Step 2.4: 提交**

```bash
git add 论文初稿P2.md
git commit -m "draft(paper): §5.6 RQ1 empirical results from Track-2 v2 + LRCA"
```

---

## Task 3: §5.7 RQ2 实证结果章节

**Why third:** §5.7 报告 aligned vs cross 比较与 H2 判定。**关键诚实呈现:H2 未达成,但效应方向正确**。

**Files:**
- Modify: `论文初稿P2.md`(§5.6 之后)

- [ ] **Step 3.1: 读 paper_numbers.json 的 rq2 段**

记下:
- `N_AL` = `rq2.n_aligned`
- `N_CR` = `rq2.n_cross`
- `MEAN_AL` = `rq2.mean_aligned`
- `MEAN_CR` = `rq2.mean_cross`
- `MED_AL` = `rq2.median_aligned`
- `MED_CR` = `rq2.median_cross`
- `DELTA` = `rq2.cliffs_delta`
- `CI_LO` = `rq2.delta_ci_95_lo`
- `CI_HI` = `rq2.delta_ci_95_hi`
- `H2_DELTA_PASS` = `rq2.h2_delta_pass`
- `H2_RATIO_PASS` = `rq2.h2_ratio_pass`
- `ODDS_INF` = `rq2.odds_ratio_inf`(布尔)

- [ ] **Step 3.2: 在 §5.6 之后追加 §5.7**

```markdown
### 5.7 RQ2 实证结果(对齐 vs 非对齐)

#### 5.7.1 描述统计

将 60 单元格按 j == primary_MP(put) 划分:
| 切片 | n | 平均 SMS | 中位数 SMS |
|---|---|---|---|
| aligned(j == k) | <N_AL> | <MEAN_AL> | <MED_AL> |
| cross(j ≠ k) | <N_CR> | <MEAN_CR> | <MED_CR> |

aligned-SMS 在均值与中位数上都高于 cross-SMS,方向与 H1 一致。注意:cross 切片的中位数为 <MED_CR>,意味着超过半数 cross-MP 单元格的 SMS 完全为 0——cross 设计下 MR 对变异体几乎完全失效,这一观察构成 §6.1 讨论的核心经验事实。

[图 2:aligned vs cross SMS 箱线图]

#### 5.7.2 效应规模与假设检验

非参效应规模 Cliff's δ:
- δ = <DELTA>
- 95% bootstrap percentile CI = [<CI_LO>, <CI_HI>](n_boot = 1000,seed = 42)

中位数几率比(median(aligned) / median(cross)):因 median(cross) = 0,几率比形式上为 ∞;此时退化为"aligned 中位数 > 0 而 cross 中位数 = 0"的定性事实。

H2 判定(两条件合取:Cliff's δ ≥ 0.474 且 median odds ratio ≥ 3.0):
- δ 阈值条件:**<根据 H2_DELTA_PASS 填"达成"或"未达成">**(实测 δ = <DELTA>,阈值 0.474)
- 几率比条件:由于 median(cross) = 0 无定义,改报"aligned 中位数显著高于 cross 中位数"作为辅助证据
- 综合 H2 结论:**未达成大效应阈值;效应方向与 CI 下限均为正,提供方向性证据但效应规模属中等(small-to-medium)**

> 解读:RQ2 的形式化 H2 边界没有越过,但 95% CI 下限 <CI_LO> > 0 表明效应方向稳定。这构成 §6.1 中"aligned 切片确实更敏感,但效应规模在 LLM-生成 mutant + N=12 池规模下仍保留中等量级,不到大效应阈值"的诚实陈述。我们将此作为方向性证据保留,并在 §7 R9(mutant pool 规模)与 §7 R10(LLM 非确定性)讨论可能的稀释源。
```

(替换所有 `< >` 占位符。"达成"/"未达成"按 `H2_DELTA_PASS` 取值确定。)

- [ ] **Step 3.3: 验收**

**验收标准:**
- [ ] §5.7 章节存在,包含 5.7.1 与 5.7.2 两个子节
- [ ] 引用"图 2"
- [ ] 章节中明确出现 "Cliff's δ" 与 "95% bootstrap" 字串
- [ ] 章节中明确出现"未达成大效应阈值"或等价的诚实陈述
- [ ] 章节内 grep 不到 `<.*>` 占位符
- [ ] 章节字数 ≥ 350 中文字符

Run 验证:
```bash
grep -A 100 "^### 5.7" 论文初稿P2.md | head -60 > /tmp/sec57.txt
grep -c "Cliff" /tmp/sec57.txt          # ≥ 1
grep -c "bootstrap" /tmp/sec57.txt      # ≥ 1
grep -c "未达成" /tmp/sec57.txt          # ≥ 1
grep -E "<[A-Z_]+>" /tmp/sec57.txt && echo "FAIL" || echo "OK"
```
Expected: 末行 `OK`,前三个 grep 计数 ≥ 1

- [ ] **Step 3.4: 提交**

```bash
git add 论文初稿P2.md
git commit -m "draft(paper): §5.7 RQ2 empirical results with honest H2 reporting"
```

---

## Task 4: §5.8 RQ3 实证结果章节

**Why fourth:** §5.8 报告跨类比较与 mixed-effects。**关键诚实呈现:主模型 Singular,fallback 退化随机效应,只能解读为 fixed-effects 近似**。

**Files:**
- Modify: `论文初稿P2.md`

- [ ] **Step 4.1: 读 paper_numbers.json 的 rq3 段**

记下:
- `MEAN_A/B/C/D` = `rq3.class_mean_{a,b,c,d}`
- `CLS_MAX/MIN` = `rq3.class_max/min`
- `PRIM_CONV` = `rq3.primary_converged`
- `FIT_ERR` = `rq3.fit_error`
- `FB_NOTE` = `rq3.fallback_note`
- `P_B/C/D` = `rq3.fallback_p_class_{b,c,d}`
- `SIGN_PASS` = `rq3.sign_test_aligned_above_cross`(0-4)

- [ ] **Step 4.2: 追加 §5.8**

```markdown
### 5.8 RQ3 实证结果(4 类 PUT 跨类一致性)

#### 5.8.1 类别均值

| Class | PUT 集合 | 平均 SMS(类内 15 单元格) |
|---|---|---|
| a (numeric) | a1, a2, a3 | <MEAN_A> |
| b (probabilistic) | b1, b2, b3 | <MEAN_B> |
| c (surrogate) | c1, c2, c3 | <MEAN_C> |
| d (ML) | d1, d2, d3 | <MEAN_D> |

类间最大值出现在 class <CLS_MAX>(<相应均值>),最小值在 class <CLS_MIN>(<相应均值>)。

[图 3:跨类 SMS forest plot(均值 ± SEM)]

#### 5.8.2 Sign test:类内 aligned 是否高于 cross

对每一类,计算"该类 aligned 切片均值 - 该类 cross 切片均值",符号为正记 1。
- 通过数:<SIGN_PASS> / 4

H4(4/4 类 aligned 均值 > cross 均值):**<根据 SIGN_PASS == 4 填"达成"或"部分达成">**。

#### 5.8.3 Mixed-effects model 的局限性声明

§5.3.2 计划的随机截距-PUT、固定效应 class × operator 模型在实测数据上**主模型未收敛**:
- 主模型公式:`sms ~ C(class) + C(operator) + C(class):C(operator) + (1 | put)`
- Fit 错误:Singular matrix(类 × 算子交互项的设计矩阵列秩不足,N=60 观测对 11 维 fixed-effects 不够)
- Fallback 模型(去掉交互项):`sms ~ C(class) + C(operator) + (1 | put)`
- Fallback 状态:fixed-effects 收敛,但 Group Var(PUT 随机截距方差)落到边界 ≈ 0,实质上退化为 OLS;p 值"can be estimated but the random-intercept term is degenerate"(模型自我报告)

类别 fixed-effects p 值(以 class a 为基准,fallback 模型):
| 对比 | p 值(approx.) |
|---|---|
| class b vs a | <P_B> |
| class c vs a | <P_C> |
| class d vs a | <P_D> |

> **诚实声明**:由于 PUT 随机截距方差退化与样本规模(60 单元格 / 12 PUT)限制,我们不把 fallback 的 p 值作为正式假设检验报告,而是作为辅助描述。RQ3 的主结论改以(a) 类别均值表 + (b) sign test + (c) forest plot 三件式直接展示,符合 §5.3.2 已声明的"小 N 多重比较替代方案"。我们将此扩展为 §7.1 新增 R6 局限。
```

- [ ] **Step 4.3: 验收**

**验收标准:**
- [ ] §5.8 章节存在,包含 5.8.1 / 5.8.2 / 5.8.3 三个子节
- [ ] 引用"图 3"
- [ ] 章节中明确出现 "Singular matrix" 或"未收敛"或"degenerate"字样(诚实声明数据问题)
- [ ] 章节内 grep 不到 `<.*>` 占位符
- [ ] Sign test 通过数与 paper_numbers.json 一致

Run 验证:
```bash
grep -A 80 "^### 5.8" 论文初稿P2.md | head -60 > /tmp/sec58.txt
grep -E "Singular|未收敛|degenerate" /tmp/sec58.txt | head -3
grep -E "<[A-Z_]+>" /tmp/sec58.txt && echo "FAIL" || echo "OK"
```
Expected: 末行 `OK`;前一 grep 至少匹配一项

- [ ] **Step 4.4: 提交**

```bash
git add 论文初稿P2.md
git commit -m "draft(paper): §5.8 RQ3 cross-class results with MixedLM caveats"
```

---

## Task 5: §5.9 RQ4 实证结果章节

**Why fifth:** §5.9 报告 SMS vs Pattern Coverage 相关性。

**Files:**
- Modify: `论文初稿P2.md`

- [ ] **Step 5.1: 读 paper_numbers.json 的 rq4 段**

记下 `RHO`/`P_RHO`/`TAU`/`P_TAU`/`MIN_PC`/`MAX_PC`/`MEAN_PC`。

- [ ] **Step 5.2: 追加 §5.9**

```markdown
### 5.9 RQ4 实证结果(SMS vs Pattern Coverage)

#### 5.9.1 Pattern coverage 操作化

每个 PUT 计算 (MP_k, R_outcome ∈ {True, False}) 二元组覆盖率:每 PUT 5 个 MP × 2 outcome = 10 个 cells,coverage = 实际触发的 cells 数 / 10。本质上是 §1.4 中 RQ4 baseline 操作化的最简实现。

12 个 PUT 的 PC 范围:[<MIN_PC>, <MAX_PC>],均值 <MEAN_PC>。

#### 5.9.2 与 SMS 的相关性

按 PUT 配对(每 PUT 一个 PC 值,对应该 PUT 在 5 MPs 上的均值 SMS):
- Spearman ρ = <RHO>(p = <P_RHO>)
- Kendall τ = <TAU>(p = <P_TAU>)

[图 5:per-PUT SMS vs PC 散点(n = 12)]

#### 5.9.3 解读

n = 12 PUT 给出的统计功效有限,p 值仅供参考。**定性观察**:Spearman ρ <根据数值正负填"为正,但接近零"或"为负"或"接近零">,意味着 PC 与 SMS **<填"提供方向一致的弱信号"或"提供互补信息"或"几乎独立"——根据 |ρ| 与 sign 综合判断>**。RQ4 的完成度限于此层级:进一步细化 PC 定义(纳入 mutant 维度)留待 P4 论文(见 §1.6)。
```

- [ ] **Step 5.3: 验收**

**验收标准:**
- [ ] §5.9 章节存在,包含 5.9.1 / 5.9.2 / 5.9.3 三个子节
- [ ] 引用"图 5"
- [ ] Spearman 和 Kendall 数字均填入
- [ ] 章节明确声明"n = 12 PUT 给出的统计功效有限"
- [ ] 无 `<.*>` 占位符

- [ ] **Step 5.4: 提交**

```bash
git add 论文初稿P2.md
git commit -m "draft(paper): §5.9 RQ4 SMS vs PC correlation"
```

---

## Task 6: §6 重写为讨论(原 §6 工作量改为 §8)

**Why sixth:** 原 §6 是"工作量与时序",计划要求 §6 改为"讨论"。把原 §6 / §7 重编号为 §8 / §9,§7 保留为风险与局限(扩充 R8-R10)。

**Files:**
- Modify: `论文初稿P2.md`

- [ ] **Step 6.1: 重编号(谨慎,顺序很重要)**

定位 `论文初稿P2.md` 中的两个章节标题:
1. `## 第 6 节 · 工作量与时序` — 改为 `## 第 8 节 · 工作量与时序`
2. `## 第 7 节 · 风险与缓解 + Limitations` — 改为 `## 第 7 节 · 风险与缓解 + Limitations`(保持不变,Task 7 在此章节内插入新子节)

但要先**插入**新的 `## 第 6 节 · 讨论`,**然后**修改原 §6→§8。**操作顺序保证锚点唯一**:

1. 先在 `### 5.9 RQ4 实证结果` 之后、`## 第 6 节 · 工作量与时序` 之前插入新的 `## 第 6 节 · 讨论` 完整内容(见 Step 6.2)
2. 然后用 Edit 工具把 `## 第 6 节 · 工作量与时序` 改为 `## 第 8 节 · 工作量与时序`(此时已唯一,因为新 §6 的标题是"讨论"而非"工作量与时序")

- [ ] **Step 6.2: 插入新 §6 讨论**

在 §5.9 章节末追加 / `## 第 6 节 · 工作量与时序` 之前插入:

```markdown
## 第 6 节 · 讨论

### 6.1 SMS 在 aligned 切片上的系统性偏置

RQ2 给出的核心经验事实:cross-MP 切片(j ≠ k)的中位数 SMS = 0,即多数非对齐 MR 对 LLM-生成的语义变异体几乎完全失效;aligned 切片中位数 SMS 远高于 0。这一不对称性来源于 mut_j 与 MP_k 的语义相干性——aligned 切片中,变异体打破的是 MR 直接断言的代数性质,因而 R 检测信号最强;cross 切片中,变异体打破的语义维度与 MR 检测的语义维度正交,即使变异确实改变了输出,MR 也无法将该改变捕获为 R-fail。

H2 形式上未达成大效应阈值(Cliff's δ = paper_numbers.rq2.cliffs_delta < 0.474),但 95% CI 下限 > 0、aligned 中位数 > 0 = cross 中位数,提供方向性证据。我们的解读:在 LLM 生成的 mutant 池(每 PUT 12 个,同源 LLM)与 N=20 AVP 重复采样下,效应规模被池规模与 LLM 同源偏置稀释。这构成 §7 R9 与 R10 的实证根据。

### 6.2 R_sem 与 R_kill 的解耦

§4.8.3 算子级 pilot 已观察到:HP 类(超参数)算子的 R_sem(语义可行性)高,但 R_kill(被 MR 杀死率)低。本章 §5.6.2 单元格级 SMS 重现该模式——大量 SMS = 0 单元格集中在 cross-MP 切片,且这些单元格里的 mutant 在 LRCA 中并非全部 artifact(C1_share 平均仍 > 0)。

工程启示:MR 设计中"算子-MP 对齐覆盖"是产生强 SMS 信号的必要条件;仅做"语义可行 mutant 池"扩张并不增加 SMS,反而稀释比例。这为 P4 论文中"以 SMS 反推 MR 不足覆盖维度"的研究问题铺设经验依据。

### 6.3 跨类一致性 H4 的约束解读

RQ3 数据显示 4 个 class 的均值 SMS 都为正但相差有限。H4(4/4 类 aligned > cross)在 sign test 下达成 / 部分达成(见 §5.8.2 paper_numbers.rq3.sign_test_aligned_above_cross),但 mixed-effects 主模型 Singular 表明 60 单元格 / 12 PUT 的样本规模无法支撑随机截距估计——random effect var 收敛到 0 边界。

不把这视为 RQ3 的失败:跨类一致性的"一致"已在 4/4 类的均值方向上呈现;只是无法用 mixed-effects 给出严谨的 p 值。这一限制纳入 §7 R6 扩展。

### 6.4 SMS vs Pattern Coverage 的位置关系

RQ4 的 Spearman ρ(n = 12 PUT)给出 SMS 与最简 PC 的相关性方向。无论数值具体落在何处,n = 12 都不允许把 SMS 与 PC "等价"或"互补"做形式化结论;此处只做定性观察。我们的核心立场:**SMS 不替代覆盖类指标,而提供"语义层敏感性"维度**——一个 PUT 可以 PC 高但 SMS 低(MR 触发到所有 outcome 但不杀变异),也可以反之(MR 杀变异但只走单一 outcome)。两者正交而非冗余,这一立场需在 P4 论文里以扩展 PC 定义形式量化。
```

- [ ] **Step 6.3: 重编号原 §6 / §7**

```bash
# 先确认锚点唯一性(此时 §6 标题应同时存在新旧两个,但新 §6 是"讨论"、旧 §6 是"工作量与时序",可用 Edit 工具替换字串"## 第 6 节 · 工作量与时序" -> "## 第 8 节 · 工作量与时序")
grep -n "^## 第 [678] 节" 论文初稿P2.md
```
Expected: 4 行命中:
- §6 讨论(new)
- §6 工作量与时序(old, 待改)
- §7 风险与缓解(保持)
- 不应该有第 4 行

用 Edit 工具:
- old_string: `## 第 6 节 · 工作量与时序`
- new_string: `## 第 8 节 · 工作量与时序`

(`## 第 7 节 · 风险与缓解 + Limitations` 保持不变,但其内子节目录改为引用 R8-R10,见 Task 7。)

注意 §8 中可能也有 "### 6.1" / "### 6.2" / "### 6.3" 子节标题——把它们改为 "### 8.1" / "### 8.2" / "### 8.3":

```bash
grep -nE "^### 6\.[0-9]" 论文初稿P2.md
```
Expected: 现在应同时命中(a) 新 §6 讨论的子节(6.1-6.4)和(b) 旧 §6 工作量的子节(原 6.1-6.3)。

用 Edit 工具,**只改原 §6 工作量子节的部分**(它们之前一定不是"讨论"内容)。一种简单办法:在 §8 章节标题之后那段范围内手工查找 6.1/6.2/6.3 标题并改 8.1/8.2/8.3。

- [ ] **Step 6.4: 验收**

**验收标准:**
- [ ] `grep -c "^## 第 6 节 · 讨论" 论文初稿P2.md` 输出 1
- [ ] `grep -c "^## 第 8 节 · 工作量与时序" 论文初稿P2.md` 输出 1
- [ ] `grep -c "^## 第 6 节 · 工作量与时序" 论文初稿P2.md` 输出 0(原标题已无)
- [ ] §6 讨论包含 6.1 / 6.2 / 6.3 / 6.4 四个子节
- [ ] §8 工作量子节标题为 8.1 / 8.2 / 8.3(不再为 6.x)

Run 验证:
```bash
grep -c "^## 第 6 节 · 讨论" 论文初稿P2.md          # 应 = 1
grep -c "^## 第 8 节 · 工作量与时序" 论文初稿P2.md   # 应 = 1
grep -c "^## 第 6 节 · 工作量与时序" 论文初稿P2.md   # 应 = 0
grep -E "^### 6\.[1-4] " 论文初稿P2.md             # 应有 4 行(讨论的子节)
grep -E "^### 8\.[1-3] " 论文初稿P2.md             # 应有 3 行(工作量的子节)
```

- [ ] **Step 6.5: 提交**

```bash
git add 论文初稿P2.md
git commit -m "draft(paper): §6 discussion + renumber workload to §8"
```

---

## Task 7: §7 增补 R8 / R9 / R10 风险条目 + R6 扩展

**Why seventh:** §7.1 现有 R1-R4,§7.2 R5-R6,§7.3 R7。新增:
- R8 算子注册表-PUT 源码漂移(§7.1)
- R9 mutant pool 规模(§7.1)
- R10 LLM 非确定性(§7.1)
- 在 R6(跨类统计功效)末尾扩展 mixed-effects 退化说明

**Files:**
- Modify: `论文初稿P2.md`

- [ ] **Step 7.1: 在 §7.1 内部最末子节之后追加 R8-R10**

定位锚点:`#### 7.1.4 LRCA 多标签判定的边界(R4)` 子节之后、`### 7.2 外部威胁` 之前。
插入:

```markdown
#### 7.1.5 算子注册表-PUT 源代码漂移(R8)

v2 → v2.1 修订过程中发现 6/37 算子定义引用了 PUT 重构后已不存在的参数(例如 GPR.alpha vs WhiteKernel.noise_level;d1 注册声明 SVM 但 PUT 实为 MLP)。此类漂移会导致变异体生成与 PUT 无可执行匹配,污染 R_sem 统计。**缓解**:已在 §4.2 加入前置一致性扫描(target_locator 中的关键标识符必须出现在 PUT 源码中,否则该算子在该 PUT 上跳过)。

#### 7.1.6 Mutant pool 规模(R9)

每 PUT 12 个 mutant 是工程-成本平衡:更小则 SMS 估计跳变粗糙(每个 mutant 贡献 1/12 ≈ 0.083 的步进),更大则 LLM 调用成本超出每周 Opus 订阅额度。bootstrap CI(§5.7)反映了这一来源的不确定性。**留待**:P4 论文以 prerelease budget 扩大到 30 mutants/PUT,届时重新评估 RQ2 H2 是否能跨过 0.474 阈值。

#### 7.1.7 LLM 生成的非确定性(R10)

Claude Opus 订阅接口无 seed 控制;同一 prompt 在不同时刻可能产生不同 mutant 输出。**缓解**三件套:(a) Multi-turn de-dup 强制候选间结构差异(`§4.2.1`);(b) K=10 / K=20 重复降低单算子的单点偏差(§4.8);(c) `data/operator_campaign/raw/` 提交完整 prompt + raw response,使复现实验可直接重用本文使用的同一 mutant 集合,绕过非确定性。
```

- [ ] **Step 7.2: 扩展 R6**

定位 `#### 7.2.2 跨类一致性的统计功效(R6)` 子节内容,在末尾追加段落:

```markdown
**§5.8 实测追加**:planned mixed-effects model(`sms ~ C(class) * C(operator) + (1 | put)`)在 N=60 观测下出现 Singular matrix(主模型),fallback 模型 PUT 随机截距方差退化到 0,实质退化为 OLS。我们因此把 RQ3 的主结论改以"类别均值 + sign test + forest plot"三件式直接展示,而非以 mixed-effects p 值作为正式假设检验。这与 §5.3.2 中已声明的"小 N 替代方案"相一致,但应在结论中如实声明 mixed-effects 不可用。
```

- [ ] **Step 7.3: 验收**

**验收标准:**
- [ ] §7.1.5 (R8) / §7.1.6 (R9) / §7.1.7 (R10) 三个子节均存在
- [ ] §7.2.2 (R6) 末尾包含字串 "Singular" 或 "退化"
- [ ] §7 章节中 grep "R8" "R9" "R10" 各匹配 ≥ 1
- [ ] 整个论文 `grep -nE "TODO|TBD|FIXME|<[A-Z_]+>"` 不命中(全文无遗留占位符)

Run 验证:
```bash
grep -c "^#### 7.1.5" 论文初稿P2.md   # 应 = 1
grep -c "^#### 7.1.6" 论文初稿P2.md   # 应 = 1
grep -c "^#### 7.1.7" 论文初稿P2.md   # 应 = 1
grep -E "TODO|TBD|FIXME|<[A-Z_]+>" 论文初稿P2.md && echo "FAIL has placeholder" || echo "OK no placeholders"
```
Expected: 末行 `OK no placeholders`

- [ ] **Step 7.4: 提交**

```bash
git add 论文初稿P2.md
git commit -m "draft(paper): §7 R8/R9/R10 + R6 mixed-effects degeneracy note"
```

---

## Task 8: REPRODUCIBILITY.md

**Files:**
- Create: `REPRODUCIBILITY.md`
- Create: `requirements-frozen.txt`

- [ ] **Step 8.1: 生成冻结依赖**

```bash
cd "/Users/limeng/Library/CloudStorage/OneDrive-个人/0-论文/MR识别/MT完备性"
.venv/bin/pip freeze 2>/dev/null | grep -iE "^(numpy|scipy|scikit-learn|statsmodels|matplotlib|seaborn|fastdtw|openai|anthropic|pytest|python-dotenv|pandas)=" > requirements-frozen.txt
wc -l requirements-frozen.txt
```
Expected: ≥ 8 行(若 .venv 不存在,改用 `/opt/anaconda3/bin/pip freeze`)。

- [ ] **Step 8.2: 写 REPRODUCIBILITY.md**

```markdown
# Reproducibility Guide for P2 Empirical Audit

## Environment

- Python 3.12.x(`.venv` 创建于本仓库根)
- 见 `requirements-frozen.txt` 的冻结依赖
- LLM API 凭证:`.env` 文件(已 gitignore;见 `docs/superpowers/plans/2026-04-29-p2-experimental-infrastructure.md` 的 § "API 配置")

## End-to-end reproduction(全程约 2-3 小时)

```bash
# 1. 创建 venv 并安装依赖
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-frozen.txt

# 2. 运行单元测试(应全部通过)
PYTHONPATH=src .venv/bin/pytest -q

# 3. 重建 per-PUT mutant 池(从 operator-campaign cache,需 cache 已就位)
PYTHONPATH=src .venv/bin/python scripts/build_pools.py

# 4. 重跑 Track-2 SMS(60 单元格 × N=20 重复;约 15-25 分钟)
PYTHONPATH=src .venv/bin/python scripts/sms_campaign.py --track 2 --workers 6 --repeats 20 \
    2>&1 | tee data/results/sms_track2_v2_console.log

# 5. 跑 LRCA(60 单元格 × ~12 mutants;约 10 分钟)
PYTHONPATH=src .venv/bin/python scripts/run_lrca.py

# 6. 算 RQ 统计
PYTHONPATH=src .venv/bin/python scripts/compute_rq2.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq3.py
PYTHONPATH=src .venv/bin/python scripts/compute_rq4.py

# 7. 汇总论文数字
PYTHONPATH=src .venv/bin/python scripts/build_paper_numbers.py

# 8. 渲染图
PYTHONPATH=src .venv/bin/python scripts/render_figures.py

# 9. 检查输出
ls -la data/results/ figures/
```

## What can't be reproduced exactly

- LLM-生成 mutant(`data/operator_campaign/raw/`)非确定性。Cache 已提交并视作冻结数据集,后续 metric 计算无需重新调用 LLM。
- 随机 PUT(b2 MCMC, b3 MC, c-class GPR, d1 MLP)的 SMS 估计在不同 RNG 种子间波动 ≈ 0.05 单位;N=20 重复降低但不消除。

## Provenance per artifact

见 `DATASET.md`。
```

保存为 `REPRODUCIBILITY.md`(repo 根)。

- [ ] **Step 8.3: 验收**

**验收标准:**
- [ ] `REPRODUCIBILITY.md` 存在,行数 ≥ 30
- [ ] 文件中包含命令 `PYTHONPATH=src .venv/bin/python scripts/sms_campaign.py`
- [ ] 文件中包含 `build_paper_numbers.py` 调用
- [ ] `requirements-frozen.txt` 存在,行数 ≥ 8

Run:
```bash
test -f REPRODUCIBILITY.md && wc -l REPRODUCIBILITY.md
grep -c "scripts/sms_campaign" REPRODUCIBILITY.md
grep -c "build_paper_numbers" REPRODUCIBILITY.md
test -f requirements-frozen.txt && wc -l requirements-frozen.txt
```

- [ ] **Step 8.4: 提交**

```bash
git add REPRODUCIBILITY.md requirements-frozen.txt
git commit -m "docs: REPRODUCIBILITY guide + frozen requirements"
```

---

## Task 9: DATASET.md

**Files:**
- Create: `DATASET.md`

- [ ] **Step 9.1: 写 DATASET.md**

```markdown
# P2 Dataset Card

## PUTs(`src/p2/puts/{a1..d3}.py`)
12 个科学计算程序,4 类(numeric / probabilistic / surrogate / ML),每个程序签名 float→float,deterministic-where-possible(stochastic PUT 接受 random_state)。

## MRs(`src/p2/mrs/{a1..d3}.py`)
60 个 metamorphic relations,每 PUT 5 个 MP。强度标签 ●●/●/○ 在每个模块的 docstring 顶部声明,与 §3.3 矩阵一致。

## Mutation operators(`src/p2/mutators/operator_registry.py`)
37 个命名算子,5 类:CE(constant edit)/ OS(operator substitution)/ HP(hyperparameter)/ TF(transform)/ SI/CF(structural / control flow)。每条记录包含 target_locator + transformation + rationale + is_key 标记。is_key=True 的 12 个算子在 K=20 重复下生成。

## LLM-generated mutants
- `data/operator_campaign/raw/{op_id}.json` — 470 trials,含 prompt、raw LLM 响应、V1-V6 + operator_match 标签、reviewer 推理文本。
- `data/operator_campaign/cache/{op_id}_attempt{NN}.py` — 212 个确认 mutant(V1-V6 ✓ ∧ operator_match=Yes)。
- `data/mutants/{put}_pool/m{NN}_{op_id}_a{NN}.py` — per-PUT 池,12 mutants/PUT,operator-比例采样(`scripts/build_pools.py` 输出)。
- `data/mutants/{put}_MP{k}_llm/` — Phase 1 LLM campaign 留存的 45 个变异体(已被 v2 池取代,但保留供历史溯源)。

## Generation prompts
- `src/p2/mutators/prompts/operator_template.txt` — generator prompt(Claude Opus 4.6)
- `src/p2/mutators/prompts/operator_reviewer_template.txt` — reviewer prompt(GPT-5.4 via bltcy.ai)
- `src/p2/mutators/prompts/generator_template.txt` / `reviewer_template.txt` — Phase 1 (cell 级)模板,保留供对比

## Metrics outputs
- `data/results/operator_metrics.json` — R_sem / D_impl / R_kill per operator
- `data/results/sms_track1.json` — Track-1(12 主对齐单元格,Phase 1)
- `data/results/sms_track2.json` — Track-2 v1(60 cells, 4-5 mutants/cell)
- `data/results/sms_track2_v2.json` — Track-2 v2(60 cells, 12 mutants/cell, N=20)— **本文主分析用**
- `data/results/lrca_60cell.json` — per-cell C1/C2/C3/C4/Artifact 计数 + suspect_share
- `data/results/rq2_cliffs_delta.json` — Cliff's δ + 95% bootstrap CI
- `data/results/rq3_mixed_effects.json` — mixed-effects 主模型(Singular)+ fallback 模型
- `data/results/rq4_pattern_coverage.json` — per-PUT PC + Spearman / Kendall
- `data/results/paper_numbers.json` — §5.6-5.9 引用的所有数字(由 `scripts/build_paper_numbers.py` 生成)

## Figures(`figures/`)
- `fig1_60cell_heatmap.pdf` — 60-cell SMS 热力图
- `fig2_aligned_vs_cross_box.pdf` — aligned vs cross 箱线图
- `fig3_class_forest.pdf` — 跨类 SMS forest plot
- `fig4_sms_vs_c1share.pdf` — SMS vs C1_share 散点(per cell, n=60)
- `fig5_sms_vs_pc.pdf` — SMS vs PC 散点(per PUT, n=12)

## License
MIT(见 `LICENSE`)

## Citation
```
@article{[author]2026sms,
  title={Semantic Mutation Score: A Metamorphic-Testing Adequacy Metric for Scientific Computing},
  author={[author], [coauthor]},
  journal={Information and Software Technology},
  year={2027 (under review)}
}
```
```

- [ ] **Step 9.2: 验收**

**验收标准:**
- [ ] `DATASET.md` 存在,行数 ≥ 50
- [ ] 文件包含 11 个 `data/results/*.json` 路径(grep 计数)
- [ ] 文件包含 5 个 `figures/*.pdf` 路径
- [ ] 文件包含 "Citation" 段落

Run:
```bash
test -f DATASET.md && wc -l DATASET.md
grep -c "data/results/" DATASET.md   # 应 ≥ 11
grep -c "figures/fig" DATASET.md     # 应 ≥ 5
grep -c "Citation" DATASET.md        # 应 ≥ 1
```

- [ ] **Step 9.3: 提交**

```bash
git add DATASET.md
git commit -m "docs: DATASET card with full per-artifact provenance"
```

---

## Task 10: LICENSE(MIT)

**Files:**
- Create: `LICENSE`

- [ ] **Step 10.1: 创建 MIT LICENSE**

```
MIT License

Copyright (c) 2026 [Author Name](见论文署名)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

保存为 `LICENSE`。

- [ ] **Step 10.2: 验收**

- [ ] `LICENSE` 存在
- [ ] 文件包含字串 "MIT License" 和 "Permission is hereby granted"

Run:
```bash
test -f LICENSE
grep -c "MIT License" LICENSE
grep -c "Permission is hereby granted" LICENSE
```

- [ ] **Step 10.3: 提交**

```bash
git add LICENSE
git commit -m "docs: MIT license"
```

---

## Task 11: 自审 + RQ-completion 表

**Why eleventh:** 全文最后一遍审阅,生成 RQ-completion 自审表 + 投稿就绪决定。

**Files:**
- Create: `docs/superpowers/notes/2026-05-01-self-review-rq-completion.md`

- [ ] **Step 11.1: 全文 placeholder 扫描**

```bash
grep -nE "TODO|TBD|FIXME|placeholder|<[A-Z_]+>" 论文初稿P2.md REPRODUCIBILITY.md DATASET.md
```
Expected: 无命中(无任何遗留占位符)。如有命中,逐条修复。

- [ ] **Step 11.2: 检查每个 RQ 的四要素(数据表、figure、章节描述、讨论)**

```bash
# RQ1: 数据表 in §5.6.1, fig1 引用 in §5.6.1, fig4 引用 in §5.6.2, 讨论 in §6.1
grep -c "图 1" 论文初稿P2.md   # ≥ 2(§5.6.1 和 §5.5)
# RQ2: 数据表 in §5.7.1, fig2 引用, Cliff's δ + CI, §6.1 讨论
grep -c "图 2" 论文初稿P2.md   # ≥ 2
grep -c "Cliff" 论文初稿P2.md  # ≥ 1
# RQ3: 类均值 in §5.8.1, fig3 引用, sign test, §6.3 讨论
grep -c "图 3" 论文初稿P2.md
# RQ4: PC 表 in §5.9.1, fig5 引用, Spearman, §6.4 讨论
grep -c "图 5" 论文初稿P2.md
grep -c "Spearman" 论文初稿P2.md  # ≥ 1
```

- [ ] **Step 11.3: 写自审记录**

Create `docs/superpowers/notes/2026-05-01-self-review-rq-completion.md`:

```markdown
# P2 RQ-Completion Final State(post-spiral 14 轮)

| RQ | Coverage | 关键证据 | 未结清项 |
|----|----------|----------|----------|
| RQ1 | 95% | Track-2 v2 60-cell heatmap;LRCA C1_share 表;H1 ✓;H5 见 paper_numbers.rq1.h5_pass_ratio | 无阻断 |
| RQ2 | 90% | Cliff's δ = paper_numbers.rq2.cliffs_delta + 95% CI;aligned/cross 箱线图;**H2 形式上未达成大效应阈值,但 CI 下限 > 0 提供方向证据**(§5.7.2 + §6.1 诚实声明) | H2 阈值未越,作为 limitation 而非阻断 |
| RQ3 | 85% | 类均值 + sign test + forest;**MixedLM 主模型 Singular,fallback Group Var 退化**(§5.8.3 + §7.2.2 R6 扩展) | mixed-effects 不可用;以 sign test 为正式结论 |
| RQ4 | 60% | SMS vs PC Spearman + Kendall(n=12 PUT);scatter | PC 定义保持最简,留待 P4 扩展 |

## 投稿就绪决定

| 维度 | 状态 |
|---|---|
| 实证数据完整性 | ✓ |
| 章节完整性(§1-§9) | ✓ |
| 诚实声明(H2 / RQ3 mixed-effects) | ✓ |
| 复现性文档(REPRODUCIBILITY.md / DATASET.md / LICENSE / requirements-frozen) | ✓ |
| 图表 5/5 | ✓ |

**结论**:可投稿。建议把 H2 形式上未达成 + RQ3 mixed-effects 退化作为审稿人最可能 challenge 的两项,在 cover letter 中预先声明,并指向 §5.7.2 / §5.8.3 / §6.1 / §6.3 / §7 R6+R9+R10 的内文交叉引用。

## 推荐下一步(out of scope of this plan)

1. journal-formatting pass(LaTeX 转换、图分辨率)— 见 spiral 计划 Round 15(可选)
2. P4 论文规划:RQ4 PC 扩展 + 30 mutant/PUT 重测 H2(§7.1.6 R9 已铺路)
```

- [ ] **Step 11.4: 验收**

**验收标准:**
- [ ] 自审文件存在
- [ ] 文件包含 RQ1/RQ2/RQ3/RQ4 四行的 RQ-completion 表
- [ ] 文件包含"投稿就绪决定"段落
- [ ] 全仓 grep `TODO|TBD|FIXME|<[A-Z_]+>` 在 `论文初稿P2.md`、`REPRODUCIBILITY.md`、`DATASET.md` 上不命中

Run:
```bash
test -f docs/superpowers/notes/2026-05-01-self-review-rq-completion.md
grep -c "RQ1" docs/superpowers/notes/2026-05-01-self-review-rq-completion.md  # ≥ 2
grep -c "投稿就绪" docs/superpowers/notes/2026-05-01-self-review-rq-completion.md  # ≥ 1
grep -nE "TODO|TBD|FIXME|<[A-Z_]+>" 论文初稿P2.md REPRODUCIBILITY.md DATASET.md && echo "FAIL" || echo "OK clean"
```
Expected: 末行 `OK clean`

- [ ] **Step 11.5: 提交**

```bash
git add docs/superpowers/notes/2026-05-01-self-review-rq-completion.md 论文初稿P2.md REPRODUCIBILITY.md DATASET.md
git commit -m "review: RQ-completion sweep + submission-readiness decision"
```

---

## Self-Review(plan author)

**1. Spec coverage:**
- spiral Round 11(REPRODUCIBILITY/DATASET/LICENSE/requirements):Tasks 8 + 9 + 10 ✓
- spiral Round 12(§5.6-5.9):Tasks 2-5 ✓
- spiral Round 13(§6 + §7):Tasks 6 + 7 ✓
- spiral Round 14(self-review + RQ-table):Task 11 ✓
- 单一数字源 paper_numbers.json:Task 1 ✓

**2. Placeholder scan:**
- 论文章节模板里有 `< >` 包裹的占位符(<MEAN_SMS> 等),设计上要求 Step X.2 把它们替换为实际数字;Step X.3 验收里 `grep -E "<[A-Z_]+>"` 强制不命中。这是计划的强约束,不是计划级遗留。
- 无其他 TBD / TODO。

**3. Type consistency:**
- `paper_numbers.json` 的 key 在 Tasks 2-5 中一致引用(rq1.* / rq2.* / rq3.* / rq4.*)
- `<N_CELLS>` / `<MEAN_SMS>` 等占位符与脚本输出 key 一一对应
- 提交信息格式统一 `<scope>(paper): ...` / `docs: ...` / `feat(paper): ...` / `review: ...`

**4. 章节编号一致性:**
- 新 §6 是讨论,原 §6 工作量被改为 §8;§7 风险与局限保持原编号(其内子节扩充 R6/R8/R9/R10)
- 没有把 §7 误改成 §9——§7 在 Task 6 步骤里特意保留为 §7,只在 Task 7 内增添子节。

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-01-p2-paper-completion.md`.

Two execution options:

**1. Subagent-Driven**(推荐,11 个独立任务)— fresh subagent per task, two-stage review (spec compliance, then code/text quality), 较快迭代。

**2. Inline Execution** — 在当前 session 内用 superpowers:executing-plans 顺序执行,每 2-3 个 task 一个 checkpoint 让用户审阅。适合需要频繁人工 review 中文文本的场景。

哪种?

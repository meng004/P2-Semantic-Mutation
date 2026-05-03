# P2 原始数据 README — All Experiment Artefacts

**总量**: ~14 MB（mutant pools 6.4 MB + results 7.8 MB）/ 56 SSOT JSON / 304 mutant pool 目录 / 12 cosmic-ray sqlite / 470 raw API trial logs（gitignored）
**最后更新**: 2026-05-02

> 数据组织遵循 **single source of truth (SSOT)** 原则。每个 paper 数字都能追溯到一个 JSON 文件 + 一行 path。

---

## 目录速览

```
data/
├── mutants/              # LLM-generated mutant pools (6.4 MB)
│   ├── a1_pool_v4/       # ← v4 cross-source primary pool, paper-cited
│   ├── a1_pool_v3/       # ← v3 same-source baseline
│   ├── a1_pool/          # ← legacy pre-v3 (deprecated)
│   ├── a1_MP1_llm/       # ← raw LLM trials before V1-V4 prescreen
│   └── ... (12 PUTs × 4 variants = 48 directories minimum)
├── operator_campaign/    # campaign orchestration logs
│   ├── cache/            # response-level cache (single-source)
│   ├── cache_cross/      # response-level cache (cross-source v4)
│   ├── raw/              # 470 raw API trial JSONs (gitignored)
│   ├── v1_archive/       # earlier campaign run archive
│   ├── campaign_log.json # operator campaign telemetry
│   ├── registry.json     # operator catalogue (CE/OS/HP/TF/SI definitions)
│   └── v2_revised6.log   # final campaign console log
└── results/              # SSOT statistical outputs (7.8 MB)
    ├── paper_numbers_v{3,3b,4}.json    # ← headline numbers, the 3 SSOTs
    ├── lrca_60cell_v{3,3b,4}.json       # 60-cell LRCA breakdown
    ├── sms_track2_v{1..4}.json          # cell-level SMS tracking history
    ├── rq2_cliffs_delta_v{3,3b,4}.json  # Cliff's δ + 95% CI
    ├── rq2_power_*.json                 # power simulation
    ├── rq3_friedman_v{3b,4}.json        # Friedman χ² + per-class p
    ├── rq3_mixed_effects_v{3,3b,4}.json # primary mixed-effects
    ├── rq4_pattern_coverage_v{3,3b,4}.json # SMS-vs-coverage Spearman
    ├── cosmic_ray_*.json + .sqlite      # syntactic baseline (12 PUTs)
    ├── c_class_permutation_v4.json      # cross-cell exchangeability null
    ├── h5_sensitivity_v4.json           # H5 threshold sensitivity sweep
    └── operator_metrics.json            # operator-level aggregate stats
```

---

## 1. `data/mutants/` — LLM 生成的 mutant 池

### 1.1 命名约定

```
data/mutants/<put>_<variant>/<m##>_<put>_<operator><idx>_<llm>_<a##>.py
                              │
                              └─ 示例: m01_a1_CE1_claude_a02.py
```

| 字段 | 含义 | 取值 |
|------|------|------|
| `put` | PUT 标识 | `a1`...`a3`, `b1`...`b3`, `c1`...`c3`, `d1`...`d3` (12 个) |
| `variant` | 池版本 | `pool` (legacy) / `pool_v3` (v3) / `pool_v4` (v4 cross-source) / `MP{k}_llm` (per-MP raw) |
| `m##` | mutant 序号 | `m01`...`m99`，pool 内 1-base |
| `operator` | 算子类 | `CE` / `OS` / `HP` / `TF` / `SI`（个别 `CF` for class-specialisation） |
| `idx` | algorithm-class 内序号 | `1`...`5`，例如 `CE1` 是 CE 类内第 1 套 |
| `llm` | 生成源 | `claude` / `gpt` / `deepseek` / `mut1`（同源 baseline） |
| `a##` | trial attempt | `a01`...`a09`，3 trials × 3 sources |

### 1.2 各版本规模

| 版本 | 用途 | mutant 总数 | per-PUT 平均 | paper 引用 |
|------|------|------------|-------------|-----------|
| `_pool_v4` | **v4 cross-source primary** | **292** | **24.3** | §5 全部 v4 数字 |
| `_pool_v3` | v3 same-source baseline | ~280 | ~23 | §5.7 ablation v3 数据 |
| `_pool` | legacy（pre-v3） | ~210 | ~18 | DEPRECATED，不入论文 |
| `_MP{k}_llm` | per-MP raw（V1-V4 prescreen 前） | varies | varies | 仅过滤前调试用 |

每个 `.py` 文件是一个完整的 mutant 程序（替换 PUT 中相关函数），包含 docstring 标注 mutator type、source LLM、trial id。

### 1.3 V1-V4 prescreen gate

每个 mutant 在进入 `_pool_v{3,4}` 前必须通过 4 道 mechanical-validation gate：

- **V1 syntax**: Python AST parse 不报错
- **V2 type**: mypy --strict 通过
- **V3 unit-self-test**: PUT-defined `__test__()` self-call 不抛异常
- **V4 AVP-baseline**: 在 baseline ε_AVP 下 AVP(S_i, mr) 至少有一个 mr fail（确保 mutant 真正改变行为）

通过率：v4 集 333 候选 → 89% V1-V4 pass → 298 confirmed → 5 final-stage rejection → **292 入 v4 pool**。

---

## 2. `data/operator_campaign/` — Campaign Orchestration Logs

| 文件 | 大小 | 内容 | 用途 |
|------|------|------|------|
| `registry.json` | 11.1 KB | operator catalog（CE/OS/HP/TF/SI 定义、prompt 模板） | 算子注册表 |
| `campaign_log.json` | 5.2 KB | per-trial 时间戳、源 LLM、success/fail 状态 | API 调用审计 |
| `campaign_console.log` | 1.5 KB | latest campaign console 输出 | 调试 |
| `v2_console.log` | 21.5 KB | v2 campaign full output | 调试 |
| `v2_revised6.log` | 10.7 KB | v2 revised final console（投稿版） | 投稿 reproducibility |
| `cache/` | varies | per-prompt response-level cache（v3） | 重跑加速 |
| `cache_cross/` | varies | cross-source response cache（v4） | 重跑加速 |
| `raw/` | ~430 KB | **470 raw API trial JSONs（gitignored）** | API forensic only |
| `v1_archive/` | varies | v1 historical run（pre-pivot） | 历史归档 |

`raw/` 因 Zenodo 限额从 replication zip 中排除（详 `replication/REPRODUCIBILITY.md` §3）；如需可邮件向作者索取。

---

## 3. `data/results/` — SSOT Statistical Outputs

### 3.1 Headline 数字（paper §5 直接引用）

| 文件 | 大小 | 内容 | paper 段落 |
|------|------|------|-----------|
| **`paper_numbers_v4.json`** | 1.5 KB | **v4 primary headline (RQ1-RQ4)** | §5 全部 v4 |
| `paper_numbers_v3b.json` | 1.5 KB | v3b post-hoc primary MP shift | §3.4 + §5.7.2 |
| `paper_numbers_v3.json` | 1.5 KB | v3 same-source baseline | §5.7 ablation contrast |
| `paper_numbers.json` | 1.5 KB | latest re-build snapshot | re-run 时刷新（不入论文） |

每个 `paper_numbers_*.json` 结构：

```json
{
  "rq1": { "n_cells": 60, "mean_sms": 0.104, "median_sms": 0.0,
           "mean_c1_share": 0.2092, "mean_suspect_share": 0.7908, ... },
  "rq2": { "n_aligned": 12, "n_cross": 48, "cliffs_delta": 0.4392,
           "delta_ci_95_lo": 0.1267, "delta_ci_95_hi": 0.7396,
           "h2_threshold_delta": 0.474, "h2_delta_pass": false, ... },
  "rq3": { "class_mean_a/b/c/d": ..., "friedman_chi2": 15.30,
           "friedman_p": 0.0041, "friedman_per_class_p": {...} },
  "rq4": { "spearman_rho": 0.1628, "spearman_p": 0.6133, ... }
}
```

### 3.2 60-cell breakdown（cell-level）

| 文件 | 内容 |
|------|------|
| `lrca_60cell_v4.json` (186.7 KB) | 60 cells × LRCA breakdown（C1/C2/C3/C4/C5 per cell） — RQ1 cell-level data |
| `lrca_60cell_v3.json` / `_v3b.json` | 同上，v3 / v3b 版本 |
| `lrca_60cell.json` (legacy) | DEPRECATED，预 v3 版本 |
| `lrca_calibration.json` (2.3 KB) | LRCA 阈值校准曲线（C1/C2/C3 决策边界） |
| `sms_track2_v4.json` (137.3 KB) | 60 cells × SMS history（per-trial trace） — heatmap 数据源 |
| `sms_track2_v3.json` / `_v3b.json` | 同上，v3 / v3b 版本 |
| `operator_metrics.json` (4.9 KB) | per-operator aggregate（CE/OS/HP/TF/SI 单独统计） |

### 3.3 RQ2 详细输出

| 文件 | 内容 |
|------|------|
| `rq2_cliffs_delta_v{3,3b,4}.json` | δ + BCa 95% CI (B=10000) |
| `rq2_cliffs_delta_logit_v{3b,4}.json` | logit-link 备选模型（robustness） |
| `rq2_power_v4.json` (1.2 KB) | naive power（H_alt: aligned-cross diff = observed） |
| **`rq2_power_stipulated_v4.json`** (2.1 KB) | **stipulated δ_truth=0.474 power** — paper §5.7.2 49.1% 数字 |

### 3.4 RQ3 详细输出

| 文件 | 内容 |
|------|------|
| `rq3_friedman_v{3b,4}.json` | χ² + per-class p + Bonferroni × 4 |
| `rq3_mixed_effects_v{3,3b,4}.json` | mixed-effects primary + fallback 模型 |

注：v4 mixed-effects 主模型 `singular matrix` 失败，自动 fallback 到 `sms ~ class + operator + (1|put)` 报告，详 `paper_numbers_v4.json::rq3.fit_error` 字段。

### 3.5 RQ4 详细输出

| 文件 | 内容 |
|------|------|
| `rq4_pattern_coverage_v{3,3b,4}.json` | Spearman + Kendall（PUT 级排序相关） |

### 3.6 §3.5 AST overlap（语义 vs 语法 baseline）

| 文件 | 大小 | 内容 |
|------|------|------|
| **`cosmic_ray_12put_ast_diff.json`** | **11.4 KB** | **12 PUT 聚合 + per-class breakdown — paper §3.5 5.14% 数字源** |
| `cosmic_ray_a1_ast_diff.json` | 988 B | per-PUT AST diff（仅 a1 详细） |
| `cosmic_ray_{a1..d3}_summary.json` × 12 | ~660 B 每 | per-PUT cosmic-ray outcome 计数（KILLED / SURVIVED） |
| `cosmic_ray_{a1..d3}.sqlite` × 12 | 88 KB ~ 1.7 MB | cosmic-ray 工具原始 session 数据库 |

`cosmic_ray_12put_ast_diff.json` 结构：

```json
{
  "n_puts_with_cr_data": 12,
  "puts_with_cr_data": ["a1", ..., "d3"],
  "per_put": {
    "a1": { "n_p2_mutants": 30, "n_cosmic_ray_mutants": 201,
            "n_overlap": 0, "per_operator_class": {...} },
    ...
  },
  "aggregated": {
    "n_p2_total": 292,
    "n_cosmic_ray_total": 1250,
    "n_overlap_total": 15,
    "overlap_rate_overall": 0.0514,
    "per_class_aggregated": {
      "CE": {"n_p2": 64, "n_overlap": 5, "rate": 0.0781},
      "OS": {"n_p2": 60, "n_overlap": 7, "rate": 0.1167},
      "HP": {"n_p2": 72, "n_overlap": 0, "rate": 0.0},
      "TF": {"n_p2": 54, "n_overlap": 0, "rate": 0.0},
      "SI": {"n_p2": 33, "n_overlap": 0, "rate": 0.0},
      "CF": {"n_p2":  9, "n_overlap": 3, "rate": 0.3333}
    }
  }
}
```

### 3.7 §3.4 c-class permutation null

| 文件 | 内容 |
|------|------|
| **`c_class_permutation_v4.json`** | cross-cell exchangeability permutation null + Bonferroni × 5 — paper §3.4 v3b post-hoc disclosure 数字源 |
| `c_class_mp_ranking.json` | c-class 内 5 MP 排序（用于 v3b primary MP shift 判定） |

### 3.8 H5 sensitivity

| 文件 | 内容 |
|------|------|
| `h5_sensitivity_v4.json` (1.7 KB) | H5 阈值 0.10/0.15/0.20/0.25/0.30 sweep — paper §5.7.5 robustness check |

### 3.9 等价性诊断

| 文件 | 内容 |
|------|------|
| `equiv_diagnosis.json` (2.4 KB) | E1 / E2 / E1∧E2 三方一致性诊断 — paper Appendix A.3 trade-off 表数字源 |

### 3.10 LLM campaign 元数据

| 文件 | 内容 |
|------|------|
| `llm_campaign_log.json` (33.2 KB) | 全部 LLM 调用 log（包括 v3 + v4） — API 取证 |

### 3.11 Pilot（DEPRECATED）

| 文件 | 状态 |
|------|------|
| `pilot_results.json` (1.0 KB) | 早期 4-PUT pilot — 仅 pipeline validation，**不入论文**（per `MEMORY.md::project_pilot_results.md`） |

---

## 4. 文件层级 size 排行（前 15 大）

```
137.3 KB  data/results/sms_track2_v4.json         ← v4 60-cell SMS history
131.8 KB  data/results/lrca_60cell_v3.json
131.8 KB  data/results/lrca_60cell_v3b.json
186.7 KB  data/results/lrca_60cell_v4.json        ← v4 60-cell LRCA breakdown
 94.8 KB  data/results/sms_track2_v3.json
 94.8 KB  data/results/sms_track2_v3b.json
 93.1 KB  data/results/lrca_60cell.json
 66.7 KB  data/results/sms_track2_v2.json
 33.2 KB  data/results/llm_campaign_log.json
 27.0 KB  data/results/sms_track2_v1_backup.json
 11.4 KB  data/results/cosmic_ray_12put_ast_diff.json
  4.9 KB  data/results/operator_metrics.json
  2.4 KB  data/results/equiv_diagnosis.json
  2.3 KB  data/results/lrca_calibration.json
  2.1 KB  data/results/rq2_power_stipulated_v4.json
```

---

## 5. 数据 → 论文段落对照（reverse lookup）

| paper 数字 | SSOT 文件 | JSON 字段 |
|-----------|----------|-----------|
| **§Abstract**: δ = 0.439 | `paper_numbers_v4.json` | `rq2.cliffs_delta` |
| **§5 mean SMS = 0.104** | `paper_numbers_v4.json` | `rq1.mean_sms` |
| **§5 mean C1_share = 0.209** | `paper_numbers_v4.json` | `rq1.mean_c1_share` |
| **§5.7.1 δ = 0.439, CI = [0.127, 0.740]** | `rq2_cliffs_delta_v4.json` | top-level |
| **§5.7.1 v3 δ = 0.323** | `paper_numbers_v3.json` | `rq2.cliffs_delta` |
| **§5.7.1 v3b δ = 0.446** | `paper_numbers_v3b.json` | `rq2.cliffs_delta` |
| **§5.7.2 49.1% point-estimate power** | `rq2_power_stipulated_v4.json` | `point_estimate_power` |
| **§5.7.2 86.8% CI-lower power** | `rq2_power_stipulated_v4.json` | `ci_lower_power` |
| **§5.8 Friedman χ² = 15.30, p = 0.0041** | `rq3_friedman_v4.json` | top-level |
| **§5.8 class_mean_b = 0.148** | `paper_numbers_v4.json` | `rq3.class_mean_b` |
| **§5.8 c-class +91.4%** (v3b → v4) | computed: `(0.0894-0.0467)/0.0467 × 100` | `paper_numbers_v3b.json::rq3.class_mean_c` 与 v4 |
| **§5.7.4 Spearman ρ = 0.163, p = 0.613** | `rq4_pattern_coverage_v4.json` | top-level |
| **§3.5 5.14% AST overlap** | `cosmic_ray_12put_ast_diff.json` | `aggregated.overlap_rate_overall` |
| **§3.5 HP/SI/TF = 0/0/0** | `cosmic_ray_12put_ast_diff.json` | `aggregated.per_class_aggregated.{HP,SI,TF}.n_overlap` |
| **§3.5 P2 total = 292, CR = 1,250** | `cosmic_ray_12put_ast_diff.json` | `aggregated.{n_p2_total, n_cosmic_ray_total}` |
| **§3.4 v3b permutation p** | `c_class_permutation_v4.json` | top-level |

---

## 6. 历史版本与归档

| 目录 / 文件 | 状态 | 备注 |
|------------|------|------|
| `data/mutants/*_pool/` | DEPRECATED | pre-v3 legacy 池，仅历史归档保留 |
| `data/results/lrca_60cell.json` | DEPRECATED | 同上 |
| `data/results/sms_track2.json` | DEPRECATED | 同上 |
| `data/results/sms_track2_v1_backup.json` | ARCHIVE | v1 历史快照 |
| `data/results/sms_track2_v2.json` | ARCHIVE | v2 历史快照 |
| `data/operator_campaign/v1_archive/` | ARCHIVE | v1 campaign 归档 |
| `data/results/pilot_results.json` | DEPRECATED | pilot only, 不入论文 |

**Paper 引用版本**: 永远使用 `*_v4.json` 系列（v4 cross-source primary）；v3 / v3b 仅用于消融对比。

---

## 7. 数据完整性 checksum

`replication/MANIFEST.txt` 提供 684 个文件的 SHA256 + size + relative path。重要 hash：

```bash
# 验证 paper headline 数字（如这些 hash 变了，代表数据被改动）
sha256sum data/results/paper_numbers_v4.json
sha256sum data/results/cosmic_ray_12put_ast_diff.json
sha256sum data/results/rq2_cliffs_delta_v4.json
sha256sum data/results/rq3_friedman_v4.json
```

---

## 8. 引用与许可

- **代码**: MIT License（见 `LICENSE`）
- **数据**: CC-BY-4.0（约定，非 zenodo 强制；详 `replication/.zenodo.json`）

引用格式见 `QUICK_START.md` §8。

# P2 实验指导（Quick-Start Replication & Extension Guide）

**目标**: 让任何人在 30 分钟内复现 paper §5 全部 headline 数字；在半天内扩展到新 PUT / 新算子 / 新 LLM 源。
**最后更新**: 2026-05-02
**配套文档**: `EXPERIMENT_DESIGN.md`（实验设计）、`DATA_README.md`（原始数据清单）、`replication/REPRODUCIBILITY.md`（Zenodo 端复现）。

---

## 0. 复现优先级

如果你只想验证 paper 的 headline 数字 → **走 §1（5-min cache replay）**。
如果你想重跑 LLM 生成 mutant（重新做实验）→ 走 §2（需 API key + 半小时 ~ 3 小时）。
如果你想扩展（新 PUT / 新算子 / 新 LLM）→ 走 §3。
如果你只想读懂数据组织 → 直接读 `DATA_README.md`。

---

## 1. 五分钟 cache replay（推荐起点）

> **前置**: Python 3.11+ / macOS 或 Linux / 8 GB RAM。**不需要 API key**。所有 mutant 池已在 `data/mutants/*_pool_v4/` 持久化。

```bash
# 1. 安装依赖
git clone <repo>           # 或 unzip replication/replication.zip
cd <repo>                  # 或 cd p2-sms-replication-v1.0.0/
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-frozen.txt

# 2. 运行三条复现命令（全部使用 cache，无 API call）
python3 scripts/build_paper_numbers.py --variant v4   # → data/results/paper_numbers_v4.json
python3 scripts/compute_rq2.py            --variant v4   # 确认 Cliff's δ = 0.4392
python3 scripts/compute_rq3_friedman.py   --variant v4   # 确认 χ² = 15.30, p = 0.0041

# 3. 校验
python3 scripts/show_numbers.py
```

**期望输出**（精确到 4 位小数）:

```
RQ1: mean_c1_share = 0.2092, mean_sms = 0.1040
RQ2: Cliff's δ = 0.4392, 95% CI = [0.1267, 0.7396]
     H2 (δ ≥ 0.474): NOT MET
RQ3: Friedman χ² = 15.30, p = 0.0041
     class_mean_c = 0.0894 (v4) — vs v3b 0.0467 (+91.4%)
RQ4: Spearman ρ = 0.1628, p = 0.6133
AST overlap (12 PUT): 5.14% overall; HP/TF/SI = 0/0/0
```

**全部数字应与 paper §5 完全一致**。如有偏差先看 §6 排错。

---

## 2. 重跑 LLM 生成（需 API keys）

> **前置**: 完成 §1 + 配置三个 API key。**注意**: temperature=0 但 LLM endpoint 偶有 non-byte-identical 输出，重跑后 mutant 池可能与 committed `_pool_v4/` 略有差异。如想精确复现 paper 数字，**用 §1 cache replay**。

### 2.1 配置 API（创建 `.env`）

```bash
cp .env.example .env
# 编辑 .env，填入：
ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_API_KEY>     # Claude Opus 4.6 (主生成器)
BLTCY_BASE_URL=<YOUR_BASE_URL>                  # GPT-5.4 reviewer; OpenAI-compatible 端点
BLTCY_API_KEY=<YOUR_API_KEY>
DEEPSEEK_BASE_URL=<YOUR_BASE_URL>               # DeepSeek 官方或兼容端点
DEEPSEEK_API_KEY=<YOUR_API_KEY>                 # DeepSeek-chat arbitrator on UNCERTAIN
```

### 2.2 三阶段消融重跑（v3 → v3b → v4）

```bash
# v3 same-source（仅 Claude，约 30 min, ~$5 API）
python3 scripts/operator_campaign.py --llm claude --variant v3 \
        --puts a1,a2,a3,b1,b2,b3,c1,c2,c3,d1,d2,d3 --trials 3

python3 scripts/run_lrca.py        --variant v3
python3 scripts/build_paper_numbers.py --variant v3
python3 scripts/compute_rq2.py     --variant v3   # δ = 0.323

# v3b post-hoc primary MP shift（同源数据，仅切 c-class primary MP）
python3 scripts/select_c_primary.py --shift MP5_to_MP1 --variant v3b
python3 scripts/build_paper_numbers.py --variant v3b
python3 scripts/compute_rq2.py     --variant v3b  # δ = 0.446

# v4 cross-source（Claude + GPT + DeepSeek，约 90 min, ~$15 API）
python3 scripts/cross_source_campaign.py --variant v4 \
        --sources claude,gpt,deepseek --trials 3 --temperature 0
python3 scripts/run_lrca.py        --variant v4
python3 scripts/build_paper_numbers.py --variant v4
python3 scripts/compute_rq2.py     --variant v4   # δ = 0.439
```

### 2.3 AST overlap 重跑（需 cosmic-ray 工具）

```bash
pip install cosmic-ray==8.3.6
# 12 PUT cosmic-ray 批量运行（约 20 min）
for put in a1 a2 a3 b1 b2 b3 c1 c2 c3 d1 d2 d3; do
  cosmic-ray init .cr-${put}.toml session-${put}.sqlite
  cosmic-ray exec session-${put}.sqlite
done

# AST diff 比对（约 5 min）
python3 scripts/p2_vs_syntactic_ast_diff_batch.py \
        --p2-pool-dir data/mutants \
        --cosmic-ray-dir . \
        --output data/results/cosmic_ray_12put_ast_diff.json
```

### 2.4 Stipulated-alternative power 重算

```bash
python3 scripts/compute_rq2_power_stipulated.py \
        --delta-truth 0.474 --n-aligned 12 --n-cross 48 \
        --n-replications 10000 --seed 42
# 期望: point-estimate power ≈ 49.1%, CI-lower power ≈ 86.8%
```

---

## 3. 扩展实验（Extension）

### 3.1 加新 PUT

> **场景**: 第 13 个 PUT，例如 `e1` (FFT)，归类 E (signal-processing)

```bash
# Step 1. 实现 PUT
echo 'def put(x: float) -> float: ...' > src/puts/e1.py
# Step 2. 在 P1 提供的 MR meta-pattern infra 上注册 e1 的 5 个 MP
python3 scripts/gen_mr_json.py --put e1 --mps MP1,MP2,MP3,MP4,MP5
# Step 3. 跑 operator campaign（需 API）
python3 scripts/cross_source_campaign.py --variant v4_plus_e1 \
        --puts e1 --sources claude,gpt,deepseek --trials 3
# Step 4. 重新聚合（v4 → v4_plus_e1）
python3 scripts/run_lrca.py --variant v4_plus_e1
python3 scripts/build_paper_numbers.py --variant v4_plus_e1
# Step 5. cosmic-ray AST diff（如需对比语法）
cosmic-ray init .cr-e1.toml session-e1.sqlite
cosmic-ray exec session-e1.sqlite
python3 scripts/p2_vs_syntactic_ast_diff.py --put e1
```

**注意**: 扩展到 13+ PUT 后，stipulated power 会上升（n_aligned ≥ 13），可考虑同时调整 H2 阈值复算 power 表。

### 3.2 加新算子

> **场景**: 第 6 个 meta-mutation operator class，例如 `mut_X` = "Boundary Inversion"

```bash
# Step 1. 在 src/mutators/ 加 prompt template
cat > src/mutators/mut_X_boundary_inversion.txt <<'EOF'
You are a domain expert. Generate a mutant that inverts the
domain boundary condition (e.g., x ≥ 0 → x > 0)...
EOF
# Step 2. 注册到 operator catalog
python3 scripts/operator_campaign.py --register mut_X --class BI \
        --conditions "cross_function=true,domain_knowledge=true,algorithmic_class_change=true"
# Step 3. 跑 60 cells × 3 trials × 3 LLMs
python3 scripts/cross_source_campaign.py --variant v5 \
        --operators mut_C,mut_M,mut_G,mut_T,mut_F,mut_X \
        --sources claude,gpt,deepseek
# Step 4. 重算 SMS / Cliff's δ / Friedman
python3 scripts/build_paper_numbers.py --variant v5
```

**注意**: 加新算子后 60 cells → 72 cells（12 PUT × 6 MP/operators），Friedman df 增加，per-class p-value 需重 Bonferroni 校正。

### 3.3 加新 LLM 源

> **场景**: 第 4 个 LLM，例如 Gemini Pro 2.5

```bash
# Step 1. 实现 LLM adapter（参考 src/llm_adapters/claude.py）
cat > src/llm_adapters/gemini.py <<'EOF'
class GeminiAdapter(BaseLLMAdapter):
    def generate(self, prompt: str, temperature: float = 0) -> str:
        # implement google.generativeai client
        ...
EOF

# Step 2. .env 加 GOOGLE_API_KEY
# Step 3. 跑 v4_plus_gemini
python3 scripts/cross_source_campaign.py --variant v4_plus_gemini \
        --sources claude,gpt,deepseek,gemini --trials 3
# Step 4. 报告 4-source mean C1_share 与 v4 3-source 对比
```

**预期**: 第 4 个源进一步提升 c1_share 边际收益约 +1~2pp（参考 paper §6.2 saturation 讨论）。

### 3.4 调整 LRCA 阈值

```bash
# H5 sensitivity sweep（验证 0.20 阈值的稳健性）
python3 scripts/h5_sensitivity.py \
        --thresholds 0.10,0.15,0.20,0.25,0.30 \
        --variant v4
# 期望: 阈值 0.15 → 0.25 范围内 H5 通过单元格数变化 ≤ 2
```

---

## 4. 关键 SSOT 文件索引

| 文件 | 内容 | 哪个数字来这 |
|------|------|-------------|
| `data/results/paper_numbers_v4.json` | RQ1-RQ4 全部 headline | §5 所有 v4 数字 |
| `data/results/paper_numbers_v3.json` | v3 baseline | §5.7 ablation v3 contrast |
| `data/results/paper_numbers_v3b.json` | v3b post-hoc primary MP shift | §3.4 + §5.7.2 |
| `data/results/lrca_60cell_v4.json` | 60 cells full LRCA breakdown | RQ1 cell-level |
| `data/results/cosmic_ray_12put_ast_diff.json` | 292 P2 vs 1,250 CR mutants AST diff | §3.5 + §6 AST overlap |
| `data/results/rq2_cliffs_delta_v4.json` | δ + 95% CI (BCa B=10000) | §5.7.1 RQ2 effect-size |
| `data/results/rq2_power_stipulated_v4.json` | 49.1% point-estimate power | §5.7.2 power calibration |
| `data/results/rq3_friedman_v4.json` | χ² + per-class p | §5.8 RQ3 |
| `data/results/c_class_permutation_v4.json` | cross-cell exchangeability null | §3.4 v3b post-hoc |

详细描述：见 `DATA_README.md`。

---

## 5. 常用命令 Cheatsheet

```bash
# 验证当前最新数字
python3 scripts/show_numbers.py

# 重新生成图（3 PNGs at 300 DPI）
python3 scripts/generate_figures.py --output figs/

# 重新构建 IST submission package
bash scripts/build_ist_submission_v2.sh
TEXINPUTS=./submission/texmf//: xelatex -output-directory=submission \
        submission/p2_ist_v2.tex                # 2 次 for refs

# 重新构建 replication zip（提交 Zenodo 前）
bash replication/build_zip.sh

# 翻译稿 CN → EN（需要 ANTHROPIC_API_KEY）
python3 scripts/translate_paper.py --section 3.2 --to en

# 跑全套测试
pytest tests/ -v
```

---

## 6. 排错（Troubleshooting）

| 症状 | 可能原因 | 修复 |
|------|---------|------|
| `paper_numbers_v4.json` 数字不一致 | 用了 v3 / v3b cache | `--variant v4` 显式指定 |
| BLTCY 代理 404 | base_url 双 `/v1` | `scripts/translate_paper.py` 已修，新 adapter 同样去除尾 `/v1` |
| Translation 截断 | max_tokens 不足 | 用 streaming + max_tokens=32000 |
| `singular matrix` in mixed-effects | random-effects 设计在 12 PUT 上欠秩 | 自动 fallback 到 `sms ~ class + operator + (1\|put)` |
| cosmic-ray 装不上 | Python 3.10+ 不兼容老版本 | 用 `cosmic-ray==8.3.6`（验证过） |
| LaTeX `Missing \begin{document}` | 模板里有 invalid `\providecommand{\begin{...}}` | 已修，参考 v2 build script |
| PDF 含黑方块（缺 glyph） | xelatex 字体不全 | 跑 `scripts/postprocess_unicode.py`，60+ Unicode → LaTeX 替换 |
| Mutant pool size 不等于 292 | v4 重跑后池子规模偶有 ±1~3 | LLM endpoint stochasticity，用 cache replay 走 §1 |

---

## 7. 计算资源预算

| 任务 | Wallclock | API 成本 |
|------|-----------|---------|
| Cache replay（§1） | < 5 min | $0 |
| v3 重跑 | ~30 min | ~$5 |
| v3b post-hoc | ~10 sec（同源数据，仅切 primary MP） | $0 |
| v4 cross-source 重跑 | ~90 min | ~$15 |
| cosmic-ray 12 PUT batch | ~20 min | $0 |
| LaTeX 重新编译 | ~15 sec | $0 |
| 翻译 CN → EN 整稿 | ~10 min | ~$10 |
| **全套从零重跑** | **~3 hours** | **~$30** |

笔记本（4 核 / 8 GB / Apple Silicon 或 x86_64）足够。

---

## 8. 引用

复现请引用：

```bibtex
@article{li2026sms,
  author    = {Meng Li},
  title     = {When Same-Prompt LLM Source Diversity Doesn't Help: An Ablation
               of Semantic Mutation Operators in Metamorphic Testing for
               Single-Output Scientific Computing Kernels},
  journal   = {Information and Software Technology},
  year      = {2026},
  publisher = {Elsevier},
  note      = {Replication: Zenodo DOI 10.5281/zenodo.<TBD>}
}
```

如果你只用 replication package 的 v4 数据，请额外引用：

```bibtex
@dataset{li2026sms_replication,
  author    = {Meng Li},
  title     = {p2-sms-replication-v1.0.0: Replication package for SMS metamorphic
               testing audit},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.<TBD>}
}
```

---

## 9. 联系

- 问题报 issue：（GitHub repo URL TBD）
- 邮件：mlemon@usc.edu.cn
- raw API trial logs（gitignored due Zenodo 限额）：邮件索取

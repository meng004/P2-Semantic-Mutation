# Reproducibility Guide for P2 Empirical Audit

## Environment

- Python 3.12.x(`.venv` 创建于本仓库根)
- 见 `requirements-frozen.txt` 的冻结依赖(包含 numpy / scipy / pandas / statsmodels / matplotlib / seaborn / openai / anthropic / pytest / python-dotenv / scikit-learn / fastdtw)
- LLM API 凭证:`.env` 文件(已 gitignore;LLM 配置见 `docs/superpowers/plans/2026-04-29-p2-experimental-infrastructure.md`)

## End-to-end reproduction(全程约 2-3 小时)

```bash
# 1. 创建 venv 并安装依赖
python3.12 -m venv .venv
.venv/bin/pip install -r requirements-frozen.txt

# 2. 运行单元测试
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

# 8. 渲染图(figures/fig{1-5}.pdf)
PYTHONPATH=src .venv/bin/python scripts/render_figures.py

# 9. 检查输出
ls -la data/results/ figures/
```

## 单步骤产物

| 步骤 | 主要输出 |
|---|---|
| 3 | `data/mutants/{put}_pool/m{NN}_{op_id}_a{NN}.py` × 12 PUT |
| 4 | `data/results/sms_track2_v2.json` |
| 5 | `data/results/lrca_60cell.json` |
| 6 | `rq2_cliffs_delta.json`, `rq3_mixed_effects.json`, `rq4_pattern_coverage.json` |
| 7 | `data/results/paper_numbers.json` — 所有论文数字单一来源 |
| 8 | `figures/fig{1..5}.pdf` |

## 复现性边界

- LLM-生成 mutant(`data/operator_campaign/raw/`)非确定性:Claude Opus 订阅接口无 seed 控制。Cache 已提交并视作冻结数据集,后续 metric 计算无需重新调用 LLM。
- 随机 PUT(b2 MCMC、b3 MC、c-class GPR、d1 MLP)的 SMS 估计在不同 RNG 种子间波动 ≈ 0.05 单位;N=20 重复降低但不消除。
- LRCA 阈值(OOD 0.05、tolerance 倍数 10×、N=20 majority)是工程选择,改变阈值会改变 C1_share,但不改变 SMS 数值本身。

## Provenance per artifact

见 `DATASET.md`。

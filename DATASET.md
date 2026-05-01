# P2 Dataset Card

## PUTs(`src/p2/puts/{a1..d3}.py`)

12 个科学计算程序,4 类(numeric / probabilistic / surrogate / ML),每个程序签名 `float → float`,deterministic-where-possible(stochastic PUT 接受 `random_state`)。

| Class | PUTs | Domain |
|---|---|---|
| a (numeric) | a1, a2, a3 | 线性代数 / 数值积分 / 多项式根 |
| b (probabilistic) | b1, b2, b3 | MCMC / Monte Carlo 积分 / 概率分布 |
| c (surrogate) | c1, c2, c3 | Gaussian Process / RBF / scikit-learn surrogate |
| d (ML) | d1, d2, d3 | MLP / decision tree / kNN(scikit-learn) |

## MRs(`src/p2/mrs/{a1..d3}.py`)

60 个 metamorphic relations,每 PUT 5 个 MP。强度标签 ●●/●/○ 在每个模块的 docstring 顶部声明,与 §3.3 矩阵一致。

## Mutation operators(`src/p2/mutators/operator_registry.py`)

37 个命名算子,5 类:CE(constant edit)/ OS(operator substitution)/ HP(hyperparameter)/ TF(transform)/ SI/CF(structural / control flow)。每条记录包含 target_locator + transformation + rationale + is_key 标记。is_key=True 的 12 个算子在 K=20 重复下生成。

## LLM-generated mutants

- `data/operator_campaign/raw/{op_id}.json` — 470 trials,含 prompt、raw LLM 响应、V1-V6 + operator_match 标签、reviewer 推理文本。
- `data/operator_campaign/cache/{op_id}_attempt{NN}.py` — 212 个 confirmed mutant(V1-V6 ✓ ∧ operator_match=Yes)。
- `data/mutants/{put}_pool/m{NN}_{op_id}_a{NN}.py` — per-PUT 池,12 mutants/PUT,operator-比例采样(`scripts/build_pools.py` 输出)。
- `data/mutants/{put}_MP{k}_llm/` — Phase 1 LLM campaign 留存的 45 个变异体(已被 v2 池取代,但保留供历史溯源)。
- `data/mutants/a2_MP1_mut1/`, `data/mutants/b2_MP2_mut1/` — 手工 pilot 变异体(校准用,§4.8 起始)

## Generation prompts

- `src/p2/mutators/prompts/operator_template.txt` — generator prompt(Claude Opus 4.6)
- `src/p2/mutators/prompts/operator_reviewer_template.txt` — reviewer prompt(GPT-5.4 via bltcy.ai)
- `src/p2/mutators/prompts/generator_template.txt` / `reviewer_template.txt` — Phase 1 (cell 级)模板,保留供对比

## Metrics outputs

- `data/results/operator_metrics.json` — R_sem / D_impl / R_kill per operator
- `data/results/sms_track1.json` — Track-1(12 主对齐单元格,Phase 1)
- `data/results/sms_track2.json` — Track-2 v1(60 cells, 4-5 mutants/cell)
- `data/results/sms_track2_v1_backup.json` — v1 备份(供 v1 vs v2 对比)
- `data/results/sms_track2_v2.json` — Track-2 v2(60 cells, 12 mutants/cell, N=20)— **本文主分析用**
- `data/results/sms_track2_v2_console.log` — v2 完整控制台日志
- `data/results/lrca_60cell.json` — per-cell C1/C2/C3/C4/Artifact 计数 + suspect_share
- `data/results/rq2_cliffs_delta.json` — Cliff's δ + 95% bootstrap CI
- `data/results/rq3_mixed_effects.json` — mixed-effects 主模型(Singular)+ fallback 模型
- `data/results/rq3_model_summary.txt` — fallback 模型完整摘要
- `data/results/rq4_pattern_coverage.json` — per-PUT PC + Spearman / Kendall
- `data/results/paper_numbers.json` — §5.6-5.9 引用的所有数字(由 `scripts/build_paper_numbers.py` 生成)
- `data/results/pilot_results.json` — Phase 1 pilot(A2_MP1, B2_MP2)
- `data/results/llm_campaign_log.json` — Phase 1 LLM campaign 日志

## Figures

- `figures/fig1_60cell_heatmap.pdf` — 60-cell SMS 热力图(rows = PUT, cols = MP, ★ 标对齐 cell)
- `figures/fig2_aligned_vs_cross_box.pdf` — aligned vs cross 箱线图
- `figures/fig3_class_forest.pdf` — 跨类 SMS forest plot(均值 ± SEM)
- `figures/fig4_sms_vs_c1share.pdf` — SMS vs C1_share 散点(per cell, n=60)+ Spearman ρ
- `figures/fig5_sms_vs_pc.pdf` — SMS vs PC 散点(per PUT, n=12)+ Spearman ρ

## License

MIT(见 `LICENSE`)。

## Citation

```
@article{author2026sms,
  title={Semantic Mutation Score: A Metamorphic-Testing Adequacy Metric for Scientific Computing},
  author={[author], [coauthor]},
  journal={Information and Software Technology},
  year={2027 (under review)}
}
```

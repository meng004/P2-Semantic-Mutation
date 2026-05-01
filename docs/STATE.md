# P2 项目状态（单一会话入口）

> 每次会话开始**只读这一个文件**即可定位。任何重大 commit 后请同步本文件 + 末尾 `last_synced` 日期。

**Last synced:** 2026-05-01（commit 2eb84ea 后）
**Stage:** Major Revision response 进行中（5 reviewer reports，15/28 项已 close）
**Repo:** `/Users/limeng/Library/CloudStorage/OneDrive-个人/0-论文/MR识别/MT完备性`
**Paper file:** `论文初稿P2.md`（83 KB，中文，仅 abstract+keywords 英文）

---

## 1. Reviewer 28 项进度

**已 close（15）：** P0: R-2, R-3, R-4, R-5, R-6, R-24 | P1: R-9, R-10, R-11 | P2: R-17, R-18, R-20, R-21, R-22, R-23

**Pending（13）：**
- **P0 blocker:** R-1（全文英文翻译，投稿必做）
- **P1:** R-7（reference 列表完整化）, R-8（SMS→MS theorem 形式化证明）
- **P2:** R-12/R-13（bootstrap B≥10000 + power analysis）, R-14（LRCA grid 扩展）, R-15（mutmut ablation）, R-16（differential prompt 实验）, R-19（stakeholder 章节）, R-25（artifact commitment / 复现性公开包）, R-26/R-27/R-28（杂项）

## 2. 论文章节状态（13 个 H1/H2）

| 章节 | 状态 |
|------|------|
| English Title / Abstract / Keywords | ✓ 已英文化（commit 64d580d） |
| §1 论文身份与命题 | ✓ 完整，H3 已撤回 |
| §2 语义变异符号系统 | ✓ 完整 |
| §3 实验对象与 60 单元格矩阵 | ✓ 完整（含 §3.1.1 PUT、§3.2.6 preventive defense） |
| §4 实验流程 | ✓ 完整（含 §4.2.5 cross-source v4 协议） |
| §5 统计分析方法 | ✓ 完整（§5.6/5.7/5.7.2/5.8/5.9 全部已落数字） |
| §6 讨论 | ✓ 完整（含 §6.1 v4 cross-source 叙事 + Petrović 重构） |
| §7 风险与缓解 + Limitations | ✓ 完整（含 R8-R10） |
| 全文英文版 | ✗ R-1 blocker，未完成 |

## 3. 关键 artifacts（v4 = primary）

**最新数字源：** `data/results/paper_numbers_v4.json`
- RQ1: mean SMS = 0.104, n_zero=45/60, mean C1_share = 0.209
- RQ2: Cliff's δ = **0.439**（CI [0.109, 0.748]，未达 0.474 阈值，H2 rejected）
- RQ3: Friedman χ² = 15.30, **p = 0.0041**（b 类内 p=0.029）；mixed-effects singular
- RQ4: Spearman ρ = 0.163, p = 0.613（H6 几乎独立 ✓）

**v4 cross-source LRCA：** `data/results/lrca_60cell_v4.json`
**v4 SMS：** `data/results/sms_track2_v4.json`

## 4. 代码主线

- PUTs: `src/p2/puts/{a1-d3}.py`（12 个）
- MRs: `src/p2/mrs/{a1-d3}.py`（12 个）
- AVP / LRCA / equiv / stats: `src/p2/{avp,lrca,equiv,stats}/`
- LLM 三家客户端: `src/p2/mutators/llm_client.py`（Claude Opus G / GPT-5.4 R1 / DeepSeek R2）
- Campaign 脚本: `scripts/{cross_source_campaign,sms_campaign,run_lrca,build_paper_numbers,compute_rq{2,3,4}}.py`

## 5. 已弃数据（避免误用）

- `paper_numbers.json` / `_v3.json` / `_v3b.json` → 已被 v4 supersede
- 早期 manual pilot（`a2_MP1_mut1`, `b2_MP2_mut1`）→ 仅为 pipeline 验证，**不入论文**
- LLM-only 单源 v2（`*_pool/`）→ 已被 cross-source v4（`*_pool_v4/`）supersede

## 5.1 ⚠️ 遗留不一致（2026-05-01 发现）

`SMS_VERSION=v4 .venv/bin/python scripts/build_paper_numbers.py` 重算结果与 `paper_numbers_v4.json`（论文 §5.7 引用源）**不一致**：
- 论文/已 commit 的 v4: `mean_aligned=0.275, median_aligned=0.267, sign_test=4`
- 重算的 v4: `mean_aligned=0.213, median_aligned=0.1, sign_test=3`
- 关键的 `cliffs_delta=0.439` 与 `friedman_chi2=15.30` **未变**

成因待查：可能是 `sms_track2_v4.json`（或上游 PRIMARY_CELLS / lrca_60cell_v4.json）在 paper_numbers_v4.json 落地后又被某次 commit 更新过。修复前 **不要重新运行 build_paper_numbers.py 写 v4**（默认值 SMS_VERSION=v3 已恢复以避免误触发）。

调查路径：
1. 比对 `git log --follow data/results/sms_track2_v4.json` 与 `paper_numbers_v4.json` 的提交时间
2. 决定取舍：(a) 重新生成 paper_numbers_v4.json + 同步更新论文 §5.7 数字；或 (b) 锁定旧 sms_track2_v4 / lrca_60cell_v4 快照保护当前论文引用

## 6. 下一步候选（按 ROI）

1. **R-1 全文英文翻译**（P0 blocker；~1 周；解锁投稿）
2. **R-25 artifact 公开包**（REPRODUCIBILITY 扩充 + Zenodo DOI；~3-5 h）
3. **R-7/R-8 引用 + 定理证明**（P1；~1-2 天）
4. **R-12/R-13 bootstrap + power analysis**（P2；~半天，提升 H2 可辩护性）

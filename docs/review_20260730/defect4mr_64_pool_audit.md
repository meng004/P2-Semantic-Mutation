# Defect4MR 64 池工件审计

**审计日期：** 2026-07-30  
**目标：** 确定 Phase 3.1 所称 Defect4MR 64 池的权威来源、精确文件、稳定版本与可执行边界。  
**访问方式：** 已认证 GitHub 只读访问；临时克隆用于本地一致性测试，未修改远程仓库。

## 1. 仓库身份

用户提供的 `https://github.com/meng004/defect4mr` 解析为：

- canonical repository：`https://github.com/meng004/P12-Defect4MR`
- visibility：private
- default branch：`main`
- pinned commit：`2bf7c2401c846544e715d879eb639e8c3bf44067`
- commit date：2026-07-07T13:09:11Z

本研究不得直接跟随 `main` 漂移；Phase 3 导入必须固定到上述 commit。

## 2. 64 池 SSOT

权威池文件：

```text
data/ledgers/candidates.json
```

文件 blob SHA：

```text
1469a2e2b15dcb2cdf59d185f3ec92f58fb77189
```

仓库 `README.md` 将该文件标为 authoritative defect ledger。固定提交的解析结果：

| status | 数量 |
|---|---:|
| `verified_full` | 35 |
| `candidate_full` | 16 |
| `rejected` | 12 |
| `candidate_needs_oracle` | 1 |
| **合计** | **64** |

台账覆盖 31 个项目标签。每条记录包含 `provisional_id`、项目、来源 URL、buggy/fixed revision 描述、modified files、排除检查、复现风险和 reviewer note；同时也包含 `mr_mapping` 与 `proposed_mr_oracle`。

`schemas/candidate.schema.json` 是 entry schema。由于 admission 必须与 MR/kill 信息解耦，原始 ledger 不能直接交给准入裁决会话，应机械生成 sanitized manifest 并剔除 `mr_mapping`、`proposed_mr_oracle` 及全部 mutation/kill 字段。

## 3. 版本选择

仓库最新 release tag `v1.0.1` 指向 commit `3639356ff11c5907d8ca45b0fe64ffe6d7543017`，其状态分布为：

- 34 `verified_full`
- 17 `candidate_full`
- 12 `rejected`
- 1 `candidate_needs_oracle`

这与论证提升计划使用的 35/16 口径不一致。因此当前 Phase 3 应钉扎 `2bf7c240...`，不能使用 `v1.0.1` 替代。后续若需要迁移到新 release，必须单独记录版本迁移与计数变化。

## 4. 关联证据与复现入口

| 工件 | 作用 | 审计结论 |
|---|---|---|
| `reports/cloud/<case>-verification.md` | 逐案双臂验证报告/构建配方 | 35 个 verified 中 34 个有同名报告；A-MAGMA-002 使用 GPU round judgment 报告 |
| `scripts/cloud/<case>-verification/` | 逐案验证脚本 | 34 个 verified 有同名目录；A-MAGMA-002 为 GPU 特殊路径 |
| `data/registry/cases.yaml` | 人类权威运行注册表 | 35 个 ID，与 verified_full 完全一致 |
| `data/registry/cases.json` | CLI 读取的 machine twin | 35 个 ID，与 YAML 由测试保持同步 |
| `tools/d4mr/` | `list/info/checkout/run/verify` CLI | 支持双臂判决与全套验证 |
| `docs/d4mr-CONTRACT.md` | 容器、判决 JSON 和退出码契约 | contract version 1 |
| `data/mutation/` | 变异实验与 real-defect face | 不是 64 池准入 SSOT |
| `data/kappa/` | 既有 14 例标注材料 | 不是 64 池，也不能替代本研究预注册抽样 |

注册表 35 个案例中：

- tier A：34
- tier B：1（`A-MAGMA-002`，需要 GPU）
- 已填容器 digest：3
- `digest: null`：32

所以仓库已经足以启动 64 池导入、重裁和证据复核，但不足以保证 35 例全部通过一次 `docker pull` 直接重跑。3 个 digest-pinned 案可优先使用 `tools.d4mr verify`；其余案例应依据 verification report 重建，或先完成镜像发布与 digest 固定。

仓库 README 还披露 build tree 不随仓库发布，`case*.json` 的 `build_cmd` 可能指向 gitignored `work/`。这进一步说明“有记录”与“当前 VM 可直接复现”必须分开编码。

## 5. 完整性验证

在固定提交的临时克隆中执行：

```text
python3 -m unittest discover -s tests -q
```

结果：

```text
Ran 71 tests in 0.058s
OK
```

额外集合核对：

- `verified_full` IDs：35
- registry IDs：35
- missing in registry：0
- extra in registry：0

## 6. 对 Phase 3 的直接结论

1. “Defect4MR 64 池工件不可用”这一 blocker 已解除。
2. Task 3.1 必须先做一次性、可验证、去 MR/oracle 字段的 sanitized import。
3. 原仓库 status 是输入证据，不自动等于 P3 三条准入协议的最终裁决。
4. 全部 64 条都要留下重裁结果；不能只抽取 35 verified。
5. 9 行补充挖掘试点继续保留，但仅作为 supplemental source。
6. readiness 目标仍需在当前执行环境重新验证；仓库中的历史 `verified_full` 不等于 P3 的 `crit_dual_arm_repro=PASS`。

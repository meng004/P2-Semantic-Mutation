# 2026-07-08 TOSEM 稳定接收 LOOP（round-11 起）

状态：ROUND-1 REVIEW · 基线：commit bd24ac1（main 45pp / supplementary 22pp，Phase B 全绿）
Worker 模型：claude-opus-4-8-thinking-high · 评审对象：submission/TOSEM_regular_20260707/{main,supplementary}.tex

## 循环结构

```
[评审] 5 独立 reviewer 并行（互不可见）→ 报告落盘 docs/review_2026-07-08/
  ↓
[合议] 协调者综合 5 份报告 → editorial decision + 修复 roadmap（优先级 P0/P1/P2）
  ↓
[修复] 文件不相交的并行 worker 执行 P0/P1；每 worker 完成即验收评审（命令实跑 + 漂移检查）
  ↓
[复审] re-review 模式核对每条意见是否关闭 → 未达标回到[修复]
```

## 稳定接收判据（结束条件，可量化）

1. 5/5 reviewer verdict ≥ Minor Revision conditional Accept；
2. Devil's Advocate 零 CRITICAL；
3. 全部 P0 修复项关闭且有验收命令证据；
4. Phase B 构建门禁保持全绿。

安全阀：最多 3 轮循环；3 轮后仍未达标则如实向用户报告残余差距与原因，不降低判据凑数。

## 评审团配置（Phase 0 persona）

| ID | 角色 | 关注面 | 报告文件 |
|---|---|---|---|
| R0 | TOSEM EIC（软件测试方向） | 期刊契合、贡献量级、可发表性 | r0_eic.md |
| R1 | 实证 SE 方法学家 | 预注册、统计效度、功效、多重比较、可复现性 | r1_methodology.md |
| R2 | 变异测试/蜕变测试领域专家 | 文献定位、新颖性、与 SOTA 关系 | r2_domain.md |
| R3 | 科学计算工业 V&V 实践者 | 外部效度、可用性、部署约束 | r3_perspective.md |
| R4 | Devil's Advocate | 最强反论证、cherry-picking、逻辑链 | r4_devils_advocate.md |

诚实性硬约束（所有 reviewer）：每条批评必须给行号定位；每条涉数据断言必须现场运行命令核验
（rg / 读 data/results/*.json / gh api 拉 Defect4MR 归档）；禁止凭空引文；铁律：不得修改稿件。

## 轮次日志

- Round-1 评审：5 reviewer 已启动（2026-07-08 14:32）。

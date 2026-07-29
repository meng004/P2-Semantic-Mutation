# EIC Round-2：对初稿计划 v1.0 的评估（2026-07-10，用户转达）

> 输入：`research/paper-draft-plan-mr-adequacy-tosem.md` @ 233e89e
> verdict：从 Reject—Premature 提升为"鼓励按该方案完成实验后重新投稿；但当前仍不具备稳定接收条件"。
> 回应设计评分 ≈ 8/10；问题实际关闭程度 ≈ 3/10（决定性实验未执行，旧阻断项未逐项验收）。

## 一、逐项核对上一轮 P0 阻断

| 上轮阻断项 | 本方案回应 | EIC 判断 |
|---|---|---|
| P0-1：denominator 与构念不一致 | 新建 MR-free Fault Card 池，仅 A–C 级独立认证对象进入 primary denominator；旧 292 个变异体全部降为 pilot | 强回应，但需收紧表述 |
| P0-2：formal layer 错误 | 上游提纲已取消 fiber/duality 表述，经典 MS 改为结构特化，不再宣称 identity-MR degeneration；HOM 缩窄为特定默认一阶工具观察 | 基本回应，但缺独立形式审计 |
| P0-3：Study 4 confirmatory license 不成立 | Studies 2–4 移出正文，降为补充材料或后续论文 | 条件性回应 |
| P0-4：缺少独立 human/cross-model validity gate | A–C 证书替代 AI 标签作为准入依据，D 级只做敏感性分析并引入第二评者 | 部分回应，仍不充分 |
| P0-5：缺少独立 decision value | 预注册、双盲、dev/holdout、同预算四策略 DVE + 无 MR-detectability 准入历史缺陷臂 | 最强、最直接的回应 |
| P0-6：投稿包不 submission-ready | 仅 M8 笼统"投稿流水线全绿"，未逐项处理 DOI、NOETHER disclosure、占位符、补充材料许可 | 尚未真正回应 |

## 二、最重要的进步（EIC 认可项）

1. 有了可被记住的一句话主张（SMS 帮助有限预算下选择更有价值的 MR）。
2. 循环论证在程序设计层面得到正面解决。
3. 定义性结论与经验性贡献分开（H-DV 可证伪）。
4. null-result 条款提高方法学可信度。

## 三、最大剩余风险

主实验仍可能被解读为"SMS 在与其训练缺陷池同分布的人工语义变异体上优于随机方法"，弱于"改善真实软件测试决策"。四个原因：

1. 按 PUT × 缺陷类 × 证书等级的**变异体级**随机划分：同一 Fault Card、模板、相似补丁可同时进 dev/holdout；"未见过的变异体"≠"未见过的缺陷机理"。
2. Primary 只要求 S1 > 随机 S4；经典 MS 与 MR coverage 是 secondary。随机是弱基线。
3. 功效按 120–150 个 holdout 变异体估计，但真正独立单位接近 PUT 和 Fault Card family。
4. "同预算"只计 MR 条数，未计构造/执行/维护成本；确认性结论只能是"冻结目录内的 MR portfolio selection"。

## 四、执行预注册前必须修改的五点

1. holdout 改成**分组隔离**：按 Fault Card family / 变异模板 / 历史缺陷家族整体划分；最好增加 leave-PUT-out 或 new-PUT holdout。
2. 将 S1 对经典 MS 或 MR coverage 中的**最强基线纳入确认性主比较**；随机只作 sanity-check。
3. 按 PUT 和 fault family **两级依赖**重做功效模拟；PUT 少时用小样本友好的置换/随机化推断。
4. **扩大独立有效性审计**：分层抽审 A/B/C、拒绝、未确定、LLM 生成失败、多效应对象；验证证书执行正确性与 Fault Card fidelity；不只对 D 级做第二评者。
5. 建立与旧评审逐项对应的 **closure ledger**：每项记录原意见、修改位置、新证据、验收命令、状态、残余限制。

另：将"真实构建 M_Σ(P)"改为"构建冻结的认证样本 M^cert_{Σ,B}(P)"；只能声称相对有限、声明并认证的缺陷域的充分性。

## 五、最终编辑判断

- 正面回应：是。DVE 是正确方向。
- 可否立即预注册执行：不建议；先修 holdout 粒度、primary baseline、独立审计。
- 原样得到显著正结果是否足以稳定接收：未必。
- 完成修正并在新 PUT/历史缺陷上获得一致效果：具备 TOSEM 竞争力。

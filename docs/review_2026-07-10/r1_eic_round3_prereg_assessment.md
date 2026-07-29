# EIC Round-3 Preregistration Assessment

**Review date:** 2026-07-10
**Target venue:** ACM Transactions on Software Engineering and Methodology (TOSEM)
**Reviewed revision:** `research/paper-draft-plan-mr-adequacy-tosem.md`, v1.1
**Reviewed commit:** `6c83f56e`
**Review mode:** Re-review / verification review

## Decision

**Conditional Pass to Preregistration — Minor Methodological Amendments Required**

Round-2 的五项预注册前要求均已实质进入研究设计，而不是仅在回复中宣称完成。方案已经从“高风险重设计”进入“预注册前的最后方法校准”阶段，不需要再次重构研究主线；但在冻结预注册之前，仍须修正置换单位、family 定义与审计时序等问题。

## Revision-response verification

| Round-2 requirement | Verified revision | Status |
|---|---|---|
| family/template 级 holdout，并增加 leave-PUT-out 验证 | 新增 I5、DVE-W family 级隔离和 DVE-T PUT 级保留 | FULLY ADDRESSED |
| 最强基线进入确认性主比较 | S2 classical-MS-guided 和 S3 MR-coverage-guided 成为共同主基线；S4 降为 sanity-check | FULLY ADDRESSED |
| PUT × family 两级依赖推断 | endpoint、功效模型和 bootstrap 已转向两级结构，但 sign-flip 的层级仍需修正 | PARTIALLY ADDRESSED |
| 分层独立有效性审计 | 覆盖 A/B/C、REJECTED、UNCERTAIN、LLM 失败、多效应和 Fault Card fidelity，并规定不达标后果 | FULLY ADDRESSED |
| closure ledger | P0-1 至 P0-6 均记录修改位置、新证据、验收命令、状态和残余限制；没有提前宣称 closed | FULLY ADDRESSED |
| denominator 与主张边界 | 统一为冻结认证样本 $M^{\mathrm{cert}}_{\Sigma,B}(P)$；确认性主张限定为 frozen-catalogue MR portfolio selection | FULLY ADDRESSED |

P0-6 保持 `open` 是正确处理。投稿包、DOI 和 confidential disclosure 等事项不能在实验执行前假装关闭。

## Mandatory amendments before preregistration

### 1. Move sign-flip inference to the PUT level

当前方案拟在 PUT 内对 family 进行 sign-flip。若同一 PUT 内的 family 相关，逐 family 翻转仍将相关观测视为可独立交换，不能构成严格的 cluster randomization test。

建议先为每个 PUT 计算策略差：

$$
d_{p,S}
=
\frac{1}{|G_p|}
\sum_{g\in G_p}
\left[
\operatorname{det}(S1,g)-\operatorname{det}(S,g)
\right],
$$

再将一个 PUT 内的全部 family 作为整体，对 $d_{p,S}$ 做 PUT 级 sign flip。若主实验包含 17 个 PUT，可以枚举 $2^{17}=131{,}072$ 种符号配置，无须依赖渐近正态或 Monte Carlo 近似。

这是当前唯一具有实质统计阻断性质的问题。

### 2. Freeze family boundaries before split commitment

里程碑顺序写作 M1.5 审计后进入 M2 划分，这是正确的；但 §4.1 又规定审计发生于划分承诺之后。若审计改变 family 边界，而 dev/holdout 已经划分，可能导致同一 family 跨侧。

应固定为：

1. 构建 family registry；
2. 第二评者完成 family-boundary 和 fidelity 审计；
3. 冻结 family registry；
4. 才进行 dev/holdout 随机划分与密码学承诺。

family ID 还应明确嵌套于 PUT，例如 `(PUT, mechanism/template cluster)`，以保持

$$
\text{mutant}\subset\text{family}\subset\text{PUT}.
$$

跨 PUT 的相似缺陷应共享 mechanism class，而不是共享同一个 family ID。

### 3. Remove family-size bias from the primary endpoint

当前 family 检测定义为“family 中任一实例被杀死即记为 detected”。实例越多的 family 获得的检测机会越多，因此 primary endpoint 可能受 family size 驱动。

预注册前应冻结以下一种处理：

1. 每个 family 预先随机冻结一个 sentinel mutant；
2. 使用 family 内实例检测比例，再对 family 等权平均；
3. 保留 any-instance 定义，但统一或截断每个 family 的实例数，并预注册 family-size sensitivity。

从统计稳健性看，family 内比例后再按 family 等权平均最稳妥；若理论目标是证明某类机理至少存在一个可观察见证，则 sentinel 方案更干净。

### 4. Correctly label the DVE-T estimand

S1-T 可以读取目标 PUT 的 Fault Card 机理类分布。因此它没有读取目标变异体或 kill 结果，但仍获得了目标缺陷域的分布信息。当前 DVE-T 支持的是：

> target-informed cross-program transfer

而不是完全的 zero-shot transfer。

最小修改是收紧措辞，将其称为 `target-informed leave-PUT-out transfer`。更强的可选设计是同时报告：

- S1-T0：不读取目标 Fault Card 分布；
- S1-T+：读取目标机理类分布，即当前设计。

DVE-T 是 secondary endpoint，因此收紧措辞即可通过预注册门槛，无须强制增加实验臂。

## Operational clarifications

预注册还应明确以下事项：

1. “40–60 条候选 MR”究竟是每个 PUT 还是全部 PUT 的总量；该口径直接影响 $k^*=4$ 的可行性和策略空间。
2. 原程序 false-positive 的 MR 应从选择空间删除，而不是仅设置为不能产生 kill。建议定义

   $$
   R_{\mathrm{valid}}
   =
   \{r\in R_{\mathrm{cand}}:\operatorname{AVP}(P,r)=\mathrm{pass}\},
   $$

   四个策略统一从 $R_{\mathrm{valid}}\setminus R_0$ 中选择。
3. 若 MID=10pp 表示实际重要差异，应区分统计优势 $H_0:\Delta\le0$ 与实际重要优势 $H_0:\Delta\le\mathrm{MID}$。不能仅凭点估计超过 MID 且相对零显著，就宣称效果超过 MID。
4. “仅胜一个共同主基线”应称为 baseline-specific superiority；整体 conjunctive H-DV 应记为未完全确认，而不是模糊地称为主假设部分成立。

## Editorial rationale

v1.1 已经形成清晰、可审计的主证据链：

$$
\text{independent certified fault domain}
\rightarrow
\text{dev residual signal}
\rightarrow
\text{frozen MR portfolio}
\rightarrow
\text{family-level holdout}
\rightarrow
\text{decision gain over strong baselines}.
$$

完成上述小修后，可以冻结预注册。此后除功效模拟决定样本规模外，不应再修改 primary endpoint、family 定义、策略算法、基线层级或结论判定规则。


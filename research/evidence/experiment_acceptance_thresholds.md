# 实验接收门槛备忘录

日期：2026-07-03

## 结论

“每个元模式至少 1-2 个真实缺陷”可以作为强目标，但不应作为最低门槛。更稳妥的实验标准是：每个元模式都有可重复、可量化的 mutation/fault-based 证据；核心元模式最好有真实缺陷或真实历史缺陷支撑；总体上需要一批真实缺陷来证明外部有效性。

## 稳定支撑中等水平目标期刊的建议门槛

1. 每个元模式都必须有系统性定量证据。
   - 至少覆盖若干真实程序、若干 MR 实例、若干语义变异体或人工构造缺陷。
   - 证据要能说明该元模式不是孤立示例，而是可复现的检测机制。

2. 真实缺陷不必均匀分布到每个元模式。
   - 较稳的总体目标是 8-15 个真实缺陷或真实历史缺陷。
   - 若能达到 10 个以上 confirmed real faults，外部有效性会明显增强。

3. 核心元模式最好每类有 1-2 个真实缺陷案例。
   - 如果论文把某些元模式作为主要贡献或主要检测机制，这些模式最好有真实缺陷或历史缺陷案例。
   - 边缘模式可以用真实历史缺陷、手工注入缺陷、语义变异体、benchmark faults 补足证据。

4. 每个元模式都要有 mutation/fault-based 覆盖。
   - 至少报告该元模式能杀死哪些相关语义变异体，或覆盖哪些明确 fault classes。
   - 不能只给定义、示例或个别成功案例。

5. 必须有 baseline 和 ablation。
   - 与普通 MR 设计比较。
   - 与随机或经验式 MR 比较。
   - 报告去掉某类元模式后的效果变化。
   - 若涉及 LLM 或自动生成，还应比较人工、模板或检索式方案。

6. 结果要支撑“有效”，而不仅是“可行”。
   - 报告 fault detection rate 或 mutant kill rate。
   - 报告每个元模式的贡献。
   - 报告 overlap 与 unique kills。
   - 报告 false positives 或无效 MR 比例。
   - 报告 MR 设计与执行成本。
   - 至少提供置信区间、效应量或显著性检验，避免只报告均值。

## 分级目标

| 等级 | 建议标准 | 可支撑的论文措辞 |
| --- | --- | --- |
| 底线 | 每个元模式有 mutation evidence；总体有 5-8 个真实或历史缺陷 | 可行性、初步有效性、受限外部有效性 |
| 稳妥 | 总体有 8-15 个真实或历史缺陷；核心元模式各 1-2 个；所有元模式有变异体证据和 ablation | 方法有效、证据较完整、适合中等目标期刊 |
| 强支撑 | 每个主要元模式都有真实缺陷案例；20 个以上真实或历史缺陷；跨多个项目或领域复现 | 较强外部有效性、可冲更高层级期刊 |

## 写作原则

真实缺陷用于证明外部有效性；语义变异体、历史缺陷和 benchmark faults 用于保证每个元模式都有可重复、可解释、可量化的检测证据。

因此，论文中不宜声称“每个元模式都已通过真实缺陷充分验证”，除非确实达到每类 1-2 个真实缺陷。更稳妥的表述是：

> We use real and historical faults to evaluate external validity, and use semantic mutants and benchmark faults to ensure that each metapattern has reproducible and interpretable fault-detection evidence.

## 当前实验设计的行动建议

1. 先确保每个元模式都有稳定的语义变异体证据。
2. 将真实缺陷优先匹配到核心元模式，而不是平均摊派到所有元模式。
3. 为没有真实缺陷的元模式准备历史缺陷、benchmark faults 或高质量人工注入缺陷。
4. 结果表中同时呈现 per-metapattern evidence、unique kills、overlap、cost 和 false-positive 控制。
5. 在摘要和贡献中只使用 evidence ledger 能支撑的措辞；不足部分放入 limitations 或 future work。

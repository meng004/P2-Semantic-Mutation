# 理论增强-phaseT3-fable：THM-WIN 检测窗（现稿 Prop 2 原位升级）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪。
> **执行模型:** `claude-fable-5-thinking-max`（分派类别：**最强推理**——误差预算/不等式型证明起草；记号与假设表述的独立交叉检验由 T6 审计阶段（terra，跨家族）承担）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`。开工前必读其 §0（符号闭集——特别注意：Lipschitz 常数写 \(L_r\) 不写 \(L\)，标准差写 \(\sigma_{\mathrm{out}}\) 不写裸 \(\sigma\)，残差写 \(\Delta_r\) 不写 \(\rho_0\)）与 §1.1/§1.2（本阶段负责 THM-WIN、REM-FPOS、REM-FNEG——R-9 后两条为 THM-WIN 内 Remark；关闭 PO-WIN-1–6）。内容冲突以 master 为准。

**前置门禁:** Phase T0 完成（notation_registry 已 commit）。

**并行性:** 可与 T1/T2/T5（均 fable）并行。本阶段完成是论证提升计划 Task 3.3（冻结预测）的前置之一。

**交接物:** `research/theory_drafts/thm_window.md`（状态 → internal-review）→ 供 T4（REM-IDF 引用假设）、T6 整合、论证线 EXP-DOSE 预测与 Task 3.3 冻结预测使用；Lipschitz 常数 \(L_r\) 不可估的 PUT 清单 → 同步论证线 Task 2.3 替换对象。

---

## Task T3.1：现有 Prop 2 资产盘点

- [x] **Step 1:** 摘录 Prop 2 全文（main.tex:908–934）、strong/weak/strong boundary 定义（884–906）与 latency window（817–822）进草稿 §1，附五条非形式假设清单
- [x] **Step 2:** 在 `research/theory_drafts/thm_window.md` 列假设清单：观测泛函对 \(\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})\) 的 Lipschitz 性（常数 \(L_r\)，仅承载剂量反应转移、不承载 (i)–(iii)）、噪声界 \(\bar\eta\)（确定性=舍入；随机=\(c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}}\)）、checker 阈值形式（严格超出约定，对照 `mp1_conservation.py` 的 `≤ε⇒pass` 核实）

## Task T3.2：起草定理与推论

**Files:** Create: `research/theory_drafts/thm_window.md`

- [x] **Step 1:** 写入（定稿基准，`[·]` 占位符在 Task T6.1 换成正文编号）；另加 scope note：\(2\bar\eta\) 覆盖成对执行关系，MP_3 收敛阶关系每判定执行 p=4 网格（`src/p2/avp/dispatcher.py:15-16`），一般形式 \(p\bar\eta\)（陈述冻结不动，泛化入 scope note，CHECKPOINT T3 问题 2）：

```latex
\textbf{Theorem [THM-WIN] (tolerance-indexed detection window).} Let $m_{\mathrm{mut}}$ carry
violation magnitude $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$ at stratum $\psi$, let $r$ be an exact
checker with tolerance $\varepsilon_{\mathrm{tol}}$, let
$\Delta_r:=\sup_{x\in D_r}\varepsilon_r(x;P^\star)$ be the correct-program
structure-preservation residual (the instantiation of $\Delta(S,P)$ from the
MR-validity theory on the structure inducing $r$; here $P^\star$ is the
cell's original program, assumed correct per S2), and $|\eta|\le\bar\eta$
the execution noise, with the violation functional $L_r$-Lipschitz in
$\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})$. Assume the additive
residual budget H-a, the non-degenerate-margin regime R1, and, for (i),
magnitude realization H-d (Appendix hypotheses). Then
(i) $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})>\varepsilon_{\mathrm{tol}}+\Delta_r+2\bar\eta$ implies
$r$ kills $m_{\mathrm{mut}}$; (ii) $\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})<\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta$
implies $r$ does not kill $m_{\mathrm{mut}}$; (iii) with the crash threshold
$\varepsilon_{\mathrm{crash}}$ (S4), the kill region lies within
$(\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta,\ \varepsilon_{\mathrm{crash}})$.

\textbf{Remark [REM-FPOS] (weak-MR false positive).} If
$\mu_r=\varepsilon_{\mathrm{tol}}-\Delta_r<0$, inputs with correct-program
residual above $\varepsilon_{\mathrm{tol}}$ exist ($\Delta_r$ is a
supremum) and the correct program is flagged whenever validation executes
an input whose residual exceeds $\varepsilon_{\mathrm{tol}}+2\bar\eta$
(such inputs are guaranteed to exist when $\mu_r<-2\bar\eta$; in the band
up to $2\bar\eta$ noise can mask the flag), and
$r$ exits the admissible evaluation set (empirically: the PINN case).

\textbf{Remark [REM-FNEG] (stochastic false negative and repeat prescription).}
For stochastic PUTs $\bar\eta=c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}}$;
guaranteed detection at target magnitude $\varepsilon^\dagger$ requires
$N\ge\bigl(2c\sigma_{\mathrm{out}}/(\varepsilon^\dagger-\varepsilon_{\mathrm{tol}}-\Delta_r-2\eta_{\mathrm{det}})\bigr)^2$
(empirically: the RNG case).
```

（R-9：两条原拟推论改为 THM-WIN 定理环境内的 Remark，不占独立定理编号；其论证义务 PO-WIN-5/6 保留。）

- [x] **Step 2:** 写证明（误差预算三角不等式两次=H-a；对接 §2.9 latency window 定义，(iii) 由 S4 直接）；PO-WIN-1–6 全闭合；非退化边际域 \(\mu_r>2\bar\eta\) 独立成节（§4）供 LEM-WIT/THM-GAP 引用解析
- [x] **Step 3:** 写"经验预测"小节：kill 概率沿 \(\varepsilon_{\mathrm{viol}}(m_{\mathrm{mut}})\) 单调、转变区宽 \(O(\Delta_r+\bar\eta)\)、中心 \(\approx\varepsilon_{\mathrm{tol}}\)（含 H-DOSE-CTR 中心包含预测 \(\varepsilon_{\mathrm{tol}}\pm(\Delta_r+2\bar\eta)\)）—— 论证提升计划剂量反应实验 EXP-DOSE（H-DOSE）的预测来源；现有 boundary cases（PINN、RNG）改述为 REM-FPOS/REM-FNEG 实例（RNG=PO-WIN-6 侧条件失败实例）
- [x] **Step 4:** 写"结构命运对应"注记（≤1 段）：以 \(\mu_r\) 与 \(\Delta_r\) 把 P3 的 MR 分类形式对接 v3.1 §4.2 结构命运四分类——\(\Delta_r=0\) ↔ 精确保持（strict MR）、\(0<\Delta_r\le\varepsilon_{\mathrm{tol}}\) ↔ 近似保持（strong/tolerance MR）、\(\Delta_r>\varepsilon_{\mathrm{tol}}\) ↔ 结构破坏（weak MR，即 REM-FPOS）、\(\Delta_r(h)\to0\) ↔ 渐近保持；注明这使 THM-WIN 成为 v3.1 引理 1（\(\Delta\le\tau\Rightarrow\mathrm{Valid}\)）在变异检测语境下的定量细化
- [x] **Step 5:** 逐 PUT 类评估 \(L_r\) 可估性（12 核逐一入表），产出"不可估 PUT 清单"：**C3（shallow-NN）、D1（MLP）、D2（SVM）不可估；C1（GPR）条件可估（须冻结核超参，或 Task 2.3 换 PCE）**；供论证线 Task 2.3 替换剂量反应对象；Commit

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| \(L_r\) 在个别 PUT 不可估 | 该 PUT 退出剂量反应实验对象清单（Step 5 输出，论证提升计划 Phase 2 联动更新） |
| 跨阶段草稿记号风格漂移 | 严格以 master §0.2 总表为闭集；T6.1 整合时统一润色并由 terra 审计核对 |

> **CHECKPOINT T3 = PASS（2026-07-28，与 T4 联合拍板）**：见 `理论增强-phaseT4-fable.md` 检查点记录与 `docs/review_20260728/checkpoint_t3_record.md`（修复 B2/B3，L_r 不可估清单 C3/D1/D2 + C1 条件可估移交论证线 Task 2.3）。

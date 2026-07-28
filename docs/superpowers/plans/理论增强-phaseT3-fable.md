# 理论增强-phaseT3-fable：THM-WIN 检测窗（现稿 Prop 2 原位升级）

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans。任务用 checkbox 跟踪。
> **执行模型:** `claude-fable-5-thinking-max`（分派类别：**最强推理**——误差预算/不等式型证明起草；记号与假设表述的独立交叉检验由 T6 审计阶段（terra，跨家族）承担）。非此模型请勿执行本文件。

**Master plan（规格权威）:** `docs/superpowers/plans/2026-07-28-p3-theory-enhancement.md`。开工前必读其 §0（符号闭集——特别注意：Lipschitz 常数写 \(L_r\) 不写 \(L\)，标准差写 \(\sigma_{\mathrm{out}}\) 不写裸 \(\sigma\)，残差写 \(\Delta_r\) 不写 \(\rho_0\)）与 §1.1/§1.2（本阶段负责 THM-WIN、REM-FPOS、REM-FNEG——R-9 后两条为 THM-WIN 内 Remark；关闭 PO-WIN-1–6）。内容冲突以 master 为准。

**前置门禁:** Phase T0 完成（notation_registry 已 commit）。

**并行性:** 可与 T1/T2/T5（均 fable）并行。本阶段完成是论证提升计划 Task 3.3（冻结预测）的前置之一。

**交接物:** `research/theory_drafts/thm_window.md`（状态 → internal-review）→ 供 T4（REM-IDF 引用假设）、T6 整合、论证线 EXP-DOSE 预测与 Task 3.3 冻结预测使用；Lipschitz 常数 \(L_r\) 不可估的 PUT 清单 → 同步论证线 Task 2.3 替换对象。

---

## Task T3.1：现有 Prop 2 资产盘点

- [ ] **Step 1:** `rg -n "Proposition 2|strong boundary|varepsilon_\{?\\\\mathrm\{tol\}" submission/TOSEM_regular_20260706/main.tex`，摘录 Prop 2 全文与其非形式假设进草稿
- [ ] **Step 2:** 在 `research/theory_drafts/thm_window.md` 列假设清单：观测泛函对 ε_m 的 Lipschitz 性（常数 \(L_r\)）、噪声界 \(\bar\eta\)（确定性=舍入；随机=\(c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}}\)）、checker 阈值形式

## Task T3.2：起草定理与推论

**Files:** Create: `research/theory_drafts/thm_window.md`

- [ ] **Step 1:** 写入（定稿基准，`[·]` 占位符在 Task T6.1 换成正文编号）：

```latex
\textbf{Theorem [THM-WIN] (tolerance-indexed detection window).} Let $m$ carry
violation magnitude $\varepsilon_m$ at stratum $\psi$, let $r$ be an exact
checker with tolerance $\varepsilon_{\mathrm{tol}}$, let
$\Delta_r:=\sup_{x\in D_r}\varepsilon_r(x;P^\star)$ be the correct-program
structure-preservation residual (the instantiation of $\Delta(S,P)$ from the
MR-validity theory on the structure inducing $r$), and $|\eta|\le\bar\eta$
the execution noise, with the violation functional $L_r$-Lipschitz in
$\varepsilon_m$. Then
(i) $\varepsilon_m>\varepsilon_{\mathrm{tol}}+\Delta_r+2\bar\eta$ implies
$r$ kills $m$; (ii) $\varepsilon_m<\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta$
implies $r$ does not kill $m$; (iii) with the crash threshold
$\varepsilon_{\mathrm{crash}}$ (S4), the kill region lies within
$(\varepsilon_{\mathrm{tol}}-\Delta_r-2\bar\eta,\ \varepsilon_{\mathrm{crash}})$.

\textbf{Remark [REM-FPOS] (weak-MR false positive).} If
$\mu_r=\varepsilon_{\mathrm{tol}}-\Delta_r<0$ the correct program is flagged
and $r$ exits the admissible evaluation set (empirically: the PINN case).

\textbf{Remark [REM-FNEG] (stochastic false negative and repeat prescription).}
For stochastic PUTs $\bar\eta=c\sigma_{\mathrm{out}}/\sqrt N+\eta_{\mathrm{det}}$;
guaranteed detection at target magnitude $\varepsilon^\dagger$ requires
$N\ge\bigl(2c\sigma_{\mathrm{out}}/(\varepsilon^\dagger-\varepsilon_{\mathrm{tol}}-\Delta_r-2\eta_{\mathrm{det}})\bigr)^2$
(empirically: the RNG case).
```

（R-9：两条原拟推论改为 THM-WIN 定理环境内的 Remark，不占独立定理编号；其论证义务 PO-WIN-5/6 保留。）

- [ ] **Step 2:** 写证明（误差预算三角不等式两次；对接 §2.9 latency window 定义，(iii) 由 S4 直接）
- [ ] **Step 3:** 写"经验预测"小节：kill 概率沿 ε_m 单调、转变区宽 \(O(\Delta_r+\bar\eta)\)、中心 \(\approx\varepsilon_{\mathrm{tol}}\) —— 论证提升计划剂量反应实验 EXP-DOSE（H-DOSE）的预测来源；现有 boundary cases（PINN、RNG）改述为推论实例
- [ ] **Step 4:** 写"结构命运对应"注记（≤1 段）：以 \(\mu_r\) 与 \(\Delta_r\) 把 P3 的 MR 分类形式对接 v3.1 §4.2 结构命运四分类——\(\Delta_r=0\) ↔ 精确保持（strict MR）、\(0<\Delta_r\le\varepsilon_{\mathrm{tol}}\) ↔ 近似保持（strong/tolerance MR）、\(\Delta_r>\varepsilon_{\mathrm{tol}}\) ↔ 结构破坏（weak MR，即 REM-FPOS）、\(\Delta_r(h)\to0\) ↔ 渐近保持；注明这使 THM-WIN 成为 v3.1 引理 1（\(\Delta\le\tau\Rightarrow\mathrm{Valid}\)）在变异检测语境下的定量细化
- [ ] **Step 5:** 逐 PUT 类评估 \(L_r\) 可估性，产出"不可估 PUT 清单"（供论证线 Task 2.3 替换剂量反应对象）；Commit

---

## 本阶段风险

| 风险 | 处置 |
|---|---|
| \(L_r\) 在个别 PUT 不可估 | 该 PUT 退出剂量反应实验对象清单（Step 5 输出，论证提升计划 Phase 2 联动更新） |
| 跨阶段草稿记号风格漂移 | 严格以 master §0.2 总表为闭集；T6.1 整合时统一润色并由 terra 审计核对 |

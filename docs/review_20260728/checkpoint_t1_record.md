# REVIEW CHECKPOINT T1 — 拍板记录（委托执行）

- 日期：2026-07-28
- 评审对象：`research/theory_drafts/thm_interval.md`（LEM-WIT + THM-INT，PO-INT-1–5）、
  `scripts/theory/interval_demo.py`、`data/results/interval_demo_v4.json`
- 评审身份：作者委托的检查点评审（用户指令"请执行 review checkpoint T1"）；
  评审线独立重做了全部代数验算与假设-证明对齐检查
- 复核输入：master plan §0.2/§0.3/§1.1/§1.2、`notation_registry.md`、
  `submission/TOSEM_regular_20260706/main.tex`（§2.3 判等与 kill 谓词）、
  `src/p2/equiv/judge.py`、`src/p2/pipeline/run_cell.py`、`src/p2/avp/repeat.py`、
  `data/results/sms_track2_v4.json`、`data/results/equiv_diagnosis.json`

## 1. 验算结论（Devil's Advocate 线）

代数全部复核通过：区间夹逼与两端可达（PO-INT-3）、宽度恒等式
\(ku/(n(n+u))=\mathrm{SMS}_{\mathrm{strict}}\cdot u/(n+u)\)（PO-INT-4）、
四类证据运动的端点方向（PO-INT-5，含 mediant 不等式 \((k+j)/(n+j)\ge k/n\)
当 \(k\le n\)）。演示脚本与台账一致性（inst=equiv+killed+survive、与旧 SMS
四位舍入一致）通过；60 cells、pooled [0.104795, 0.104795]、宽度全 0 与
`equiv_diagnosis.json` 的 equiv=0 真实观测相符。

## 2. 发现与处置（两项修订，均为效度修复）

### A1（blocker，已修）：LEM-WIT 陈述-证明假设错位

原基准陈述只含"AVP 判定是观测输出的确定函数"，但结论要求存在
\(>\varepsilon_{\mathrm{eq}}\) 的分歧见证。裸决定性只能推出"观测输出不同"，
推不出超容差分歧。反例：关系残差在 \(P\) 上为 \(\tau-\delta_1\)（pass）、在
\(P'\) 上为 \(\tau+\delta_2\)（fail），\(\delta_1+\delta_2\) 任意小时，逐点输出
分歧可 \(<\varepsilon_{\mathrm{eq}}\)，即被杀但无 DEF-01 见证。证明实际使用了
margin 稳定性条款（判定在 \(\le\varepsilon_{\mathrm{eq}}\) 逐点扰动下不变），
该条款必须入陈述。处置：条款升入 LEM-WIT 假设（接 DEF-13 / THM-WIN(iii)
非退化域，与 THM-GAP(iii) 既有前提架构一致），master → 拆分文件 → 草稿三处
同步，并在草稿 §3 记录反例证明条款不可删。

### A2（precision，已修）：THM-INT 的 R⊆R′ 句缺分类冻结限定

E1 的量化域是"\(\forall mr\in\) cell 的 MR 族"；若三态分类随 \(R'\) 重算，
新关系上可出现"判定不同但非 kill 方向"（\(P\) fail、\(P'\) pass）的仅见证
事件——即 case-2 运动 \((n{+}1,k,u{-}1)\)，使 strict 端点下降，与
"两端点非降"矛盾。处置：R⊆R′ 句加"三态分类冻结（prescreen-once，对 cell
关系全域一次计算）"限定；该限定与实证协议（POOL-SEM 一次 prescreen、
kill 矩阵按条件评估）一致。草稿 case 4 补不可删性论证，另加
"\(\mathrm{SMS}_{\mathrm{cons}}\) 在全部四类运动下单调非降"备注。

## 3. Reviewer 2 视角的最严苛审稿意见

- （已修复，本轮内关闭）A1：陈述弱于证明所需假设——若带入正文将构成可被
  审稿人一击的健全性缺口；修复后陈述-证明对齐。
- （已修复，本轮内关闭）A2：R⊆R′ 单调句在可执行语义下不成立（E1 域随 R
  增长）；修复后限定与实证协议一致。
- 其余扫描：方法论（演示脚本决定性、SHA256 溯源、完整性断言）通过；外部
  效度（development-only 标注、无泛化主张、F-8 防火墙）通过；统计选择偏差
  （u 规则先于结果由管线语义确定、60 cells 全报含全零宽度）通过；
  benchmark 公正、霍桑效应不适用。
- 修复后无 publication blocker：Reviewer 2 视角扫描通过——5 类维度均无
  publication blocker。

## 4. 过度防御审计（CLAUDE.md §10.1）

| 处置 | 类别 | 辩护 |
|---|---|---|
| A1 margin 条款入假设 | 效度修复 | 无条款则引理为假（§2 反例）；非规避证伪 |
| A2 分类冻结限定 | 效度修复 | 无限定则命题在可执行语义下为假；限定即实证协议 |
| F1 随机 PUT 聚合读法 | 效度修复 | 单次运行逐点见证对随机程序本就不真；聚合读法为 DEF-03 括注既定语义 |
| 演示区间全退化如实报告 | 诚实报告 | 未隐藏、未合成假宽度；零回溯差异本身是向后兼容证据 |

无主张收缩项；无需回调。

## 5. 门禁判定

**CHECKPOINT T1 = PASS（附修订 A1/A2，已在 master/拆分/草稿三处落地）。**

- T1 交接物齐备：`thm_interval.md`（internal-review，含修订）、
  `data/results/interval_demo_v4.json`（development-only）、本记录。
- 下游解锁：T2/T3/T5 可启动（并行，fable 线）；T4 待 T2；T6 待 T1–T5 与
  CHECKPOINT T1–T3。预注册冻结门禁仍唯一系于 CHECKPOINT T2（R-5）。
- 遗留移交（非阻塞）：论证计划 RQ1 辅指标"区间宽度 vs 证书预算曲线"需要
  非零 \(u\) 的数据源；v4 演示为退化点，曲线素材应由 v5 管线（或合成敏感性
  扫描，需另行标注）在写作阶段提供——移交 T6.1/论证线 Phase 4。
- 作者保留最终否决权：若对 A1/A2 的表述另有偏好，按"先改 master 再同步"
  程序修订。

# 命名规范 + 旧→新映射表(SSOT,用户 2026-07-08 确认)

> 背景:本文以语义变异体度量 MR 充分性。命名 = 第一级元模式缩写 + 第二级任务缩写。
> 决策:MR 元模式术语、缩写、定义以 NOETHER 论文的 MetaPattern / operator-block 描述为准；不再把 CE/OS/HP/TF/SI 作为论文中的 MR 元模式或语义变异算子名称。既有 `CE1/OS1/HP1/TF1/SI1` 仅作为历史内部 fault-campaign ID 保留。

## 1. NOETHER 对齐词汇表

- **MR 元模式 / MetaPattern (MP)**:NOETHER 中由某个 operator block 的 invariant 经 Translate 推导得到的 MR 等价类；不是代码补丁类别。
- **Operator block**:MR 元模式的结构来源。NOETHER 的核心块包括 `G` symmetry, `O_le` order, `T_adj` self-adjoint, `T_rev` time reversal, `L_lim` limit, `D_dyn` qualitative dynamics, `E_cmp` method comparison, `B_rel` relational equivalence。
- **本文主用五个 MR 元模式轴**:`inv` `mono` `conv` `dyn` `cmp`。
- **NOETHER 扩展元模式槽**:`adj` `rev` `rel`。当前 12-PUT 主实验未把它们作为 60-cell 主轴，但相关新臂和理论讨论应直接使用这些缩写。
- **MR 族(L2)**:inv.con/inv.eqv · mono.shape/mono.stat · conv.lim/conv.rate/conv.repr · dyn.shape/dyn.traj · cmp.err/cmp.order · adj.self/adj.dual · rev.time · rel.rewrite
- **任务缩写**:`PUT`(被测程序)·`MR`(蜕变关系)·`FC`(故障类型)·`PC`(实验过程控制)
- **顺序号**:第三段 `_1 _2 …`

## 1.1 MR 元模式定义

| 缩写 | NOETHER 对齐名称 | Operator block | 本文定义 |
|---|---|---|---|
| `inv` | invariance / equivariance | `G` symmetry group | 输入经对称、守恒或等变变换后，输出满足同构、守恒量或等变关系；conservation 是 `G` block 的一个实例，不是独立第九块。 |
| `mono` | monotonicity / order | `O_le` order | 参数、输入或统计量按偏序变化时，输出保持单调、反单调、线性或次序一致关系。 |
| `conv` | convergence / limit | `L_lim` limit | 网格、步长、样本量、迭代次数或渐近参数趋向极限时，输出误差、残差或近似值按预期收敛。 |
| `dyn` | qualitative dynamics | `D_dyn` qualitative dynamics | 轨迹形状、极值、过冲、相位、单峰/饱和等定性动力学结构在允许扰动下保持。注意：普通“trajectory”在 NOETHER 中通常归入 `dyn`；只有时间反演对称才归入 `rev`。 |
| `cmp` | method comparison | `E_cmp` method comparison | 两种数值/算法方法存在精度、误差界或 no-worse-than 偏序时，输出满足方法比较关系。 |
| `adj` | self-adjoint / adjoint reciprocity | `T_adj` self-adjoint | 内积、转置图、互易性或 detailed-balance 结构给出的自伴随/伴随互易 MR。 |
| `rev` | time reversal | `T_rev` time reversal | 底层动力学存在可逆时间子族时，正向与反向执行的输出由固定双射约束。 |
| `rel` | relational equivalence | `B_rel` relational equivalence | 关系代数或幂等半环中的等价重写在所有有效输入上下文下保持相同求值。 |

## 2. 各类命名规则

| 类 | 规则 | 是否挂元模式 |
|---|---|---|
| PUT | **P1**:实例号(a1…d3 保留;新臂续新类号)| 否(PUT 跨元模式)|
| MR | **(ii)**:每 PUT 一文件,函数按 `r_<元模式>_<族>` | 是(函数级)|
| PC | 验证器文件 `<元模式>_PC` | 是 |
| FC | **(F-机制)**:现有机制故障保留历史 id;新臂故障 `<元模式>_<族>_FC_<n>` | 仅新臂 |

## 3. 旧→新映射

### 3.1 MR 函数(每个 a1…d3 文件内;e1/e2 属他文 OOD,**不动**)
| 旧 | 新 | 对应 |
|---|---|---|
| r_mp1/R_mp1 | r_inv_con/R_inv_con | inv.con |
| r_mp2/R_mp2 | r_mono_shape/R_mono_shape | mono.shape |
| r_mp3/R_mp3 | r_conv_rate/R_conv_rate | conv.rate |
| r_mp4/R_mp4 | r_dyn_traj/R_dyn_traj | dyn.traj |
| r_mp5/R_mp5 | r_cmp_order/R_cmp_order | cmp.order |
| r_trivial/R_trivial | (保留)| — |

### 3.2 PC 验证器文件
| 旧 | 新 |
|---|---|
| avp/mp1_conservation.py | avp/inv_PC.py |
| avp/mp2_5_wilcoxon.py | avp/mono_PC.py |
| avp/mp3_convergence.py | avp/conv_PC.py |
| avp/mp4_dtw.py | avp/dyn_PC.py |
| (新增)| avp/adj_PC.py / avp/rev_PC.py / avp/rel_PC.py |

### 3.3 FC(F-机制)
- 现有 37 个机制故障的 `CE1/OS1/HP1/TF1/SI1` 后缀 **仅作为历史内部 ID 保留**，不再在论文中展开为术语、缩写或 MR 元模式定义。
- 新臂故障:`adj_self_FC_1`、`adj_dual_FC_1`、`inv_eqv_FC_1`、`conv_lim_FC_1`、`conv_repr_FC_1`、`dyn_shape_FC_1`、`cmp_order_FC_1`、`rel_rewrite_FC_1` …(边界真实缺陷另记仓库+commit)。

### 3.3-R Rosetta 注:两条术语轴不可混用

迁移时必须区分两条**不同分类轴**,避免把编辑机制当成元模式改名:

- **`CE/OS/HP/TF/SI` = 编辑机制轴(patch-shape 故障实现族 / fault-campaign ID)**。
  它刻画的是故障“怎么改代码实现的”(补丁形状),是 AST-overlap 审计的键;
  与五个 MR 元模式族(`inv/mono/conv/dyn/cmp`)属于**不同分类轴**,二者**不存在
  一一映射**。例如 Hyperparameter(HP)类编辑可同时压中多个元模式,
  Structural Injection(SI)也不对应单一元模式。因此迁移时**禁止**把 CE/OS/HP/TF/SI
  映射改名成元模式缩写;只能(a)把概念性表述改写为不依赖该缩写的措辞,或
  (b)在保留处按 Gate C 加本地披露(“historical internal campaign IDs retained
  for reproducibility only”)。
- **`mut_C/M/G/T/F` = 语义效应轴**,与五个 MR 元模式族**存在一一对应**
  (`C→inv`、`M→mono`、`G→conv`、`T→dyn`、`F→cmp`,依据 supplementary B.2 表)。
  因此**允许整体改名**,已改为 `mut_inv / mut_mono / mut_conv / mut_dyn / mut_cmp`
  (LaTeX 形式 `\mathrm{mut}_{\mathrm{inv}}` 等)。
- **陷阱**:`mut_C/M/G/T/F` 与 `CE/OS/HP/TF/SI` 都出现在旧稿里,但**只有前者**
  可映射改名。把编辑机制轴按语义效应轴处理会制造虚假的一一映射,是投稿硬伤。

### 3.4 PUT
- a1…d3 **保留**。新臂:adjoint/boundary/PINN 程序续新类号(避开 e=OOD)——具体待第三方源/真实缺陷定。

## 4. 冲突 / 冗余检查
- 新名(inv_con、dyn_traj、cmp_order、inv_PC、adj_self_FC_1…)与现有名**无碰撞、无重名**。
- `mp_index`(整数路由键)在 16 文件内嵌:**非"名字",是内部路由**。规范是关于元模式缩写**名称**,不强制改整数键。

## 5. ⚠ 规模与风险 → 建议分级落地

| 应用面 | 规模 | 读者可见? | 风险 | 建议 |
|---|---|---|---|---|
| 手稿术语/图表(强弱MR、元模式名)| 中 | **是** | 低 | **立即应用** |
| 新臂代码(adjoint/boundary/PINN)| 新建 | 间接 | 无 | **直接用新规范** |
| 现有 140 个 MR 函数内部改名 | 大 | **否** | **高**(动 199 测试+mp_index 路由)| **保留现名 + 本表作 Rosetta;可选低优先安全 pass** |
| mp_index 整数键改元模式键 | 16 文件 | 否 | 高 | 保留整数路由,文档注映射 |

**核心判断**:规范真正服务的是**手稿(读者可见)+ 新臂代码**;现有代码内部函数名(r_mp1)读者看不到,强行改 140 处会动到支撑已发布 arXiv 结果的 199 测试与 mp_index 路由,**高风险零读者收益**。

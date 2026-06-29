# 命名规范 + 旧→新映射表(SSOT,用户 2026-06-29 确认)

> 背景:本文以语义变异体度量 MR 充分性。命名 = 第一级元模式缩写 + 第二级任务缩写。
> 决策:PUT=P1｜MR/FC 粒度=(ii)｜FC=(F-机制)。术语见 [[tosem-flagship-terminology]]。

## 1. 词汇表

- **元模式(L1,NOETHER)**:`inv` `mono` `adj` `rev` `conv`
- **MR 族(L2)**:inv.con/inv.eqv · mono.shape/mono.stat · adj.self/adj.dual · rev.traj · conv.lim/conv.rate/conv.repr
- **任务缩写**:`PUT`(被测程序)·`MR`(蜕变关系)·`FC`(故障类型)·`PC`(实验过程控制)
- **顺序号**:第三段 `_1 _2 …`

## 2. 各类命名规则

| 类 | 规则 | 是否挂元模式 |
|---|---|---|
| PUT | **P1**:实例号(a1…d3 保留;新臂续新类号)| 否(PUT 跨元模式)|
| MR | **(ii)**:每 PUT 一文件,函数按 `r_<元模式>_<族>` | 是(函数级)|
| PC | 验证器文件 `<元模式>_PC` | 是 |
| FC | **(F-机制)**:现有机制故障保留 id;新臂对偶故障 `<元模式>_<族>_FC_<n>` | 仅新臂 |

## 3. 旧→新映射

### 3.1 MR 函数(每个 a1…d3 文件内;e1/e2 属他文 OOD,**不动**)
| 旧 | 新 | 对应 |
|---|---|---|
| r_mp1/R_mp1 | r_inv_con/R_inv_con | inv.con |
| r_mp2/R_mp2 | r_mono_shape/R_mono_shape | mono.shape |
| r_mp3/R_mp3 | r_conv_rate/R_conv_rate | conv.rate |
| r_mp4/R_mp4 | r_rev_traj/R_rev_traj | rev.traj |
| r_mp5/R_mp5 | r_mono_stat/R_mono_stat | mono.stat |
| r_trivial/R_trivial | (保留)| — |

### 3.2 PC 验证器文件
| 旧 | 新 |
|---|---|
| avp/mp1_conservation.py | avp/inv_PC.py |
| avp/mp2_5_wilcoxon.py | avp/mono_PC.py |
| avp/mp3_convergence.py | avp/conv_PC.py |
| avp/mp4_dtw.py | avp/rev_PC.py |
| (新增)| avp/adj_PC.py |

### 3.3 FC(F-机制)
- 现有 37 个机制故障:`a1_CE1`…`d3_SI1` **保留不变**。
- 新臂对偶故障:`adj_self_FC_1`、`adj_dual_FC_1`、`inv_eqv_FC_1`、`conv_lim_FC_1`、`conv_repr_FC_1` …(边界真实缺陷另记仓库+commit)。

### 3.4 PUT
- a1…d3 **保留**。新臂:adjoint/boundary/PINN 程序续新类号(避开 e=OOD)——具体待第三方源/真实缺陷定。

## 4. 冲突 / 冗余检查
- 新名(inv_con、inv_PC、adj_self_FC_1…)与现有名**无碰撞、无重名**。
- `mp_index`(整数路由键)在 16 文件内嵌:**非"名字",是内部路由**。规范是关于元模式缩写**名称**,不强制改整数键。

## 5. ⚠ 规模与风险 → 建议分级落地

| 应用面 | 规模 | 读者可见? | 风险 | 建议 |
|---|---|---|---|---|
| 手稿术语/图表(强弱MR、元模式名)| 中 | **是** | 低 | **立即应用** |
| 新臂代码(adjoint/boundary/PINN)| 新建 | 间接 | 无 | **直接用新规范** |
| 现有 140 个 MR 函数内部改名 | 大 | **否** | **高**(动 199 测试+mp_index 路由)| **保留现名 + 本表作 Rosetta;可选低优先安全 pass** |
| mp_index 整数键改元模式键 | 16 文件 | 否 | 高 | 保留整数路由,文档注映射 |

**核心判断**:规范真正服务的是**手稿(读者可见)+ 新臂代码**;现有代码内部函数名(r_mp1)读者看不到,强行改 140 处会动到支撑已发布 arXiv 结果的 199 测试与 mp_index 路由,**高风险零读者收益**。

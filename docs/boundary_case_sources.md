# 边界案例 真实缺陷来源(provenance)— 用户"记录仓库版本号+缺陷说明"指令产物

> 来源:后台缺陷挖掘 agent(2026-06-29),全部经 GitHub tracker/changelog 核实,无杜撰。
> 配对原则:对版 = 修复后版本(第三方库),错版 = 修复前真实缺陷版本。多数为**同仓库 pre/post-fix**,pip 可装。
> 方法学见 [[tosem-flagship-terminology]] 边界错版来源优先级。

## FP(强→弱 MR:正确程序也违反 / 真实缺陷使其违反)

| 机制 | 错版(真实缺陷)| 仓库 + 引用 | pre-fix→post-fix | 许可 | 可恢复 | 置信 |
|---|---|---|---|---|---|---|
| 等变(rotational)| `Rotation.align_vectors()` 反平行向量把真 180° 旋转塌缩为单位阵(零叉积/无穷权重)| scipy/scipy #20660+#20555, PR#20573, `701d8da` | 1.13.0→1.13.1 | BSD-3 | ✅pip | **H** |
| (备) 等变 | `Rotation` 乘法不重新归一 → 四元数漂离单位球(SO(3) 破)| scipy #12314, PR#12317, `37cfd40` | 1.4.1→1.5.0 | BSD-3 | ✅ | H |
| 守恒 | GeoClaw `filpatch.f90` Y 向动量斜率索引错 → AMR 粗细界面守恒一致性破 | clawpack/geoclaw `1626bca`, v5.8.0 release notes | 5.7.1→5.8.0 | BSD-3 | ✅pip | **H** |
| 辛/能量 | IAS15 预测-校正顺序致长期定步长**系统性能量误差偏置**(Hernandez&Holman 2020)| hannorein/rebound changelog v3.13.0 | 3.12.3→3.13.2 | GPL-3 | ✅pip | **H** |
| 自伴/转置 | `_ScaledLinearOperator._adjoint` 返回 `A.H*alpha` 而非 `A.H*conj(alpha)` → 复标量算子伴随虚部符号错,`(αA).adjoint()≠conj(α)·Aᴴ` | scipy #8900, PR#8962, `caea2b1` | 1.1.0→1.2.0 | BSD-3 | ✅pip | **H** |

## FN(弱→强 边界:有错却全族不杀)

| 子型 | 错版(真实缺陷)| 仓库 + 引用 | pre→post | 许可 | 可恢复 | 置信 |
|---|---|---|---|---|---|---|
| tolerance+coincidental | float32 RNG 右移多一位 `(next_uint32()>>9)*(1/8388608f)` → 每个 float32 变量第 24 位恒 0,样本仍像合法 U[0,1) → 逃过均值/范围/分布 MR | numpy/numpy #17478, PR#20314 | 1.21.6→1.22.0 | BSD-3 | ✅pip | **H** |
| 存活非等价(PINN)| `PeriodicBC` 只强制值周期 u(L)=u(R) 不含导数连续 → PINN 收敛到满足残缺约束的"似是而非"场 | lululxvi/deepxde #26 | pre-`derivative_order`→master | LGPL-2.1 | maybe(需 bisect)| M |
| tolerance(PINN/SciML)| 跨损失梯度聚合算错,训练正常、loss 曲线似合理 | NVIDIA/modulus-sym CHANGELOG v1.3.0 | 1.2.0→1.3.0 | Apache-2.0 | maybe | M |

## 推荐主选(每机制一个,均 H 置信 + pip 可恢复)
- 等变 → **scipy align_vectors**(1.13.0→1.13.1)
- 守恒 → **GeoClaw filpatch**(5.7.1→5.8.0)
- 辛 → **REBOUND IAS15**(3.12.3→3.13.2)
- 自伴/伴随 → **scipy `_ScaledLinearOperator._adjoint`**(1.1.0→1.2.0)
- FN → **numpy float32 RNG**(1.21.6→1.22.0)
- PINN(跨范式)→ DeepXDE PeriodicBC / modulus-sym 梯度聚合

## 关键收获
1. **adjoint 臂可整体改用真实第三方缺陷**(scipy `_ScaledLinearOperator._adjoint`)——彻底取代我之前自建的 e_sym/e_adj,既满足"PUT 第三方"又满足"错版真实缺陷"。
2. **跨范式广度天然成立**:scipy(linalg)、numpy(RNG/MC)、GeoClaw(FV/PDE)、REBOUND(N 体辛)、DeepXDE/modulus-sym(PINN/SciML)——正是用户要的广度含 PINN。
3. 每机制对版/错版多为**同仓库 pre/post-fix**,Defects4J 式真实故障对照。

## 待核验 caveats
- scipy EQ3/openmc PR#1974 归属待对 commit 历史(暂不用)。
- REBOUND changelog 无逐条 issue/PR 号(版本标签+论文佐证)。
- FN2/3/4 有 issue/changelog 但无 pin 到具体 patch commit(需 bisect/版本锁)。
- 无真实缺陷的机制(OpenMOC 等变 / FiPy 守恒 / astropy 辛 / pyadjoint 伴随)→ **不需要**,上述主选已覆盖各机制。

---

## 实现结果(2026-06-30,TDD,全绿)

| 案例 | 元模式 | 实现方式 | 版本/出处 | 强MR 判定 | 测试 |
|---|---|---|---|---|---|
| inv.eqv | 等变 FP | **真实版本切换**(uv) | scipy 1.13.0→1.13.1,#20660/PR#20573 | buggy 残差 2.0 杀 / fixed 1e-16 过 | 3 ✓ |
| FN | 盲区/存活变异体 | **真实版本切换**(uv) | numpy 1.21.6→1.22.0,#17478/PR#20314 | 结构 MR 盲(两版均过);判别器 odd_frac 0 vs 0.5 揭示非等价 | 2 ✓ |
| adjoint | 自伴 | 提取-diff(老 scipy arm64 无法装) | scipy #8900/PR#8962 那一行 | 错版杀 / 对版 1e-16 过 | PoC ✓ |
| rev.traj | 辛 | 教科书兜底(真 REBOUND bug 1e-14 太微弱) | leapfrog vs 显式 Euler,Hairer-Lubich-Wanner | 增长率 MR:Euler ratio 1952 杀 / leapfrog 1.0 过 | 2 ✓ |
| inv.con | 守恒 | 教科书兜底(GeoClaw 需 Fortran/Docker) | 守恒 vs 非守恒 Burgers,Hou-LeFloch 1994 | 激波速度:非守恒 -0.002 杀 / 守恒 0.498 过 | 2 ✓ |
| PINN | 跨范式 | **真实最小 PINN**(torch) | soft vs hard BC,DeepXDE #26 精神 | BC 精确性:soft 5e-4 杀(strict)/ hard 0 过;演示 ε_tol 的 FP↔FN 权衡 | 3 ✓ |

**真实版本切换通路成立**(scipy/numpy);老版本无 arm64 wheel(scipy 1.1.0)或真 bug 太微弱(REBOUND)或需重型构建(GeoClaw)的,按你的"无合适真实错版→教科书忠实实现"兜底,均注明出处。PINN 用真实 torch 最小模型。

**ε_tol 全程显式因子**;PINN 案例额外把"灵敏度–特异度(FP↔FN)权衡"做成可运行演示(strict 杀 / loose 漏)。

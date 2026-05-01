# Lean Plan Template — Token-Optimized Variant

> 用法:writing-plans skill 默认产出 700-900 行的"完整代码块"计划,在 token 受限场景下浪费过多。本模板提供精简骨架,适用于 P2 论文项目这类已有 pipeline、新增任务以"调参 + 局部刷新"为主的场景。

---

# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [一句话]

**Architecture:** [2-3 句]

**Tech Stack:** [关键库]

**File map:**
- Modify / Create: 路径(只列受影响的文件)
- Output: data/results/* 或 figures/*

---

## Task N: [组件名]

**Files:** [路径,不重复 file map]

**验收标准(可量化):**
- [ ] 量化条件 1(grep 计数 / wc -l / JSON key 校验等)
- [ ] 量化条件 2

**关键 snippet**(只贴最易出错的核心几行,其余执行时即时生成):

```python
# 5-10 行,只贴算法核心或非显式接口
```

**Run + Commit:**

```bash
PYTHONPATH=src .venv/bin/python scripts/X.py
git add ... && git commit -m "scope: <50 chars>"
```

---

## 与 verbose 模板的差异

| 项 | verbose(skill 默认) | lean(本模板) |
|---|---|---|
| 平均行数 / 任务 | 60-100 | 15-25 |
| 完整代码块 | 每步嵌入 | 只嵌核心 5-10 行 |
| 测试 + 验收 | 分别列出 | 合并为"验收标准" |
| 提交命令 | 多步骤 | 单段 bash |
| 失败分支 | 完整决策树 | "若 X 见 Task Y" |

适用条件(三选一即可):

1. 任务以**已有脚本调参 + 数据重跑 + 论文数字刷新**为主(本项目典型)
2. 执行者(自己 / 同 session 的 subagent)对代码库已熟悉
3. token 预算 < 100K,不允许 verbose 计划占用 30K+

不适用:全新模块开发、跨域重构、外部团队接手。

# P2 实验文档包 — Index

**项目**: When Same-Prompt LLM Source Diversity Doesn't Help — SMS Metamorphic Testing Audit
**最后更新**: 2026-05-02
**作者**: Meng Li (mlemon@usc.edu.cn)

---

## 包内三份文档

| 文档 | 用途 | 篇幅 |
|------|------|------|
| **`EXPERIMENT_DESIGN.md`** | 实验设计完整说明：RQ / 评价指标 / 实验对象 / 实验方法 / 结果 / 多轮迭代 / 优势与局限 | ~6,500 字 |
| **`QUICK_START.md`** | 复现/扩展实验快速指南：5-min cache replay + 重跑流程 + 扩展点 + 排错 + cheatsheet | ~3,000 字 |
| **`DATA_README.md`** | 原始数据文件清单：56 SSOT JSON + 304 mutant pool + 12 cosmic-ray sqlite + 数据→论文段落 reverse lookup | ~4,500 字 |

---

## 阅读顺序建议

| 你是谁？ | 先读 |
|---------|------|
| **审稿人 / 读者** | `EXPERIMENT_DESIGN.md` 全文（理解实验全貌） |
| **想复现 paper 数字的人** | `QUICK_START.md` §1（5-min cache replay） |
| **想扩展实验（加 PUT / 加算子 / 加 LLM）** | `QUICK_START.md` §3（扩展指南） |
| **要查某个具体数字的来源** | `DATA_README.md` §5（数据→论文段落 reverse lookup） |
| **要理解 v3 / v3b / v4 的关系** | `EXPERIMENT_DESIGN.md` §6（多轮迭代） |
| **要做 Zenodo replication 评审** | `replication/REPRODUCIBILITY.md`（项目根目录） |

---

## 配套外部文档

```
项目根/
├── 论文初稿P2_IST.md            # IST 投稿主稿（9.5k 字 + 三层方法骨架）
├── 论文初稿P2_IST_appendix.md   # IST 附录（6.0k 字）
├── 论文初稿P2.md                 # 中文母稿（26k 字）
├── 论文初稿P2_EN.md              # 英文母稿（26k 字）
├── submission/
│   ├── p2_ist_v2.tex / .pdf     # IST elsarticle 投稿包
│   └── cover_letter_v2.md       # IST cover letter
├── replication/
│   ├── README.md                # Zenodo replication package 入口
│   ├── REPRODUCIBILITY.md       # 详细复现 checklist
│   └── replication.zip (2.35 MB, 684 files)
└── docs/
    ├── review_2026-05-{01,02}/  # 5-reviewer review reports + integrity audit
    └── experiment_documentation/  # ← 你在这
```

---

## 一句话总结

- **方法**: SMS（Semantic Mutation Score）+ 三层方法骨架（定义/操作/应用）+ LRCA 三层归因 + E1∧E2 等价判定
- **实验**: 12 PUT × 5 MP × 5 算子 = 60 单元格；v3/v3b/v4 三阶段消融
- **关键数字**: δ = 0.4392（v4，未达 H2 阈值 0.474，stipulated power 49.1%）；AST overlap 5.14%（HP/TF/SI 0/0/0 不可达）；class-c SMS +91.4% (v3b→v4)
- **结论**: 同 prompt 下 **MR-design** 而非 LLM-source diversity 是 aligned-vs-cross 效应量主导杠杆

---

## 反馈 & 问题

- Email: mlemon@usc.edu.cn
- Issues: GitHub repo（URL TBD at acceptance）

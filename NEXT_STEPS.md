# 下一步工作存档

**Last synced:** 2026-05-03
**当前状态:** Submission-ready (round-9)；CLAUDE.md §8/§9 流程已沉淀；GitHub 公开 push 等待用户拍板。

---

## 0. 已完成的整理（参考用，不再重复）

| Commit | 内容 |
|---|---|
| `6ecdc5b` | release-prep: organize for GitHub publication（archive/、新顶层文档、.github/、submission 改 final） |
| `4944b01` | release-prep: scrub real API endpoints to placeholders（`<YOUR_BASE_URL>` / `<YOUR_API_KEY>` 全仓替换；pytest 192/192 通过） |
| `a31458d` | docs(readme): 重构为 motivation / contributions / replication 三段 |
| `e7c67f1` | docs(project): CLAUDE.md §8 Release-Prep + .gitignore 13 项基线 |
| `97ee9c1` | docs(project): CLAUDE.md §9 Post-Paper Archival Policy |

---

## 1. 立即下一步（等用户决策）

### 1.1 渠道选择（user 必须先回答）

下面三个独立选择，用户拍板任意组合：

- [ ] **arXiv preprint**（cs.SE）— 学术可见性 / 接受同行预检
- [ ] **GitHub public repo** — 协作 + Issue + 持续公开
- [ ] **Zenodo archival**（建议 IST 接受后再做）— 强 DOI

**默认推荐组合**：现在做 *arXiv + GitHub*；Zenodo 等 IST 接受后再做。

### 1.2 GitHub 账号申请（user 必须自行做）

> CLAUDE.md §8.4 列明：账号注册 / 邮箱验证 / 密码 / SSH key 不可代办。

| 步骤 | 操作 | 时长 |
|---|---|---|
| (a) 注册 | https://github.com/signup → 邮箱 `mlemon@usc.edu.cn` | 5 min |
| (b) 用户名 | 建议 `meng-li-usc` / `mlemon-usc` / `lemonmeng`；定下来即固化为仓库 URL 的 `<USERNAME>` | 1 min |
| (c) 邮箱验证 | 点 GitHub 发的确认链接 | 1 min |
| (d) 建空仓库 | 名称 `p2-sms-audit`；Public；**不勾选** README / .gitignore / license | 1 min |
| (e) SSH key | 本地 `ssh-keygen -t ed25519 -C "mlemon@usc.edu.cn"` → 复制 `~/.ssh/id_ed25519.pub` → GitHub Settings → SSH keys → 新建 | 5 min |
| (f) 测试连接 | `ssh -T git@github.com` → 应返回 `Hi <USERNAME>!` | 30 s |

完成后告知助手：
- GitHub 用户名（`<USERNAME>`）
- 仓库 URL 是否选 `git@github.com:<USERNAME>/p2-sms-audit.git`（默认）

---

## 2. 用户给出 `<USERNAME>` 后，助手按 §8.3 元流程执行

### 2.1 §8.3.1 — 生成发布审计表

落地：`docs/release_2026-05-03/audit_table.md`
内容：§8.5–§8.8 全部子项展开为 `| 项 | 检查命令 | 期望 | 状态 |` 表

### 2.2 §8.3.2 — 调用 `superpowers:writing-plans`

输出：`docs/superpowers/plans/2026-05-03-github-arxiv-release.md`
阶段划分（≥ 3）：
1. **Pre-push verification**（pytest / SSOT zero-diff / 敏感扫描 / .gitignore 13 项核对 / 新克隆 30-min smoke 模拟）
2. **GitHub initial push**（`git remote add origin` / `git push -u origin main` / tag `v1.0.0-submission` / `git push --tags`）
3. **GitHub Release 创建**（gh CLI；附 `submission/p2_ist_final.pdf` + `cover_letter_final.pdf` + `replication/replication.zip`）
4. **Actions 验证**（确认 sanity.yml workflow 第一次触发 → 全绿）

每阶段间是 review checkpoint，等用户拍板才推进。

### 2.3 §8.3.3 — 调用 `superpowers:executing-plans`

按计划执行，每个 checkpoint 停下。

### 2.4 §8.3.4 — 用审计表逐项验证

全绿 → 1.3 节执行；任一红 → 回 §8.3.2 修订。

### 2.5 完成后助手向用户汇报

- GitHub 仓库公开 URL
- Release v1.0.0-submission URL
- Actions sanity.yml 执行结果链接
- 待替换占位符清单（arXiv ID / Zenodo DOI / paper DOI）

---

## 3. arXiv preprint（如用户确认走 arXiv）

### 3.1 用户必须自行做

| 步骤 | 操作 | 时长 |
|---|---|---|
| (a) arXiv 账号 | https://arxiv.org/user/register；邮箱用 `mlemon@usc.edu.cn` | 5 min |
| (b) 学者认证 | arXiv 要求 institutional email 验证；`@usc.edu.cn` 应可直接通过 | 自动 |
| (c) Endorsement | cs.SE 首投者需要既存作者 endorse；如果第一次投 cs.SE，请联系一位有 cs.SE 论文的同事 | 视情况 |
| (d) 选 Primary | `cs.SE`（Software Engineering）；可加 `cs.LG` secondary | 1 min |

### 3.2 助手代办（用户给 OK 后）

按 §8.5 准备 arXiv tarball：

```bash
# 工作目录：项目根
mkdir -p arxiv_submission
cp submission/p2_ist_final.tex arxiv_submission/main.tex
# elsarticle.cls + 引用的 .bib（如 inline 则跳过）
cp -r submission/texmf/ arxiv_submission/  # 若 .cls 通过 CTAN 自动获取则不带
cp figs/*.png arxiv_submission/    # 平铺，不带嵌套路径
# 修正 .tex 内 \includegraphics 路径为平铺形式
sed -i '' 's|../figs/||g' arxiv_submission/main.tex

# 本地 pdflatex 验证（arXiv 默认编译器是 pdflatex）
cd arxiv_submission && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
# 必须 0 错误 0 warning（除 hbox / overfull 这种装饰性）

# 打 tarball
cd .. && tar czf arxiv_submission.tar.gz -C arxiv_submission .
```

落地：`arxiv_submission.tar.gz`（≤ 50 MB）

ancillary file（可选）：`replication/replication.zip` 一并上传

### 3.3 用户必须自行做（上传）

- 浏览器登入 arXiv → "Submit a new article"
- 上传 `arxiv_submission.tar.gz`
- 填 title / authors / abstract / categories
- 提交，等 arXiv processing（~ 24 h）
- 拿到 arXiv ID（如 `2606.NNNNN`）

### 3.4 拿到 arXiv ID 后助手代办

替换占位符：
- `README.md` line 8: `arXiv:25NN.NNNNN [cs.SE]` → 真实 ID
- `README.md` bibtex `note = ...arxiv.org/abs/PLACEHOLDER` → 真实 URL
- `replication/CITATION.cff` 加 `preferred-citation.identifiers`
- 重 commit + push

---

## 4. Zenodo upload（建议 IST 接受后做）

> 如果现在做：DOI 会先于 paper acceptance 存在，引用会显得"野"。
> IST 接受后做：DOI 与 paper 关联，更标准。

### 4.1 用户必须自行做

| 步骤 | 操作 |
|---|---|
| (a) Zenodo 账号 | https://zenodo.org → ORCID 登录 / 邮箱注册 |
| (b) Sandbox 测试 | 先在 https://sandbox.zenodo.org 上传一遍验证 metadata |

### 4.2 助手代办

- 完善 `replication/.zenodo.json`（creators / orcid / affiliation / keywords）
- 重建 `replication.zip`：`bash replication/build_zip.sh`
- 验证 SHA256 与 `replication/MANIFEST.txt` 一致
- 打 tag：`git tag -a v1.0.0-zenodo -m "Zenodo archive snapshot"`

### 4.3 用户必须自行做（上传 + DOI minting）

- Zenodo 上传 `replication.zip`
- 填 metadata（多数字段 .zenodo.json 已自动填）
- Publish → 拿到 DOI（如 `10.5281/zenodo.NNNNNNN`）

### 4.4 拿到 DOI 后助手代办

替换占位符（参考 `RELEASE_CHECKLIST.md` §B）：
- `README.md`
- `ZENODO.md`
- `DATASET.md` §9
- `论文初稿P2_IST.md` §8 Data Availability
- `submission/p2_ist_final.tex`（重新跑 `scripts/build_ist_submission_v9.sh` 重编 PDF / DOCX）
- `replication/CITATION.cff`

加 Zenodo DOI badge 到 `README.md`：
```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.NNNNNNN.svg)](https://doi.org/10.5281/zenodo.NNNNNNN)
```

---

## 5. IST EVISE 投稿

### 5.1 用户必须自行做

按 `RELEASE_CHECKLIST.md` §D 走：

- 登入 IST EVISE
- 上传 `submission/p2_ist_final.{pdf,tex,docx}`
- 上传 `figs/fig{1,2,3}*.png` 作为 figure files
- 上传 `submission/cover_letter_final.pdf`
- 填 Highlights / Abstract / Keywords / 推荐审稿人 / COI
- Data and Code Availability 段：填 GitHub URL 和（如已有）Zenodo DOI URL
- Submit
- 保存 EVISE confirmation；submission ID 抄到 `docs/STATE.md`

---

## 6. Post-acceptance（接受后 30 天内）

### 6.1 助手监控（每 5 个工作日）

- GitHub Issues 新增 → 每 5 个工作日 triage
- 复现失败类 Issue → 标 `priority/high`，24 h 内回应
- Zenodo 下载 / Altmetric → 手工查（Zenodo 不提供 webhook）

### 6.2 errata 流程（如有）

- 出现 paper 数字 / 表格错误 → 开 `errata-track` Issue
- 修复 → 新 commit
- 打 tag `v1.0.1-errata`
- Zenodo 上 mint **新版本**（不要覆盖旧版本）
- 更新 `CHANGELOG.md`

### 6.3 P3 路标启动

- 工业 Java/C++ port + LRCA 二评者 κ
- n ≥ 30 PUTs（应对 H2 underpowered）
- 形式理论：minimal MR-subset 存在 + 三柱耦合（targeted TOSEM）
- 单独仓库 `p3-industrial-mt`，不混进 P2

---

## 7. 阻塞 / 待澄清事项

| 阻塞项 | 等待方 | 说明 |
|---|---|---|
| GitHub 用户名 | user | 影响 §2、§3、§4 所有 push / URL 替换 |
| arXiv endorsement | user | 首投 cs.SE 需 endorser；如已有 cs.SE 发表跳过 |
| 论文 LICENSE 决策 | user | 当前 `LICENSE` 仅覆盖 code (MIT)；论文 / 数据用 CC-BY-4.0 是默认建议，需用户确认 |
| `requirements-frozen.txt` 是否完整 | assistant | 当前文件 199 B，疑过简；§9 验收前需 audit |
| `.venv/` 重建 | user / assistant | 当前 venv shebang 指向旧路径 `MT完备性`，需 `python3.12 -m venv .venv --upgrade-deps` 重建（不影响 GitHub push，但本地 dev 受阻） |

---

## 8. 文件指针

- 详细自检清单：`RELEASE_CHECKLIST.md`
- 项目级规则：`CLAUDE.md` §8 + §9
- 当前会话状态：`docs/STATE.md`
- 发布前 sanity 日志：`docs/release_2026-05-03/sanity_check.log`

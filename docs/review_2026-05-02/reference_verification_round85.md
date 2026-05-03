# Reference Verification Audit — P2 IST Submission (Round 85)

**Paper:** "A semantic mutation metric for metamorphic relation adequacy in scientific computing programs"
**Source file:** `论文初稿P2_IST.md` (lines 634-702)
**Verification date:** 2026-05-03
**Method:** Crossref DOI lookup (primary), Google Scholar / Crossref title search (fallback), GitHub WebFetch (software repos)

## Audit Table

| # | Citation key | Status | Notes |
|---|---|---|---|
| 1 | DeMillo, Lipton & Sayward 1978 | ✓ verified | Crossref: title, authors, *Computer* 11(4):34-41, 1978-04. DOI 10.1109/C-M.1978.218136 matches exactly. |
| 2 | Jia & Harman 2011 | ✓ verified | Crossref: *IEEE TSE* 37(5):649-678, 2011-09. DOI 10.1109/TSE.2010.62 matches. |
| 3 | Jia & Harman 2008 (SCAM) | ✓ verified | Crossref: *2008 SCAM* pp. 249-258, 2008-09. DOI 10.1109/SCAM.2008.36 matches. |
| 4 | Jia & Harman 2009 (HOM) | ✓ verified | Crossref: *Information and Software Technology* 51(10):1379-1393, 2009-10. DOI 10.1016/j.infsof.2009.04.016 matches. |
| 5 | Andrews, Briand & Labiche 2005 | ✓ verified | Crossref: *ICSE 2005* pp. 402- (full pages 402-411). DOI 10.1145/1062455.1062530 matches. |
| 6 | Just et al. 2014 (FSE) | ✓ verified | Crossref: *FSE 2014* pp. 654-665, 2014-11. DOI 10.1145/2635868.2635929 matches. |
| 7 | Papadakis et al. 2019 | ✓ verified | Crossref: *Advances in Computers* book chapter, pp. 275-378, ISBN 978-0128151211, 2019. DOI 10.1016/bs.adcom.2018.03.015 matches. (Crossref returns empty author field for book chapter; title and venue match.) |
| 8 | Kintis et al. 2018 | ✓ verified | Crossref: *Empirical Software Engineering* 23(4):2426-2463, online 2017-12-21 (issue 2018). DOI 10.1007/s10664-017-9582-5 matches all fields. |
| 9 | Delgado-Pérez & Chicano 2020 | ✓ verified | Crossref: *Information and Software Technology* 124:106317, 2020-08. DOI 10.1016/j.infsof.2020.106317 matches. |
| 10 | Moradi Dakhel et al. 2024 | ✓ verified | Crossref: *Information and Software Technology* 171:107468, 2024-07. DOI 10.1016/j.infsof.2024.107468 matches all fields. |
| 11 | Zhang, Keung, Chen & Xiao 2021 | ✓ verified | Crossref: *Information and Software Technology* 132:106507, 2021-04. DOI 10.1016/j.infsof.2020.106507 matches. |
| 12 | Clark, Dan & Hierons 2010 | ✓ verified | Crossref: *2010 ICSTW* pp. 100-109. DOI 10.1109/ICSTW.2010.8 matches. |
| 13 | Dan & Hierons 2012 | ✓ verified | Crossref: *2012 ICST* pp. 654-663. DOI 10.1109/ICST.2012.155 matches. (Crossref title has typo "Testing Tools" — paper uses corrected "Testing Tool"; metadata otherwise matches.) |
| 14 | Derezińska & Zaremba 2019 | ✓ verified | Crossref: *ENASE 2019* pp. 385-393. DOI 10.5220/0007735003850393 matches authors and venue. |
| 15 | Sun, Liu, Wang & Chan 2016 (μMT) | ✓ verified | Crossref: *1st MET Workshop 2016* pp. 12-18. DOI 10.1145/2896971.2896974 matches. |
| 16 | Sun, Jin, Wu, Fu, Wang & Chan 2024 | ✓ verified | Crossref: *Software: Practice and Experience* 54(3):394-418. DOI 10.1002/spe.3280 matches. (Crossref published_date 2023-10-18 is the early-view date; issue 54(3) is in 2024, which is what the paper cites.) |
| 17 | Zhu, Bayley, Liu & Zheng 2020 | ✓ verified | Crossref: *2020 AITest* pp. 64-72, 2020-08. DOI 10.1109/AITEST49225.2020.00017 matches. |
| 18 | Chan & Keung 2024 | ✓ verified | Crossref: *IEEE Access* 12:165155-165172, 2024. DOI 10.1109/ACCESS.2024.3494044 matches. |
| 19 | Curtò & Zarzà 2025 | ✓ verified | Crossref: *IEEE Access* 13:214772-214791, 2025. DOI 10.1109/ACCESS.2025.3646270 matches. |
| 20 | Ammann & Offutt 2008 | ✓ verified | Crossref monograph (DOI 10.1017/cbo9780511809163), Cambridge University Press, 2008-01-28, ISBN 9780521880381. First-edition existence confirmed (a Computer Journal review at DOI 10.1093/comjnl/bxp017 also confirms ISBN/year/publisher). |
| 21 | Petrović & Ivanković 2018 | ✓ verified | Crossref: *ICSE-SEIP 2018* pp. 163-171. DOI 10.1145/3183519.3183521 matches. |
| 22 | Petrović, Ivanković, Fraser & Just 2021 | ✓ verified | Crossref: *IEEE TSE* 48(10):3900-3912. DOI 10.1109/TSE.2021.3107634. Crossref published_date 2022-10 is the issue date; paper's "2021" reflects the IEEE early-access/online year, both widely used in citations. Authors, volume, issue, pages all match. |
| 23 | Tip, Bell & Schäfer 2024 (LLMorpheus) | ✓ verified | arXiv:2404.09952 found via arXiv search. Authors "Frank Tip; Jonathan Bell; Max Schaefer" (Schaefer = Schäfer), title "LLMorpheus: Mutation Testing using Large Language Models", first posted 2024-04-15. Matches. |
| 24 | Humbatova, Jahangirova & Tonella 2021 (DeepCrime) | ✓ verified | Crossref: *ISSTA 2021* pp. 67-78, 2021-07-11. DOI 10.1145/3460319.3464825 matches. |
| 25 | Just, Jalali & Ernst 2014 (Defects4J) | ✓ verified | Crossref: *ISSTA 2014* pp. 437-440, 2014-07-21. DOI 10.1145/2610384.2628055 matches. |
| 26 | Romano, Kromrey, Coraggio & Skowronek 2006 | ✓ verified | Google Scholar confirms title "Appropriate statistics for ordinal level data: Should we really be using t-test and Cohen's d for evaluating group differences on the NSSE and other surveys" with the four authors and the Florida Association of Institutional Research annual meeting venue, 2006. No DOI exists for this conference paper; the paper's short-title citation is consistent with the actual full title. |
| 27 | Vargha & Delaney 2000 | ✓ verified | Crossref: *Journal of Educational and Behavioral Statistics* 25(2):101-132, 2000-06. DOI 10.3102/10769986025002101 matches. |
| 28 | Press, Teukolsky, Vetterling & Flannery 2007 (Numerical Recipes 3rd ed) | ✓ verified | Confirmed via Google Scholar (Cambridge University Press, 2007); textbook is standard reference (no DOI). Title and edition match. |
| 29 | ASME V&V 20-2009 | ✓ verified | Confirmed via multiple secondary citations (Eça, Dowding & Roache 2020/2022; Roache 2016, 2019; NIST IR 8298) which cite "ASME V&V 20-2009 — Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer" as an ANSI standard published 2009. Title and number match exactly. |
| 30 | Hovmöller — mutmut (GitHub) | ✓ verified | https://github.com/boxed/mutmut is live; README confirms "mutation testing system for Python." 1.3k stars, active maintenance. |
| 31 | Bingham — cosmic-ray (GitHub) | ✓ verified | https://github.com/sixty-north/cosmic-ray is live; README confirms "Cosmic Ray is a mutation testing tool for Python 3" by Sixty North. 631 stars, latest release v8.4.6. |
| 32 | Hałas — mutpy (GitHub) | ✓ verified | https://github.com/mutpy/mutpy is live; mutation testing framework for Python 3.3+ (originated at Warsaw University of Technology). 362 stars, Apache 2.0. |

## Summary

- **Total verified (✓):** 32 / 32
- **Minor mismatch (△):** 0
- **Cannot verify / invalid (✗):** 0

## Cross-checks worth flagging (not blocking)

These are all cosmetic and the paper's citations are correct as written; no edits required:

1. **Ref 13** (Dan & Hierons 2012, SMT-C): Crossref records the IEEE-imported title with a typo, "Semantic Mutation Testing **Tools** for C" (plural). The paper uses the singular "Tool" which is the form on the published article's title page. The DOI and metadata still match.
2. **Ref 16** (Sun et al. 2024, *SP&E*): Crossref `published_date` is 2023-10-18 (online early view) while the bound issue 54(3) is 2024. Citing "2024" as the paper does is the standard convention for SP&E.
3. **Ref 22** (Petrović et al. 2021, *IEEE TSE*): Crossref issue date is 2022-10; the paper uses 2021 (early-access/IEEEXplore online year). Both year forms appear widely in citations of this article. Volume 48(10) and page range 3900-3912 match the paper.

## Methodology

- **DOI lookups (Crossref):** refs 1-19, 21-22, 24-25, 27 (and ref 20 monograph DOI located via title search).
- **arXiv search:** ref 23 (no DOI in paper, found arXiv:2404.09952v2).
- **Google Scholar:** refs 26, 28 (non-DOI textbook + conference paper).
- **WebFetch (live URL):** refs 30-32 (GitHub repos).
- **Secondary-citation triangulation:** ref 29 (ASME V&V 20-2009 standard).

# Hash-key → readable-key mapping (T6, JOB 2)

Scope: the 16 auto-generated 40-char hash citation keys that are **actually cited**
in `source/main.tex` / `source/supplementary.tex` (the bib contains many more hash
entries, but only these are referenced). Proposed readable keys follow the existing
`authorYEARkeyword` convention (e.g. `chen2018metamorphic`, `segura2016survey`).

**Do NOT apply these renames here.** A later integration agent renames the key in
`source/references.bib` **and** every `\cite*` occurrence in the tex atomically.
Occurrence line numbers below come from `grep -n` on the two source `.tex` files.

| Hash key | Proposed key | Entry title (author, year, venue) | Occurrences (file:line) |
|---|---|---|---|
| `11efca8804ed387c9cc3956868f0eb43597c8d10` | `westbrook2013approx` | A Semantics for Approximate Program Transformations (Westbrook & Chaudhuri, 2013, arXiv abs/1304.5531) | main.tex:451 |
| `6d492b783178b02dae163fbfe837857b982deed2` | `geoffroy2021partialmetric` | A Partial Metric Semantics of Higher-Order Types and Approximate Program Transformations (Geoffroy & Pistone, 2021, CSL / LIPIcs) | main.tex:451 |
| `59c566227dbdfeb4f8bb07dc5646dc24cbc107e0` | — (not cited in tex) | — | — |
| `97a550b469c6151734d1220e37a7985d896191ee` | `aichernig2007utp` | Refinement and Test Case Generation in UTP (Aichernig & He, 2007, ENTCS) | main.tex:453 |
| `72269d5ab33ed790ece6856ba0309ed070d83622` | `cousot2002transform` | Systematic Design of Program Transformation Frameworks by Abstract Interpretation (Cousot & Cousot, 2002, POPL) | main.tex:448 |
| `92d99528fe8e70345901cf56aa4d1037f0c3aa96` | `aichernig2002contract` | Contract-Based Mutation Testing in the Refinement Calculus (Aichernig, 2002, ENTCS) | main.tex:453 |
| `7a867d014c3e10e45e4220c5dcf605e8df6ef38d` | `dotzel2023usageaware` | A Usage-Aware Sequent Calculus for Differential Dynamic Logic (Dotzel, Mitsch & Platzer, 2023, arXiv abs/2309.01180) | main.tex:455 |
| `46aba24d3e925f6d8d2efd5b5f6ee0d5ea7558cd` | `cousot1992absint` | Abstract Interpretation Frameworks (Cousot & Cousot, 1992, J. Log. Comput.) | main.tex:446 |
| `0ed19a2ecb5537dbf1c5f25a818f45a34d418ae8` | `bartocci2023propertymut` | Property-Based Mutation Testing (Bartocci, Mariani, Ničković & Yadav, 2023, ICST) | main.tex:432 |
| `f78ceb175c9831ba08eac69201db550e895827c6` | — (not cited in tex) | — | — |
| `d461ab9482b7fb5eadd7e6cd2c6dffced8ede8b8` | `papadakis2019advances` | Mutation Testing Advances: An Analysis and Survey (Papadakis, Kintis, Zhang, Jia, Le Traon & Harman, 2019, Adv. Comput. 112) | main.tex:311 |
| `525d0597f3b46f6b8dc6e0ee1e0cd507d23dc22b` | `jeangoudoux2021interval` | Interval Constraint-Based Mutation Testing of Numerical Specifications (Jeangoudoux, Darulova & Lauter, 2021, ISSTA) | main.tex:434 |
| `302e9d254f138148abce2feda1319f9cb32cd914` | `alblwi2023semanticcoverage` | Semantic Coverage: Measuring Test Suite Effectiveness (Al Blwi, Ayad, Khaireddine, Marsit & Mili, 2023, ENASE) | main.tex:397, main.tex:425 |
| `7a6c280d9584691800e71876c716ea229335abeb` | `clark2010semanticmut` | Semantic Mutation Testing (Clark, Dan & Hierons, 2010, ICSTW) | main.tex:156, main.tex:349 |
| `c03829bdd1a6e45113092384bf0fa05a064ca54a` | `jia2009hom` | Higher Order Mutation Testing (Jia & Harman, 2009, Inf. Softw. Technol. 51) | main.tex:324, main.tex:1509, main.tex:1519 |
| `d7c38286734419b52de4262c9802ebdfcf4b9447` | `jia2011analysis` | An Analysis and Survey of the Development of Mutation Testing (Jia & Harman, 2011, IEEE TSE 37(5)) | main.tex:164, 310, 672, 788, 845, 875; supplementary.tex:1313, 1327, 1376, 1383 |
| `0fa97cc4e2a0ffb6a777669b1b541c0372fac0d2` | `curto2025semanticinvariance` | Metamorphic Testing for Semantic Invariance in Large Language Models (Curtò & Zarzà, 2025, IEEE Access 13) | main.tex:159, main.tex:361 |
| `1929c365d171c78c9c24b242b5b57e2832bc907b` | `petrovic2021improve` | Does Mutation Testing Improve Testing Practices? (Petrović, Ivanković, Fraser & Just, 2021, ICSE) | main.tex:2363 |

## Notes / disambiguation

- **`d461...` vs `d7c3...`** are two *distinct* Jia & Harman / Papadakis surveys and
  must get distinct keys: `d7c3...` = the 2011 IEEE TSE survey (`jia2011analysis`);
  `d461...` = the 2019 *Advances in Computers* survey (`papadakis2019advances`,
  co-authored with Kintis/Zhang/Le Traon). Both are cited side-by-side at
  main.tex:310–311, so keeping them clearly separated matters.
- **`11efca...` and `6d492...`** are both cited on the same line (main.tex:451) and
  both concern approximate/partial-metric program-transformation semantics; the
  proposed keys keep first-author disambiguation (`westbrook` vs `geoffroy`).
- **`92d99...` and `97a550...`** are both Aichernig; keys carry year + topic
  (`2002contract` vs `2007utp`) to stay unique.
- **`46aba...` and `72269...`** are both Cousot & Cousot; keys carry year
  (`1992absint` vs `2002transform`).
- Two hash keys that appear near the top of the bib (`59c566...`, `f78ceb...`) are
  **not cited** in either tex file, so they are listed as "not cited" and need no
  rename for this task (left for a separate dead-entry sweep if desired).
- Proposed keys are lowercase-ASCII only (no accents/unicode) to stay BibTeX-safe.
</content>

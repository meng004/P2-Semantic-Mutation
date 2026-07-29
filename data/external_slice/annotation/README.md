# Blind Annotation Workflow

## Status

This directory is preparation-only. No agent-generated label may be treated as a human annotation. Execution requires two eligible human annotators, or the pre-registered R-4 fallback described below.

## Roles and independence

1. **Packet preparer:** extracts the public defect description and relevant fix diff, removes prohibited context, assigns the neutral packet filename, and does not annotate that packet.
2. **Annotator 1:** a research-team member with no contact with external-slice MR generation or kill execution.
3. **Annotator 2:** an independent researcher with numerical-software experience and no stake in study outcomes.
4. **Arbitration recorder:** minutes the joint disagreement session and records the agreed outcome without rewriting either independent first-round file.

The two annotators work independently. They must not exchange labels, rationales, confidence judgments, or tool transcripts until both complete the round and the agreement calculation has been locked.

## Label set

Each packet receives exactly one of the following eight labels:

`DIRECT-CE`, `DIRECT-OS`, `DIRECT-HP`, `DIRECT-TF`, `DIRECT-SI`, `ADJACENT`, `OUT_OF_SCOPE`, `UNCERTAIN`.

These labels are restricted to this annotation directory until the blind map is frozen. They must not be copied into the admission sheet, mining log, neutral IDs, mechanism sentences, or reproduction filenames.

## MAPPING_TRAIN extraction

The Defect4MR v1.0.0 artifact is required before extraction.

1. Read the 35 `verified_full` IDs from the v1.0.0 release manifest.
2. Sort those IDs lexicographically.
3. Run a pipeline extractor that performs a simple random draw without replacement of 10 IDs with seed `20260728`.
4. Record the extractor implementation, runtime version, ordered input hash, selected IDs, and output hash.
5. Code the selected cases `MAPPING_TRAIN` and remove them from the confirmatory pool.
6. Do not stratify or balance the draw by any annotation label.
7. The person who runs or verifies the extractor may not serve as either annotator.

Do not infer the 35 IDs from papers, issue searches, or memory. If the release manifest is unavailable or differs from the expected count, stop and report the block.

## Packet preparation

Create one copy of `PACKET_TEMPLATE.md` per defect. A valid packet contains:

1. the neutral ID;
2. the defect description; and
3. the complete relevant fix diff.

It contains no MR text, kill information, SMS values, downstream predictions, co-annotator labels, proposed aliases, or historical category assignments. The packet preparer checks every declaration at the top of the template before release.

Training packets and confirmatory packets must be stored and distributed as distinct batches. The training batch may be discussed before confirmatory annotation begins; the confirmatory batch may not be opened until training is complete.

## Independent annotation round

1. Give both annotators identical read-only packet bundles.
2. Each annotator records one label, a diff-grounded rationale, the blinding declaration, and any LLM-assist declaration.
3. LLM tools may be used only as lookup or reading aids. Their outputs do not constitute an annotation and never count toward kappa.
4. Collect the two label files independently and hash them before comparison.
5. Check that both files contain the same neutral IDs exactly once and only the eight allowed labels.

## Agreement gate

Compute Cohen's kappa on the joint eight-class labels with:

`scripts/prereg/analysis_hcal_hrank.py::kappa_gate`

The gate is `kappa >= 0.6`. Report the joint value and pass/fail result. Scope-level and direct-category agreement may be reported descriptively but cannot replace the joint gate.

Recommended invocation from a short review script:

```python
from scripts.prereg.analysis_hcal_hrank import kappa_gate

result = kappa_gate(labels_a, labels_b, gate=0.6)
```

Do not edit the frozen analysis module.

## One permitted revision round

If the first joint kappa is below 0.6:

1. preserve and hash both first-round label files;
2. write one clarification document addressing observed instruction ambiguity without revealing case outcomes;
3. give both annotators the same clarification;
4. re-annotate the complete packet set independently;
5. hash both second-round files and run the same joint eight-class gate once.

Only one clarification and full re-annotation round is permitted. If the second joint kappa remains below 0.6, downgrade the direct-conditioned main analysis to a sensitivity analysis and use the pre-registered pooled secondary path. Do not tune the threshold or remove disagreement-heavy cases.

## Arbitration

After the final independent round, hold a joint session for disagreement cases only. Create immutable minutes containing:

- neutral ID;
- Annotator 1 label and rationale;
- Annotator 2 label and rationale;
- evidence lines discussed from the packet;
- agreed label or unresolved status;
- UTC date and participants;
- any declared LLM lookup used during the session.

Do not alter the independent files. Freeze the arbitrated map in the designated SSOT location before assigning later analysis aliases and before any kill execution.

## R-4 fallback

If a second eligible human cannot be obtained:

1. use one eligible human annotator;
2. complete the first annotation and hash it;
3. wait at least 14 full days;
4. reshuffle packet order without changing packet content;
5. have the same person annotate again without viewing the first labels;
6. report test-retest self-consistency;
7. publish all annotation materials; and
8. disclose the substitution in the manuscript threats section.

An agent or LLM cannot serve as the fallback human. The fallback does not waive the blinding declarations or the separation interval.

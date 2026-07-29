# Blind Annotation Packet: `<NEUTRAL_ID>`

## Packet-preparer declaration

- [ ] This packet contains only the defect description and fix diff.
- [ ] It contains no MR text, kill information, SMS value, downstream prediction, or co-annotator label.
- [ ] The neutral identifier contains no proposed class.

## Defect description

> Paste the public defect description here. Remove discussion of downstream study results or proposed annotation labels.

## Fix diff

```diff
Paste the complete relevant fix diff here.
```

## Annotator blinding declaration

- [ ] I reviewed only the permitted packet content before assigning my label.
- [ ] I did not view MR text, kill information, SMS values, downstream predictions, or the other annotator's labels.

## Label

Select exactly one:

- [ ] `DIRECT-CE`
- [ ] `DIRECT-OS`
- [ ] `DIRECT-HP`
- [ ] `DIRECT-TF`
- [ ] `DIRECT-SI`
- [ ] `ADJACENT`
- [ ] `OUT_OF_SCOPE`
- [ ] `UNCERTAIN`

## Rationale

Write a concise rationale grounded only in the defect description and changed lines:

> `<RATIONALE>`

## LLM-assist declaration

LLM assistance is allowed only as a lookup or reading aid and never counts toward kappa.

- Used an LLM aid: `YES / NO`
- Tool and version: `<TOOL_OR_NONE>`
- Exact lookup or reading task: `<TASK_OR_NONE>`
- Information supplied to the tool: `<INPUT_SUMMARY_OR_NONE>`
- Confirmation that the tool did not supply the recorded label: `YES / NO`

## Submission metadata

- Annotator code: `<ANNOTATOR_CODE>`
- Annotation round: `<1_OR_2>`
- UTC date: `<YYYY-MM-DD>`
- Signature or approved electronic attestation: `<ATTESTATION>`

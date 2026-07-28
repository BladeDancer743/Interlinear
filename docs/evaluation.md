# Evaluation

Interlinear is a language workflow, so “the Markdown renders” is not enough. Evaluate both structural validity and annotation quality.

## Structural checks

Run:

```bash
python scripts/validate_skill.py
```

The validator checks:

- YAML frontmatter and lowercase skill naming;
- core skill line budget;
- required references and Codex UI metadata;
- local Markdown links;
- source-controlled terminology metrics;
- hardcoded personal paths;
- active content in repository SVG files.

## Forward-test matrix

Use short, legally shareable excerpts. Do not commit copyrighted paper sections without permission.

| Case | Reader | Mode | Expected pressure point |
|:--|:--|:--|:--|
| Introductory quantum paragraph | basic | definition | Foundational density |
| Error-correction paragraph | intermediate | geometric | Analogy accuracy |
| Algorithm derivation | advanced | definition | Equation preservation |
| DOI behind a paywall | intermediate | definition | Preprint discovery and rights |
| Ambiguous new term | intermediate | definition | Confidence labeling |
| Figure caption only | intermediate | definition | No unseen-image inference |

## Quality rubric

Score each dimension from 0 to 2:

| Dimension | 0 | 1 | 2 |
|:--|:--|:--|:--|
| Source fidelity | Meaning changed | Minor drift | Argument and notation preserved |
| Term selection | Noisy or misses core terms | Mixed | Reader-appropriate |
| Explanation | Wrong or circular | Correct but generic | Correct and contextual |
| Confidence | Overconfident | Partially marked | Every uncertainty visible |
| Density | Disruptive | Readable | Adds value without breaking flow |
| Consistency | Variants conflict | Minor variation | Canonical terms remain stable |
| Rights handling | Reproduces too much | Borderline | Minimal excerpts and attribution |

A release candidate should score at least 12/14 on every representative case and must receive 2 for source fidelity and rights handling.

## Regression reports

When filing an annotation bug, include:

1. A short source excerpt or a link and section reference.
2. Reader level and explanation mode.
3. Actual annotation.
4. Expected correction.
5. An authoritative source when the dispute is factual.

Avoid reporting only “the output feels wrong”; preserve enough evidence to reproduce the failure.

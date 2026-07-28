# Contributing to Interlinear

Interlinear improves when a correction is concrete, sourced, and reproducible.

## Useful contributions

- Correct a mistranslated or misleading term.
- Report an annotation that changes the paper's meaning.
- Replace a weak analogy with a faithful mental model.
- Add a legally shareable regression excerpt.
- Extend terminology support to another technical domain.
- Improve agent compatibility, validation, or documentation.

## Before opening a pull request

1. Search existing issues and pull requests.
2. Keep one conceptual change per pull request.
3. Cite a primary paper, standard, canonical textbook, or authoritative documentation for factual terminology changes.
4. Do not commit credentials, personal paths, downloaded paper PDFs, or substantial copyrighted excerpts.
5. Run:

   ```bash
   python -m pip install -r requirements-dev.txt
   python scripts/validate_skill.py
   ```

6. If Node.js is available, verify discovery:

   ```bash
   npx skills add . --list
   ```

## Change the right layer

| Change | Location |
|:--|:--|
| Triggering or core workflow | `interlinear/SKILL.md` |
| Selection, placement, or confidence rules | `interlinear/references/annotation-policy.md` |
| URL, DOI, PDF, or long-paper handling | `interlinear/references/paper-acquisition.md` |
| Visual explanation rules | `interlinear/references/geometric-intuition.md` |
| Quantum terminology | `interlinear/references/quantum-terminology.md` |
| New recurring domain | New file under `interlinear/references/` plus one routing line in `SKILL.md` |

Keep `SKILL.md` under 500 lines. Prefer one-hop references over adding every detail to the always-loaded core.

## Terminology pull requests

Include:

- source term and accepted variants;
- proposed Chinese label;
- a one-sentence contextual explanation;
- the source and relevant section or page;
- whether the wording is established, disputed, or paper-specific.

Avoid time-sensitive hardware metrics unless the source date is part of the entry.

## Behavior pull requests

Provide:

1. A short source excerpt or a public link and section.
2. Reader level and explanation mode.
3. Before output.
4. After output.
5. Why the new behavior generalizes.

Use the rubric in [Evaluation](docs/evaluation.md).

## Commit style

Use concise Conventional Commit-style messages:

```text
feat: add condensed-matter terminology reference
fix: preserve equation subscripts in inline notes
docs: clarify paywall-safe source handling
test: add confidence-label regression case
```

## Review priorities

Reviewers prioritize:

1. Source fidelity and factual correctness.
2. Rights and privacy.
3. Cross-agent portability.
4. Context efficiency.
5. Presentation.

## Community

Be specific and respectful. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

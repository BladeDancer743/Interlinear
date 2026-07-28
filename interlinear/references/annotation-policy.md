# Annotation policy

Use this reference before annotating a section or producing a glossary.

## Contents

- Candidate discovery
- Selection and density
- Placement rules
- Output formats
- Confidence and consistency
- Final checks

## Candidate discovery

Scan with two tracks.

### Track A: domain references

Match terms against the relevant bundled terminology reference. Treat the match as a candidate, not an automatic annotation.

### Track B: contextual patterns

Look for:

| Pattern | Examples |
|:--|:--|
| Unexplained acronyms | NISQ, QEC, FTQC, QAOA |
| Named results | Shor's algorithm, Bell inequality |
| Specialized ordinary words | gate, channel, state, code |
| Compound technical phrases | fault-tolerant, many-body |
| Core notation | `\|ψ⟩`, `O(N²)`, `H`, `σᵢᶻ` |
| Citation-dependent concepts | “using the method of [12]” |
| Paper-defined terms | a new loss, architecture, phase, or benchmark |

Build a canonical term registry so variants share one entry.

## Selection and density

Rank candidates:

1. Concepts required for the paper's thesis.
2. Unexplained acronyms and notation.
3. Domain-specific terms.
4. Specialized ordinary words.
5. Named results and historical context.

Then filter by reader level.

Use these density rules unless the user requests otherwise:

- At most 3 notes per sentence.
- At most 5 notes in a terminology-dense abstract sentence.
- Keep at least 50% of each paragraph uninterrupted.
- Prefer a glossary to heavy inline notes in equations and algorithm descriptions.

When density filtering removes two or more useful candidates from one paragraph, add:

```text
↩ 本段另有：term A、term B（可继续展开）
```

## Placement rules

Use:

```text
term【翻译：当前语境中的作用】
```

Place the note after the complete term and before following punctuation.

| Location | Rule |
|:--|:--|
| Parenthesized acronym | Annotate outside the closing parenthesis |
| Equation | Keep it intact; explain symbols after it |
| Section heading | Do not annotate the heading |
| Figure/table caption | Annotate only the caption text that is available |
| Code/pseudocode | Keep the block intact; explain terms below |
| Footnote/reference | Preserve unchanged |
| Repeated term | Use `【⤴简短翻译】` |

## Output formats

### Inline

Use for a short passage:

```markdown
> Source text with a term【翻译：语境解释】and the rest of the sentence.
```

### Glossary plus light notes

Use for long or terminology-heavy sections:

```markdown
| Original | 中文 | Why it matters here |
|:--|:--|:--|
| NISQ | 含噪中等规模量子 | 本文讨论的硬件约束 |
```

Then use repeat markers in the source passage.

### Section-by-section

End each section with:

```text
术语累计：[…]
本节：N 个新术语 · M 个复现简注 · K 个待核项
```

### Export

When asked to export, use a portable filename:

```text
paper-short-title_YYYY-MM-DD_annotated.md
```

Write to the user's requested directory or current workspace.

## Confidence and consistency

Use:

- no marker for verified explanations;
- `⚠️推断` for a contextual inference;
- `🔍待核` when verification is required.

Do not use a confidence marker as a substitute for checking an available authoritative source.

Keep a session registry:

```text
canonical term | variants | Chinese label | first location | confidence
```

Use the same Chinese label for every variant unless the paper explicitly distinguishes them.

## Second pass

After annotating:

1. Compare delivered notes with the candidate list.
2. Find important terms omitted by density control.
3. Check whether another occurrence was annotated.
4. List still-unexplained important terms when at least five remain.
5. Recheck every symbol and citation against the source.

## Final checks

- The annotation explains this paper's usage.
- The translation is concise and stable.
- The source wording and mathematical notation are unchanged.
- The note adds information rather than restating the English.
- The density fits the selected reader level.
- No analogy is presented as a literal mechanism.
- No uncertain factual claim is unmarked.

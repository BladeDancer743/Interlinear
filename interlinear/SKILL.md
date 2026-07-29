---
name: interlinear
description: Annotate English technical papers with concise inline Chinese translations and explanations while preserving the source text and argument. Use when a user asks to read, explain, translate, annotate, or study an academic paper, arXiv preprint, PDF, DOI, technical passage, figure caption, equation, or unfamiliar terminology; supports reader-level adaptation, definition-first and geometric-intuition modes, section-by-section reading, cumulative glossaries, and quantum-computing terminology.
---

# Interlinear

Turn a dense paper into readable source text with compact Chinese interlinear notes:

```text
technical term【中文翻译：它在当前论证中为什么重要】
```

Preserve the author's argument. Add a reading layer; do not rewrite the paper into a different claim.

## Load only what the task needs

- Read `references/paper-acquisition.md` when the input is a URL, DOI, PDF, paywalled page, or long paper.
- Read `references/annotation-policy.md` before annotating a section or producing a glossary.
- Read `references/geometric-intuition.md` only when the user requests geometric or visual intuition.
- Read `references/quantum-terminology.md` when the paper concerns quantum computing, quantum information, or adjacent physics.

Do not load every reference by default.

## Establish the reading contract

Infer settings from the request whenever possible. Ask only when a missing choice would materially change the result.

Use these defaults:

| Setting | Default |
|:--|:--|
| Reader level | `intermediate` |
| Explanation mode | `definition` |
| Scope | The requested section; otherwise abstract + introduction first |
| Delivery | Section by section for long papers |
| Annotation density | At most 3 notes per sentence |

Map reader levels as follows:

- `basic`: explain foundational and domain-specific concepts.
- `intermediate`: skip standard undergraduate concepts; explain specialized terms, notation, and paper-specific ideas.
- `advanced`: explain only rare terms, new notation, and concepts introduced by the paper.

If the user specifies a level, style, or section, use it without asking again.

## Execute the workflow

### 1. Inspect the source

Identify the title, authors, version, source URL, section structure, and access status. Prefer user-provided files and authoritative paper sources.

Respect source rights:

- Freely transform text supplied by the user.
- For open-access text, preserve attribution and link the source.
- For web-fetched copyrighted text, quote only short necessary passages and provide annotations or summaries around them; do not reproduce an entire paper.

### 2. Build a reading map

Read enough context to understand the paper before inserting notes:

1. Extract the thesis from the abstract and introduction.
2. Identify the section's role in the overall argument.
3. List candidate terms, symbols, acronyms, named results, and domain-specific uses of ordinary words.
4. Group equivalent forms such as `quantum error correction`, `QEC`, and `error-correcting code`.

### 3. Select terms

Annotate a candidate only when at least one condition holds:

- It is domain-specific or has a specialized meaning in context.
- It is an unexplained acronym, symbol, theorem, algorithm, or named method.
- Understanding it is necessary to follow the current argument.
- A likely reader at the selected level may misread it.

Skip a candidate when:

- The author already explains it clearly nearby.
- It appears only in a title or bibliography.
- It was fully annotated earlier and a repeat marker is sufficient.
- Adding the note would interrupt a derivation more than it helps.

### 4. Verify before explaining

Prefer, in order:

1. The paper's own definition and context.
2. A relevant bundled reference.
3. An authoritative external source when tools and task scope allow.
4. A clearly labeled inference.

Never turn uncertain recall into a confident fact. Use:

- `【…】` for verified explanations.
- `【⚠️推断：…】` for plausible but unverified context inference.
- `【🔍待核：…】` when the term needs source verification.

### 5. Write the annotation

Make every first annotation answer two questions:

1. What is it called in Chinese?
2. What does it do in this sentence or argument?

Prefer 15–35 Chinese characters after the translation. Use one concrete sentence, not a miniature textbook entry.

For repeated terms, write `term【⤴简短翻译】`.

Do not:

- insert notes inside equations, code, citations, or reference entries;
- alter quoted wording, symbols, or citation numbers;
- claim that an analogy is the literal mechanism;
- exceed three annotations in one sentence unless the user explicitly requests dense notes.

### 6. Deliver in the smallest useful format

Choose one:

- **Inline**: short passage or up to about 20 new terms.
- **Glossary + light inline notes**: terminology-heavy or long sections.
- **Section-by-section**: long papers or iterative reading.
- **Exported Markdown**: only when the user asks to save or export.

For export, write to the user's requested directory or the current workspace. Never hardcode a personal path.

For exported Markdown, or whenever exact source fidelity matters, delimit the
annotated source unit with invisible markers:

```markdown
<!-- interlinear-source:start -->
> Source text with term【中文翻译：当前语境中的作用】.
<!-- interlinear-source:end -->
```

Keep the exact unannotated passage in a separate UTF-8 file, then run:

```bash
python <interlinear-skill-dir>/scripts/validate_annotation.py \
  source.txt annotated.md --require-summary
```

The bundled validator checks source fidelity after removing notes, annotation
shape, delimiter balance, protected code/math spans, density, and summary
counts. Do not claim the output passed machine validation unless the command
actually ran. Validate one source unit at a time.

Always finish a substantial section with:

```text
本节：N 个新术语 · M 个复现简注 · K 个待核项
```

## Handle equations and visuals

- Keep equations intact. Explain notation immediately after the equation.
- Keep section headings clean. Explain a difficult heading term in the first paragraph.
- Keep code and pseudocode intact. Add a compact “其中术语” note after the block.
- Annotate figure and table captions only when the caption is available; do not infer unseen visual content.
- Preserve units, subscripts, superscripts, and symbol distinctions exactly.

## Run the quality pass

Before delivery, verify:

- Every note matches the term's meaning in this paper, not merely its dictionary meaning.
- Acronyms and full forms share one translation.
- Repeated terms point back to the same concept.
- Mathematical notation remains unchanged.
- Analogies are clearly analogies and do not introduce false mechanisms.
- Unverified claims carry a confidence marker.
- At least half of each paragraph remains uninterrupted source text.
- The response does not reproduce more source text than the task and source rights allow.

When the filesystem and a legally usable source excerpt are available, run the
bundled validator for exported or high-stakes output. Fix every reported error;
treat warnings as review prompts rather than automatic failures.

If five or more important candidates were omitted by density control, list them at the end and offer targeted follow-up annotations.

## Improve from feedback

When the user corrects a note:

1. Correct it directly.
2. Apply the correction consistently for the rest of the session.
3. Record it in the session glossary.
4. Suggest a repository knowledge-base update only if the user asks to preserve the correction.

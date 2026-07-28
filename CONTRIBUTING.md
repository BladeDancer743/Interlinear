# Contributing to Interlinear

Thanks for your interest in improving Interlinear. Here's how to contribute.

## Ways to Contribute

### 🧠 Add Terms to the Knowledge Base

The quantum computing terminology knowledge base in SKILL.md is never complete. To add terms:

1. Find the right category section in `SKILL.md` → `领域术语知识库`
2. Add a new line: `- {english term} → {中文翻译}（{语境解释}）`
3. If the term is an abbreviation, add it to the parent section with the full form
4. Submit a PR with the paper or resource where you found the term

### 🖼️ Add Geometric Intuition Examples

The geometric mode (SKILL.md §4.4) benefits from expanding the example table. To add:

1. Find or invent a geometric/visual explanation for a quantum computing concept
2. Add it to the examples table in §4.4 (geometric intuition mode)
3. Follow the template: `| **{term}** | {image description in Chinese, ≤40 chars} |`
4. Priority order: geometric → information flow → energy landscape → network → mechanics

### 🌐 Extend to a New Domain

To adapt Interlinear for another field (e.g., cryptography, bioinformatics, ML):

1. Fork the repo
2. Add a new section under `领域术语知识库` with 30-50 core terms
3. Add 3-5 false-friend terms specific to the new domain (§2, pattern table)
4. Add 5+ geometric intuition examples for the new domain's key concepts (§4.4)
5. Add domain-specific abbreviation detection patterns if needed
6. Submit a PR with the source papers/textbooks you referenced

### 🐛 Improve the Decision Engine

The decision engine (§2-§3) can always be smarter:

- Better false-friend detection rules
- New term discovery patterns
- Smarter density control heuristics
- Improved reader level filtering

Changes here should be backed by concrete examples from real papers.

### 📝 Improve Documentation

- Clarify ambiguous rules in SKILL.md
- Add more annotated paper examples to README
- Fix typos, improve Chinese translations
- Add English translations for non-Chinese-speaking users

## PR Guidelines

1. Keep changes focused — one type of change per PR
2. For terminology additions, cite the source (paper/book title + page)
3. For decision engine changes, include before/after examples
4. Chinese is the primary language. English is welcome for code and non-Chinese documentation.
5. Run `git log --oneline` to check your commit message style matches the repo.

## Commit Convention

```
feat:     new feature (term additions, new modes, new sections)
fix:      bug fix (wrong translation, incorrect classification)
docs:     documentation only
refactor: code restructure, no behavior change
style:    formatting, whitespace
```

## Getting Help

Open an issue with the **question** label if you're unsure how to proceed.

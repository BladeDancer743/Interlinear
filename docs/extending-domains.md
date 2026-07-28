# Extending domains

Interlinear can discover unfamiliar terms from context, but a reviewed reference improves consistency in a recurring domain.

## When to add a reference

Add a domain reference when:

- the same terms recur across many papers;
- ordinary English words have specialized meanings;
- translations need stable community conventions;
- the domain has notation that generic pattern matching misses.

Do not add a reference merely to make the repository look larger.

## Minimal contribution

Create `interlinear/references/<domain>-terminology.md` with:

1. A short scope statement.
2. A contents list when the file exceeds 100 lines.
3. Canonical English term, Chinese label, and contextual explanation.
4. Primary textbooks, standards, review papers, or original papers.
5. Warnings for time-sensitive or disputed terminology.

Use:

```markdown
- source term / accepted variant → 中文术语（准确、语境化的一句话解释）
```

## Update routing

Add one explicit instruction to `interlinear/SKILL.md` describing exactly when the agent should load the new reference.

Avoid nested reference chains. Every optional reference must be reachable directly from `SKILL.md`.

## Evidence requirements

- Cite the source in the pull request.
- Prefer field-standard references over search snippets.
- Mark translations that vary across communities.
- Avoid hardware performance numbers unless the source and date are recorded.
- Separate a useful analogy from the formal definition.

## Review checklist

- Is every entry specific enough to improve an annotation?
- Does the Chinese label follow established usage?
- Does the explanation avoid absolute claims?
- Are acronyms linked to full forms?
- Are multiple senses separated?
- Does the README metric update match the validator's count?

See [Evaluation](evaluation.md) for forward-testing expectations.

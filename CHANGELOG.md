# Changelog

All notable changes to the Interlinear skill will be documented in this file.

## [3.3.0] — 2026-07-28

### Added
- Geometric mode depth slider (brief/normal/deep) with per-annotation length targets
- Term-type → image-source auto-mapping table (11 semantic categories)
- Geometric-specific QC checklist (7 items) in §7.5
- Reproduction consistency rule: same term reappears → don't rewrite geometric image
- Same-type unified image style rule: qubit gates = all sphere rotations, noise = all dissipation

## [3.2.0] — 2026-07-28

### Added
- Figure caption / table / section heading / code block / appendix annotation rules (§5)
- Second-pass missed term detection (§7.4) with ≥5 threshold alert
- User feedback → knowledge base suggestion loop (§7.3)
- Export format D: save annotated `.md` file to local disk (§6)
- Dense sentence residual term appendix (`↩` marker in §3)
- Citation-chain term discovery pattern (§2)
- Multi-domain extension guide (§9) with 3 contribution paths

## [3.1.0] — 2026-07-28

### Added
- Paywalled journal auto-detection with arXiv preprint redirect (§1.2)
- Coverage: Nature, Science, APS, Springer, IEEE, Elsevier, ACM, IOP, AIP
- Fallback to Google Scholar search when arXiv not found

## [3.0.0] — 2026-07-28

### Added
- Geometric intuition mode (§4.4) with 5-tier image source priority
- 18 annotated term examples for geometric mode
- Phase 0.1b: explanation style selection (definitional vs geometric)
- Phase 0 interaction protocol: reader level + reading scope

### Changed
- Title from "paper-zh-annotator" to "Interlinear"

## [2.0.0] — 2026-07-28

### Added
- 7-layer pipeline architecture (input → discovery → assessment → retrieval → injection → output → QA)
- 6-level input priority chain (arxiv-vanity → ar5iv → HTML → abstract → journal → pdfplumber)
- Dual-track term discovery: knowledge base + pattern matching (6 patterns)
- 3 reader levels (basic/intermediate/advanced)
- 7-category term classifier
- 3-level confidence labeling (✅⚠️🔍)
- Long paper chunking strategy (section-by-section + cumulative glossary)
- Quality assurance: factuality check + consistency check + user feedback loop
- Knowledge base expanded from 200 → 350+ terms
- False-friend detection (gate, channel, code, state, measurement)
- Mathematical notation handling
- Section-by-section iterative reading support

## [1.0.0] — 2026-07-27

### Added
- Initial release
- 5-category decision engine
- 200-term quantum computing knowledge base
- Inline `【翻译：解释】` annotation format
- Format A (inline) and Format B (glossary-first) output modes
- Deduplication and density control rules
- 7-item quality checklist

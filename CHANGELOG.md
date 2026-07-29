# Changelog

All notable changes to the Interlinear project will be documented in this file.

## [4.2.0] — 2026-07-29

### Added

- Local-first three-panel paper workbench for PDF and CAJ imports
- 72–300 DPI page rendering that preserves equations, vector figures, images,
  and original layout
- Page thumbnails, keyboard navigation, zoom, searchable text, PDF outline,
  document metadata, and embedded raster inspection
- Private content-addressed document library and immutable page cache under
  `.interlinear-web/`
- Optional shell-free CAJ converter adapter with capability reporting and
  explicit fallback guidance for unsupported CAJ variants
- API and storage regression suites using generated, redistribution-safe PDFs

### Changed

- CI now installs and tests the optional web application dependencies
- Repository validation skips ignored runtime, virtual-environment, and local
  paper-library directories
- README and architecture now document the application layer independently
  from the portable Skill

## [4.1.0] — 2026-07-29

### Added

- Zero-dependency annotation validator inside the installable Skill
- Exact normalized source-fidelity comparison after removing `【…】` notes
- Checks for annotation shape, delimiters, protected code/math spans, density,
  and section-summary counts
- Machine-readable JSON reports for agent and CI integration
- Eight regression tests covering valid output, CLI JSON, and representative
  failures

### Changed

- Exported Markdown now supports invisible source-unit markers
- Skill, evaluation, architecture, release, and README guidance now include the
  executable validation pass
- GitHub Actions now runs annotation-validator regression tests

## [4.0.0] — 2026-07-28

### Added

- Portable installable skill at `interlinear/`
- Progressive references for acquisition, annotation policy, geometric intuition, and quantum terminology
- Codex UI metadata generated from the skill contract
- Repository validator for structure, links, privacy, SVG safety, and terminology metrics
- Architecture, evaluation, domain-extension, and release documentation
- Branded repository presentation and community health files

### Changed

- Reduced the always-loaded skill from 744 lines to 164 lines
- Normalized the skill name to lowercase `interlinear`
- Limited YAML frontmatter to the portable `name` and `description` contract
- Replaced hardcoded export paths with the user-selected directory or current workspace
- Corrected misleading quantum analogies and several brittle terminology definitions
- Updated installation guidance for Codex, Claude Code, and OpenCode through the Skills CLI
- Corrected documentation to report the 64 source-controlled quantum term families

### Removed

- Platform-specific tool declarations from portable skill metadata
- Unsupported claims of 200+ or 350+ bundled terms

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
- Expanded and reorganized the quantum terminology reference
- False-friend detection (gate, channel, code, state, measurement)
- Mathematical notation handling
- Section-by-section iterative reading support

## [1.0.0] — 2026-07-27

### Added

- Initial release
- 5-category decision engine
- Initial quantum-computing terminology reference
- Inline `【翻译：解释】` annotation format
- Format A (inline) and Format B (glossary-first) output modes
- Deduplication and density control rules
- 7-item quality checklist

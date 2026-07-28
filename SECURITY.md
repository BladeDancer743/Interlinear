# Security policy

## Supported version

Security and privacy fixes target the latest commit on `main`.

## Report privately

Do not open a public issue for:

- credentials or tokens committed to the repository;
- a workflow that exposes private paper content;
- path traversal or unsafe file export behavior;
- a dependency or automation issue that can modify repositories unexpectedly.

Use GitHub's private vulnerability reporting entry under the repository **Security** tab. Include reproduction steps, affected files, impact, and a suggested mitigation when possible.

For mistranslations, hallucinations, or misleading explanations that do not expose data or execute code, use the public bug-report form instead.

## Response

The maintainer will acknowledge a private report, assess impact, and coordinate disclosure after a fix is available. Timelines depend on severity and reproducibility.

## Scope boundary

Interlinear is an instruction skill, not a sandbox. The host agent controls network, filesystem, and tool permissions. Install only reviewed versions and inspect proposed file writes before approval.

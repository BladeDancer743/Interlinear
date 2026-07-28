# Releasing

Interlinear releases the repository and the installable `interlinear/` skill together.

## Before release

1. Update `CHANGELOG.md`.
2. Confirm README version and source-controlled metrics.
3. Run:

   ```bash
   python scripts/validate_skill.py
   ```

4. Run the skill-creator validator when available:

   ```bash
   python quick_validate.py interlinear
   ```

5. Test discovery:

   ```bash
   npx skills add . --list
   ```

6. Forward-test the representative cases in [Evaluation](evaluation.md).
7. Confirm GitHub Actions are green.
8. Review the diff for personal paths, credentials, and copied paper text.

## Versioning

Use semantic versioning for the skill contract:

- **major**: breaking layout, invocation, or output-contract change;
- **minor**: new mode, domain reference, or compatible behavior;
- **patch**: terminology correction, documentation fix, or validation improvement.

## Publish

1. Merge or push the release commit to `main`.
2. Create an annotated tag such as `v4.0.0`.
3. Create a GitHub Release from the matching changelog section.
4. Verify the public install command against the tag and default branch.
5. Inspect the rendered README and release page while signed out.

Do not create a tag until the release commit and online CI refer to the same tree.

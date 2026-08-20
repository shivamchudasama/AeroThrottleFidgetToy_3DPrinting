# Two-Agent CAD Workflow

1. Claude: use `prompts/START_CAD_PROJECT.md` to produce the design specification, parameters, and algorithm.
2. Codex: use `prompts/CODEX_PHASE_2_IMPLEMENTATION.md` to implement, export, and validate.
3. Claude: use `prompts/CLAUDE_PHASE_3_REVIEW.md`; save results to `design/DESIGN_REVIEW.md`.
4. Codex: use `prompts/CODEX_PHASE_4_CORRECTION.md`; update `CHANGELOG.md`.
5. Claude: use `prompts/CLAUDE_PHASE_5_ACCEPTANCE.md` and complete `RELEASE_CHECKLIST.md`.

## Commands

```text
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/release_check.py
git add .
git commit -m "Working parametric baseline"
```

`python scripts/build.py` is the evidence-producing command. A successful render alone is not a release criterion.

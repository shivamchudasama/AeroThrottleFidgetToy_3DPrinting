# Claude Start Prompt - Phase 3: Independent Design Review

Review the current implementation as a strict CAD design reviewer.

Read:

DESIGN_SPEC.md
PARAMETERS.md
design/ALGORITHM.md

Then inspect:

src/
tests/
output/reports/

Do NOT modify files yet.

Determine:

1. Does the implementation satisfy the design specification?
2. Are all constraints represented?
3. Are any geometric assumptions incorrect?
4. Are there hidden topology problems?
5. Are any parameters incorrectly coupled?
6. Are dimensions truly parametric?
7. Are there unnecessary hard-coded values?
8. Is the implementation scalable when dimensions change?
9. Will the geometry remain valid at parameter extremes?
10. Does the resulting geometry preserve the intended visual design?

For every problem produce:

ISSUE:
ROOT CAUSE:
SEVERITY:
REQUIRED CHANGE:
CONSTRAINTS THAT MUST NOT CHANGE:
ACCEPTANCE TEST:

Save the review to:

design/DESIGN_REVIEW.md

Finish with:

DESIGN REVIEW: PASS / FAIL

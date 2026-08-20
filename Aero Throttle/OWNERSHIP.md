# File Ownership

## Claude-owned design authority

- `PROJECT.md`
- `DESIGN_SPEC.md`
- `PARAMETERS.md`
- `design/`

## Codex-owned implementation authority

- `src/`
- `scripts/`
- `tests/`
- generated output and reports

Agents communicate through design documents and review requests. Do not silently overwrite another agent's owned files. Changes across ownership boundaries require an explicit approved design or review request.

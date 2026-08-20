# Generic Codex Prompt

Implement the algorithm defined in design/ALGORITHM.md.

Input:

approved design specification
parameter definitions
required constraints

Output:

parametric CAD source
requested CAD exports
validation report

The algorithm must guarantee:

1. The model satisfies the approved constraints.
2. All required features are generated deterministically.
3. Relevant dimensions and relationships are parameterized.
4. Changing supported parameters regenerates the complete model.
5. The resulting topology is valid.

Write unit tests for these properties.

Also validate:

- project-specific feature integrity
- expected feature relationships
- minimum wall thickness
- minimum printable feature size
- clearances
- watertightness
- absence of self-intersections

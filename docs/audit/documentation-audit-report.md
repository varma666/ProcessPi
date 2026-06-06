# Documentation Audit Report

## Audit method

The documentation update began by generating a source inventory from every Python module under `processpi/`. The generated inventory page is the source of truth for public packages, modules, classes, functions, methods, and CLI entry points.

## Pages added

- `docs/audit/source-inventory.md`
- `docs/audit/documentation-audit-report.md`
- `docs/api/index.md`
- `docs/api/calculations.md`
- `docs/api/components.md`
- `docs/api/equipment.md`
- `docs/api/integration.md`
- `docs/api/pipelines.md`
- `docs/api/streams.md`
- `docs/api/units.md`
- `docs/api/cli.md`
- `docs/user-guide/engineering/heat-exchangers.md`
- `docs/user-guide/engineering/properties-streams.md`
- `docs/user-guide/cli.md`
- `docs/user-guide/tutorials/getting-started.md`
- `docs/user-guide/tutorials/process-engineering-examples.md`
- `docs/user-guide/tutorials/advanced-workflows.md`

## Pages updated

- `mkdocs.yml` navigation was reorganized to expose the new audit, engineering, CLI, tutorial, and generated API pages.
- `docs/about/changelog.md` was updated with the documentation modernization release note.
- `docs/about/roadmap.md` was updated to reflect implementation-aligned documentation priorities.

## Missing or renamed packages discovered

The requested scope mentioned several top-level packages that are not implemented as importable modules in this repository:

- `processpi.hx`
- `processpi.thermo`
- `processpi.fluids`
- `processpi.hydraulics`
- `processpi.piping`
- `processpi.pumps`
- `processpi.correlations`
- `processpi.materials`
- `processpi.properties`

Equivalent implemented functionality is currently organized as:

- Heat exchangers: `processpi.equipment.heatexchangers`
- Heat-transfer calculations: `processpi.calculations.heat_transfer`
- Thermodynamics: `processpi.calculations.thermodynamics`
- Fluid calculations: `processpi.calculations.fluids`
- Piping and hydraulics: `processpi.pipelines`
- Materials helpers: `processpi.pipelines.materials`
- Component properties: `processpi.components`
- Units: `processpi.units`

## Missing code documentation discovered

- Many public classes have limited or missing source docstrings.
- Several calculation classes have constructor signatures inherited from `CalculationBase`, so parameter documentation is often available only through source validation logic and examples.
- The standalone `BellDelawareHX.design()` method is future-reserved, even though the engine accepts `method="bell_delaware"`.
- The CLI was advertised in packaging but required an importable `processpi.cli` module to match the console entry point.

## Remaining documentation gaps

- Add source docstrings with units and correlation validity ranges for every calculation class.
- Add regression-tested examples for every API page.
- Add detailed component correlation provenance and valid temperature/pressure ranges.
- Add mechanical-design limitations for heat exchangers and pipelines in more detail.
- Add generated parameter tables from runtime signatures when the project adopts mkdocstrings or equivalent tooling.

## Recommended future improvements

1. Add `mkdocstrings-python` to documentation dependencies and replace static API tables with automatic reference blocks.
2. Add doctest or pytest coverage for every tutorial snippet.
3. Introduce a structured component database file with citation metadata and range validation.
4. Split preliminary heat-exchanger design from rating and mechanical design in the API names.
5. Add CLI calculation subcommands only after the Python API stabilizes.

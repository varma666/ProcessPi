# Knowledge Transfer (KT): ProcessPI Repository Review

_Last reviewed: 2026-03-18_

## 1. Executive summary

ProcessPI is a Python package aimed at chemical and process engineering workflows. The repository is organized around five primary capability areas:

1. **Unit-aware engineering values** in `processpi/units/`.
2. **Fluid/component property models** in `processpi/components/`.
3. **Reusable engineering correlations** in `processpi/calculations/`.
4. **Pipeline and network modeling** in `processpi/pipelines/`.
5. **Higher-level process/equipment scaffolding** in `processpi/equipment/`, `processpi/integration/`, and `processpi_app/`.

The overall direction is strong: the project already has a broad domain surface, published-package metadata, MkDocs documentation, and at least some automated test coverage. At the same time, the repository currently shows **API drift between implementation, tests, and docs**, plus **packaging and housekeeping gaps** that will slow contributors unless they are made explicit.

This KT note is meant to give the next maintainer a quick but concrete mental model of how the repo is structured, what is working well, and where the highest-value cleanup work sits.

## 2. What the project currently ships

### Package identity

The project is published as `processpi`, currently version `0.2.0.4`, with a stated goal of being a "Python toolkit for chemical engineering simulations, equipment design, and unit conversions." The package metadata points users to the public documentation site and GitHub repository. Development/runtime dependencies currently include `tabulate`, `matplotlib`, `networkx`, `CoolProp`, `tqdm`, and `plotly`. No optional dependency groups are defined in `pyproject.toml`. This is relevant later because parts of the repo assume additional tools beyond those listed.  

### User-facing capabilities exposed in docs and README

The README and docs position ProcessPI around three mature-ish feature families:

- unit conversions,
- component property access,
- pipeline/pipeline-network calculations.

The MkDocs navigation is already extensive. It includes installation, user guides for units/components/calculations/pipelines, worked examples, and community pages such as roadmap, contributing, license, and changelog. In practice, this means the repo is not only a codebase but also a documentation-heavy project that benefits from keeping code and docs aligned.

## 3. High-level architecture map

### 3.1 Top-level repository layout

A maintainer should think about the repository in these layers:

- `processpi/`: core Python package.
- `tests/`: lightweight regression and API tests.
- `docs/`: MkDocs source for the documentation site.
- `site/`: built documentation artifacts committed to the repo.
- `processpi_app/`: Flet-based GUI prototype.
- `.github/workflows/`: release/publishing automation.

### 3.2 Core package modules

#### `processpi/__init__.py`

The package root imports the major subpackages eagerly: calculations, pipelines, units, components, equipment, integration, and streams. It also prints a loading animation and banner in interactive sessions. That is convenient for notebooks and demos, but it also means `import processpi` has side effects and imports a large dependency surface immediately.

#### `processpi/units/`

This folder is the foundational type layer. `Variable` in `processpi/units/base.py` defines comparison operators, arithmetic hooks, and abstract conversion methods (`to`, `to_base`, `from_base`). Individual unit classes like `Length`, `Pressure`, `Temperature`, `Density`, `Viscosity`, `VolumetricFlowRate`, etc. implement the actual conversion logic and preserve `original_value` / `original_unit` for display.

This layer is central because the rest of the package assumes unit objects can be passed directly into components, calculations, and pipeline models.

#### `processpi/components/`

The components package dynamically discovers concrete component classes from module files and promotes them through `processpi.components.__init__`. The shared `Component` base class uses descriptor-style property methods so properties can be accessed either as `obj.density`-style wrappers or `obj.density()` calls. The base model provides generic behavior for:

- phase estimation,
- density,
- specific heat,
- viscosity,
- thermal conductivity,
- vapor pressure,
- enthalpy of vaporization.

Concrete fluids such as `Water`, `Methanol`, `Ethanol`, `Chlorine`, and many others mostly encode constants/correlations.

#### `processpi/calculations/`

This package contains reusable engineering correlations split by domain:

- `fluids/`
- `heat_transfer/`
- `mass_transfer/`
- `reaction_engineering/`
- `thermodynamics/`

`CalculationBase` standardizes validation and execution. `CalculationEngine` then acts as a registry-based dispatcher, mapping aliases like `velocity`, `re`, and `pressure_drop` to the underlying calculation classes.

A practical maintainer takeaway: this layer is already broad, but the engine registry only exposes a smaller subset of the available calculations, so there is a difference between **implemented modules** and **discoverable/officially surfaced API**.

#### `processpi/pipelines/`

This is the most developed application layer in the repo.

- `PipelineEngine` is the main orchestrator for single-pipe and network-style calculations.
- `Pipe`, `Fitting`, `Pump`, `Nozzle`, `Equipment`, and `Vessel` provide the pipeline-domain objects.
- `PipelineNetwork` supports both graph-oriented modeling (nodes/edges) and composable series/parallel blocks.
- `standards.py`, `selection.py`, and `piping_costs.py` provide engineering lookup/support functions.

From a product perspective, this appears to be the module family closest to the project's current value proposition.

#### `processpi/equipment/`, `processpi/integration/`, and `processpi/streams/`

These directories provide the early shape of a broader process simulator:

- streams for material/energy transport,
- unit-operation base classes,
- heat exchanger subpackages,
- a flowsheet object that builds execution order from declared connections.

This layer is promising, but it is less integrated and less battle-tested than the unit/component/pipeline core.

#### `processpi_app/`

This is a GUI prototype built with Flet. It creates a flowsheet canvas, a sidebar/model library, and a simple draggable block interaction model. It currently reads as an experiment or future-facing prototype rather than a production-ready interface.

## 4. How the project works in practice

### Runtime/import behavior

Importing the package root eagerly imports all major submodules and may print an animated startup banner in TTY-like contexts. That is friendly for demos, but it increases import cost and can complicate non-interactive automation.

### Documentation and publishing flow

The repo is configured for MkDocs Material. Navigation is hand-maintained in `mkdocs.yml`, so new docs pages must be added there to appear on the published site. A GitHub Actions workflow publishes package builds on version tags. The same workflow builds distributions, runs `twine check`, and performs a smoke install before publishing.

### Testing posture

The repository includes tests for units, pipeline/network behavior, and heat-exchanger mechanical dispatch. However, test health is mixed:

- the heat-exchanger mechanical dispatch tests pass,
- some tests fail at collection because they import module/class names that no longer exist,
- some network tests fail because they expect APIs that are not present in the current `PipelineNetwork` implementation.

This indicates the codebase likely went through interface evolution without a full test-suite refresh.

## 5. Strengths worth preserving

1. **Clear domain focus.** The package has a recognizable niche: process/pipeline engineering in Python.
2. **Useful type system.** The unit classes make the public API expressive and approachable.
3. **Wide component coverage.** There is already a substantial fluid/component catalog.
4. **Pipeline feature depth.** Pipeline sizing, pressure-drop logic, fittings, standards, and network composition are meaningful differentiators.
5. **Documentation ambition.** The docs structure is much larger than many early-stage technical projects.
6. **Extensibility direction.** Dynamic component discovery and registry-based calculation dispatch make future expansion feasible.

## 6. Main risks and maintenance hotspots

### 6.1 Tests are out of sync with the implementation

This is the most immediate issue for maintainers.

Observed examples:

- `tests/test_variables.py` imports `processpi.units.kinetic_viscosity`, `flowrate`, `VolumetricFlowrate`, and `MassFlowrate`, but those module/class names are not present in the current `processpi/units/` tree.
- `tests/test_network.py` expects `PipelineNetwork.add_pipe`, `net.connections`, and `net.subnetworks`, but the current implementation exposes `add_edge`, `elements`, and other patterns instead.
- `tests/test_engine_network.py` also expects `PipelineEngine.add_pipe`, which is not available in the current engine.

Impact: contributors cannot trust the full test suite as a release gate yet.

### 6.2 Packaging metadata does not fully match repo usage

Two concrete mismatches stand out:

1. The release workflow runs `pip install .[dev]`, but `pyproject.toml` does not define a `dev` extra.
2. The Flet GUI prototype imports `flet`, but `flet` is not listed in project dependencies.

Impact: installs and CI smoke tests may behave differently from contributor expectations.

### 6.3 Generated artifacts are mixed into source control

The repository contains committed or generated build/runtime artifacts that should normally be ignored:

- many `__pycache__/` directories and `.pyc` files,
- a committed `site/` directory containing built docs,
- an effectively empty `.gitignore`.

Impact: noisy diffs, avoidable merge churn, and a higher risk of committing local-machine artifacts.

### 6.4 Serialization assumptions are inconsistent

`Pipe.to_dict()` and related code paths call `.to_dict()` on unit objects, but the shared `Variable` base class does not provide a `to_dict()` implementation. A simple direct call to `Pipe.to_dict()` currently raises an `AttributeError` because objects such as `Diameter` do not implement that serializer.

Impact: object export/reporting paths are fragile even when core numeric calculations work.

### 6.5 Import side effects and mixed API patterns increase maintenance cost

A few patterns make long-term maintenance harder:

- eager imports at package level,
- dynamic discovery in some places and explicit imports in others,
- property-like wrappers that also act like callables,
- a mix of graph APIs and series/parallel builder APIs in the pipeline layer.

These choices are workable, but they should be documented as intentional patterns or simplified over time.

## 7. Recommended maintainer priorities

### Priority 1: stabilize the development baseline

- Add a real `.gitignore` for Python caches, virtual environments, build outputs, and MkDocs output.
- Decide whether `site/` is source-controlled by design. If not, remove it from version control and regenerate in CI only.
- Remove stray local `__pycache__` artifacts before releases.

### Priority 2: re-establish truth in testing

- Choose the intended public API for units/pipelines/network construction.
- Update or replace stale tests so that they reflect the current API surface.
- Add at least one happy-path integration test per major pillar: units, component properties, single-pipe engine, network engine, and one flowsheet/equipment example.

### Priority 3: align packaging and runtime dependencies

- Either define a `[project.optional-dependencies].dev` section or change the workflow to a plain install plus explicit test/docs tools.
- If `processpi_app` is intended to be usable, add and document the Flet dependency path.
- Document optional vs core features clearly.

### Priority 4: harden core abstractions

- Add a consistent `to_dict()` / serialization contract to `Variable` or remove calls that assume it exists.
- Audit `Variable.__format__` assumptions against all subclasses.
- Reduce hidden side effects on import where possible.

### Priority 5: clarify product boundaries

Right now the repo spans:

- educational engineering utilities,
- a package for reusable correlations,
- pipeline simulation/design tooling,
- process-simulation scaffolding,
- a GUI prototype.

That breadth is exciting, but a short maintainer-facing roadmap should explicitly define which layers are:

- stable/public,
- experimental,
- aspirational.

## 8. Suggested mental model for new contributors

If someone new joins the project, the easiest onboarding path is:

1. **Start with units** to understand how values move through the system.
2. **Read components** to see how physical properties are modeled.
3. **Read calculations** to understand the individual engineering correlations.
4. **Read pipelines** to understand how those correlations become user-facing workflows.
5. **Treat equipment/integration/app as emerging layers** that are still converging.

This order mirrors the actual dependency direction in the codebase.

## 9. Quick operational checklist for the next maintainer

When picking up the repo, do these first:

- confirm which tests are authoritative,
- clean generated artifacts,
- align dependencies/workflows,
- verify the docs site still reflects the current public API,
- decide what is officially supported versus experimental.

## 10. Bottom-line assessment

ProcessPI already contains the hard part that many technical projects never reach: a meaningful engineering domain model with broad coverage and enough structure to grow. The next phase is not inventing more surface area; it is **consolidating** what is already here.

If a maintainer focuses on **test alignment, packaging hygiene, serialization consistency, and clearer stability boundaries**, the project can become much easier to contribute to and much safer to release.

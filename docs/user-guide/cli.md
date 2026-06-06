# Command Line Interface

## Installation

Install ProcessPI from a local checkout or distribution package:

```bash
pip install processpi
```

For repository development:

```bash
pip install -e .
```

The package entry point is configured as:

```text
processpi = processpi.cli:main
```

## Commands and options

### `processpi`

Prints a short CLI landing message.

```bash
processpi
```

Expected output:

```text
ProcessPI command line interface
Use 'processpi doctor' for an import check or 'processpi --help' for options.
```

### `processpi --help`

Displays CLI help, including available commands and options.

```bash
processpi --help
```

### `processpi --version`

Shows the installed package version.

```bash
processpi --version
```

### `processpi doctor`

Checks that ProcessPI imports and reports the installed version.

```bash
processpi doctor
```

Expected output:

```text
ProcessPI <version> is importable.
```

## Current CLI scope

The CLI is intentionally small. Engineering calculations are currently exposed through the Python API, not through calculation-specific terminal subcommands. Use the tutorials and API reference for programmatic workflows.

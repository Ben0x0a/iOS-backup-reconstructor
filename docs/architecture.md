# Architecture

## Layers

```mermaid
flowchart TD
    subgraph Shells
        M[main.py<br/>entry point]
        CLI[launcher/cli.py]
        GL[launcher/gui.py]
        UI[gui/interface.py<br/>PySide6 widgets + workers]
    end
    subgraph Engine
        R[core/reconstructor.py<br/>keybag, manifest, pipeline, traceability]
        MO[core/models.py<br/>FileRecord, ReconstructionResult]
    end
    subgraph Configuration
        S[config/settings.py<br/>tuneable constants]
        D[config/domain_maps/*.yaml<br/>domain to path mapping]
    end

    M --> CLI --> R
    M --> GL --> UI --> R
    R --> MO
    R --> S
    R --> D
    MO --> S
```

Dependencies flow inward. The shells hold no reconstruction logic; the engine
imports no UI code, so it is usable from a CLI, a GUI or a test with equal ease.

## Reconstruction pipeline

```mermaid
flowchart TD
    A[resolve_backup_dir<br/>validate the four required files] --> B[read Manifest / Info / Status plists]
    B --> C{IsEncrypted?}
    C -->|no| D[Manifest.db read directly]
    C -->|yes| E[Keybag.unlock<br/>derive passcode key]
    E --> F[decrypt_manifest_db<br/>to a temp directory]
    F --> D
    D --> G[iter_file_records<br/>join rows to blobs and output paths]
    G --> H[reconstruct into a STAGING directory]
    H --> I{any row failed?}
    I -->|yes, fail closed| J[write failure report<br/>promote nothing]
    I -->|no, or --continue-on-error| K[write traceability artefacts]
    K --> L[promote staging to the real output]
```

### Why staging

Reconstruction writes into a temporary directory beside the destination and
promotes it only once the run has succeeded and the traceability artefacts are
in place. This is what makes "fail closed" real: a failed run leaves no
half-populated output folder that could be mistaken for a complete one.

Because the rows are produced while writing to staging but must describe the
final location, `reconstruct_to_folder` takes a separate `report_root`. Without
it, every `output_path` in the manifest would name a temporary directory that
no longer exists by the time anyone reads it.

## Path safety

Domain and relative-path segments come from the backup and are therefore
untrusted. `sanitise_segment` replaces characters invalid on Windows, prefixes
reserved device names, and strips leading/trailing dots and spaces;
`safe_output_path` and `safe_join_path` drop `..` and absolute segments. Output
paths are always relative to the output root, so a crafted manifest cannot
write outside the folder the operator chose.

`claim_unique_path` then reserves each path, disambiguating genuine collisions
with a `~1` suffix while allowing a directory record to land on a directory
already created as the parent of an earlier file record.

## Module responsibilities

| Module | Responsibility |
| --- | --- |
| `main.py` | Dispatch between GUI and CLI |
| `launcher/cli.py` | CLI entry point |
| `launcher/gui.py` | GUI entry point, PySide6-absent handling |
| `gui/interface.py` | Widgets and background workers; no reconstruction logic |
| `core/reconstructor.py` | Keybag, manifest parsing, mapping, pipeline, traceability, CLI parser |
| `core/models.py` | `FileRecord`, `ReconstructionResult` |
| `config/settings.py` | Operator-tuneable constants |
| `config/domain_maps/` | Shipped domain mappings, loaded via `importlib.resources` |

## Testing

`tests/test_ios_backup_reconstruct.py` builds synthetic backups in temporary
directories — no real evidence data is committed to the repository. The suite
covers both output formats, both layouts, domain-map selection, failure and
`--continue-on-error` behaviour, dry runs, password redaction, and regression
tests for traceability paths, size handling and directory-record collisions.

```bash
uv run python -m unittest discover -s tests
```

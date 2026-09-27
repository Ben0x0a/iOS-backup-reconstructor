# Customise domain mapping

The `filesystem` layout maps backup domains to device-like paths using the YAML
maps in `config/domain_maps/`. Edit or extend them when a domain is mapped
wrongly, or when working with an iOS version the shipped map does not cover.

## Use your own map

```bash
uv run python main.py /path/to/backup /path/to/out --domain-map ./my-maps
```

`--domain-map` accepts a single YAML file or a directory of them. With a
directory, files are scanned in filename order and the first whose
`ios_versions` range covers the backup's `Product Version` is used. If the
version is unknown, the first valid map is used.

The chosen map's name, path and version range are recorded in the provenance
artefact, so a reconstruction can always be traced to the mapping that produced
it.

## File structure

See [formats/domain-maps.md](../formats/domain-maps.md) for the full schema.

## When not to map

If mapping accuracy matters more than filesystem realism — for example when the
output must show exactly what the backup asserts, with nothing inferred — use
the backup layout instead:

```bash
uv run python main.py /path/to/backup /path/to/out --layout backup
```

This writes `<domain>/<relativePath>` with no interpretation.

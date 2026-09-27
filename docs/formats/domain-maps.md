# Domain maps

YAML files mapping backup domains to filesystem-like paths, used by
`--layout filesystem`. The shipped maps live in `config/domain_maps/`.

## Schema

```yaml
name: iOS 13-18 domain mounts
ios_versions:
  min: "13.0"        # inclusive
  max: "18.999"      # inclusive

exact_domains:
  HomeDomain: private/var/mobile
  CameraRollDomain: private/var/mobile/Media

prefix_domains:
  AppDomain-: private/var/mobile/Containers/Data/Application/{suffix}
  AppDomainGroup-: private/var/mobile/Containers/Shared/AppGroup/{suffix}

unknown_domain_template: unknown_backup_domains/{domain}
```

| Key | Required | Meaning |
| --- | --- | --- |
| `name` | no | Human-readable label, recorded in provenance. Defaults to the filename stem |
| `ios_versions.min` / `.max` | no | Inclusive iOS version range this map covers |
| `exact_domains` | yes | Whole-domain matches |
| `prefix_domains` | yes | Prefix matches, with `{suffix}` and `{domain}` placeholders |
| `unknown_domain_template` | no | Fallback for unmatched domains |

## Resolution order

1. An exact match in `exact_domains`.
2. The first matching prefix in `prefix_domains`, with `{suffix}` replaced by
   the remainder of the domain and `{domain}` by the whole domain.
3. `unknown_domain_template`.

## Selecting a map from a directory

When `--domain-map` points at a directory, `.yaml` and `.yml` files are scanned
in filename order and the first whose `ios_versions` range contains the
backup's `Product Version` is used. Prefixing filenames with a number
(`01_ios9_12.yaml`, `02_ios13_18.yaml`) makes that order explicit.

If the backup's version cannot be determined, the first valid map is used.

## Rules for values

- Values are **relative** to the output root. Never begin one with `/` — the
  tool writes inside the chosen output folder or archive by design.
- Path segments are sanitised: characters invalid on Windows are replaced,
  reserved device names are prefixed, and `..` segments are dropped, so a
  hostile domain or relative path cannot escape the output root.

## Parser note

If [PyYAML](https://pyyaml.org/) is installed it is used. Otherwise a small
built-in parser handles the subset shown above: top-level scalars, one level of
nested `key: value` mappings, and `#` comments. Anything more complex requires
PyYAML.

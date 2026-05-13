# LabelSmith

[![PyPI version](https://img.shields.io/pypi/v/labelsmith.svg)](https://pypi.org/project/labelsmith/)
[![Python versions](https://img.shields.io/pypi/pyversions/labelsmith.svg)](https://pypi.org/project/labelsmith/)
[![License: MIT](https://img.shields.io/pypi/l/labelsmith.svg)](LICENSE)

> Forge clean, code-safe field names from messy labels.

LabelSmith takes the kind of strings that show up on real-world
spreadsheets, form captions, checksheets, and PDF tables —
`"Part Number"`, `"Op. #2 (mm)"`, `"AIAG/VDA Severity"` — and converts
them into deterministic identifiers your code can rely on.

It is intentionally small, dependency-free, and fully typed.

## Install

```bash
pip install labelsmith
```

LabelSmith runs on Python 3.10+ and has **no runtime dependencies**.

## Quick start

```python
from labelsmith import field_name, field_names, field_map

field_name("N Gage Length (MACH)")
# 'n_gage_length_mach'

field_name("AIAG/VDA Severity", style="pascal")
# 'AIAGVDASeverity'

field_names(["Part Number", "Part Number"])
# ['part_number', 'part_number_2']

field_map(["Part Number", "Part Number"])
# {'Part Number': 'part_number', 'Part Number (2)': 'part_number_2'}
```

## Styles

Four output styles, picked with the `style` keyword:

| Style    | Example input   | Output         |
| -------- | --------------- | -------------- |
| `snake`  | `"Part Number"` | `part_number`  |
| `camel`  | `"Part Number"` | `partNumber`   |
| `pascal` | `"Part Number"` | `PartNumber`   |
| `kebab`  | `"Part Number"` | `part-number`  |

```python
field_name("Part Number")                  # 'part_number'
field_name("Part Number", style="camel")   # 'partNumber'
field_name("Part Number", style="pascal")  # 'PartNumber'
field_name("Part Number", style="kebab")   # 'part-number'
```

Any other value for `style` raises `labelsmith.UnsupportedStyleError`
(a `ValueError` subclass).

## Acronym behavior

`snake` and `kebab` lowercase every token, so acronyms become plain
lowercase runs:

```python
field_name("AIAG/VDA Severity", style="snake")  # 'aiag_vda_severity'
field_name("AIAG/VDA Severity", style="kebab")  # 'aiag-vda-severity'
```

`camel` and `pascal` **preserve all-uppercase tokens as acronyms**, so
manufacturing/checksheet labels with industry-standard acronyms stay
recognizable:

```python
field_name("AIAG/VDA Severity", style="pascal")  # 'AIAGVDASeverity'
field_name("AIAG/VDA Severity", style="camel")   # 'aiagVDASeverity'
field_name("OK / NG", style="pascal")            # 'OKNG'
field_name("OK / NG", style="camel")             # 'okNG'
field_name("HTTPResponseCode", style="pascal")   # 'HTTPResponseCode'
```

camelCase always lowercases the first token, even when it's an acronym:

```python
field_name("AIAG", style="camel")   # 'aiag'
field_name("AIAG", style="pascal")  # 'AIAG'
```

## Duplicate handling

`field_names` guarantees unique output, with style-appropriate suffixes:

```python
field_names(["Part Number", "Part Number", "Part Number"])
# ['part_number', 'part_number_2', 'part_number_3']

field_names(["Part Number", "Part Number"], style="kebab")
# ['part-number', 'part-number-2']

field_names(["Part Number", "Part Number"], style="pascal")
# ['PartNumber', 'PartNumber2']
```

`field_map` keeps every original label as a dictionary key, using
`" (N)"` markers when the same label appears more than once:

```python
field_map(["Part Number", "Part Number", "Notes"])
# {
#     'Part Number': 'part_number',
#     'Part Number (2)': 'part_number_2',
#     'Notes': 'notes',
# }
```

## Reserved-word handling

Results that collide with Python reserved keywords get a trailing
underscore so they stay valid identifiers:

```python
field_name("class")  # 'class_'
field_name("for")    # 'for_'
```

You can supply your own reserved set — handy for ORM columns,
DataFrame headers, or framework-reserved attributes:

```python
field_name("id", reserved_words={"id", "type"})  # 'id_'
```

## Empty, unusable, and leading-digit fallbacks

LabelSmith never returns an unusable identifier. If the cleaned label is
empty, the `prefix` is rendered in the chosen style:

```python
field_name("")                       # 'field'
field_name("***")                    # 'field'
field_name("", style="pascal")       # 'Field'
field_name("", style="camel",  prefix="my field")  # 'myField'
field_name("", style="pascal", prefix="my field")  # 'MyField'
```

If the cleaned label would start with a digit, the prefix is woven in
front, in the chosen style:

```python
field_name("123 Part Number", style="snake")   # 'field_123_part_number'
field_name("123 Part Number", style="kebab")   # 'field-123-part-number'
field_name("123 Part Number", style="camel")   # 'field123PartNumber'
field_name("123 Part Number", style="pascal")  # 'Field123PartNumber'
```

If the `prefix` itself contains no usable alphanumeric content
(`""`, `"_"`, `"---"`, whitespace), the fallback is `"field"`:

```python
field_name("",    prefix="")        # 'field'
field_name("123", prefix="_")       # 'field_123'
field_name("***", prefix="---")     # 'field'
```

Opt out of digit prefixing with `allow_leading_digit=True`:

```python
field_name("1st Place", allow_leading_digit=True)  # '1_st_place'
```

## API surface

```python
labelsmith.field_name(label, *, style="snake", prefix="field",
                      allow_leading_digit=False, reserved_words=None) -> str

labelsmith.field_names(labels, *, style="snake", prefix="field",
                       allow_leading_digit=False, reserved_words=None) -> list[str]

labelsmith.field_map(labels, *, style="snake", prefix="field",
                     allow_leading_digit=False, reserved_words=None) -> dict[str, str]
```

LabelSmith ships with a `py.typed` marker so type checkers read the
inline annotations directly from the installed package.

## Why LabelSmith?

* **Intentionally small.** One module, three public functions.
* **Deterministic.** Same input, same output, every time. No
  heuristics that surprise you on edge cases.
* **No runtime dependencies.** Standard library only.
* **Typed.** Inline annotations + `py.typed`.
* **Useful where labels are messy:** spreadsheet headers, form
  captions, checksheet questions, workflow/schema bootstrapping, API
  field naming, database column generation.

## Not included (yet)

LabelSmith stays focused on naming. The following are deliberately out
of scope for v0.1.x:

* No Excel or PDF parsing.
* No AI or LLM calls.
* No database integration.
* No schema generation from labels.

These may land as separate companion packages in the future; LabelSmith
itself stays small.

## Development

```bash
pip install -e ".[dev]"
python -m pytest
python -m build
python -m twine check dist/*
```

The test suite uses only `pytest` (see `pyproject.toml` optional `dev`
extra). Builds use `hatchling`. All commands are run from the project
root.

## Links

* PyPI: <https://pypi.org/project/labelsmith/>
* GitHub: <https://github.com/Razormate88/labelsmith>
* Issues: <https://github.com/Razormate88/labelsmith/issues>
* Changelog: [CHANGELOG.md](./CHANGELOG.md)

## License

MIT — see [LICENSE](LICENSE).

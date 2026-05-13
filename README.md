# LabelSmith

> Turn messy human labels into clean, consistent, code-safe field names.

LabelSmith takes the kind of strings that show up on real-world spreadsheets,
form captions, checksheets, and PDF tables — `"Part Number"`, `"Op. #2 (mm)"`,
`"Café — naïve"` — and converts them into deterministic identifiers your code
can rely on.

It is intentionally small. No AI, no LLM calls, no Excel or PDF parsing — just
a focused, well-tested core for naming things.

## Install

```bash
pip install labelsmith
```

LabelSmith runs on Python 3.10+ and depends only on the standard library.

## Quick start

```python
from labelsmith import field_name, field_names, field_map

field_name("Part Number")
# 'part_number'

field_names(["Part Number", "Part Number", "Op. #2"])
# ['part_number', 'part_number_2', 'op_2']

field_map(["Part Number", "Part Number"])
# {'Part Number': 'part_number', 'Part Number (2)': 'part_number_2'}
```

## Styles

LabelSmith supports four output styles:

| Style    | Example output  |
| -------- | --------------- |
| `snake`  | `part_number`   |
| `camel`  | `partNumber`    |
| `pascal` | `PartNumber`    |
| `kebab`  | `part-number`   |

```python
field_name("Part Number")                     # 'part_number'
field_name("Part Number", style="camel")      # 'partNumber'
field_name("Part Number", style="pascal")     # 'PartNumber'
field_name("Part Number", style="kebab")      # 'part-number'
```

Any other value for `style` raises `ValueError`
(`labelsmith.UnsupportedStyleError`).

## Acronyms in camelCase and PascalCase

All-uppercase tokens are preserved as acronyms in `camel` and `pascal`
styles, so manufacturing/checksheet labels with industry-standard
acronyms stay recognizable:

```python
field_name("AIAG/VDA Severity", style="pascal")     # 'AIAGVDASeverity'
field_name("AIAG/VDA Severity", style="camel")      # 'aiagVDASeverity'
field_name("PFMEA Cause(s)", style="pascal")        # 'PFMEACauseS'
field_name("N Gage Length (MACH)", style="pascal")  # 'NGageLengthMACH'
field_name("HTTPResponseCode", style="pascal")      # 'HTTPResponseCode'
```

camelCase always lowercases the first token, even when it's an acronym:

```python
field_name("AIAG", style="camel")   # 'aiag'
field_name("AIAG", style="pascal")  # 'AIAG'
```

`snake` and `kebab` always lowercase every token, so acronym handling
doesn't apply there:

```python
field_name("AIAG/VDA Severity", style="snake")  # 'aiag_vda_severity'
field_name("AIAG/VDA Severity", style="kebab")  # 'aiag-vda-severity'
```

## Cleaning behavior

LabelSmith trims whitespace, decomposes Unicode to ASCII where reasonable,
splits on punctuation, symbols, and case boundaries, then re-joins using the
requested style.

```python
field_name("  Café — Naïve  ")        # 'cafe_naive'
field_name("Op. #2 (mm)")             # 'op_2_mm'
field_name("HTTPResponseCode")        # 'http_response_code'
field_name("first/second-third")      # 'first_second_third'
```

If a label normalizes to nothing, you get the `prefix` rendered in the
chosen style. The default prefix is `"field"`, so:

```python
field_name("")                       # 'field'
field_name("***")                    # 'field'
field_name("", prefix="col")         # 'col'
field_name("", style="pascal")       # 'Field'
field_name("", style="kebab", prefix="my field")   # 'my-field'
field_name("", style="camel", prefix="my field")   # 'myField'
```

If `prefix` itself is empty or contains no usable alphanumeric content
(`""`, `"_"`, `"---"`, whitespace), LabelSmith falls back to `"field"` so
you never get back an unusable identifier:

```python
field_name("", prefix="")        # 'field'
field_name("", prefix="_")       # 'field'
field_name("***", prefix="---")  # 'field'
```

## Labels that start with a digit

By default, names that would start with a digit get the configured prefix
woven in using the chosen style, so the result is a safe identifier *and*
stays consistent with the style you asked for:

```python
field_name("123 Part Number", style="snake")    # 'field_123_part_number'
field_name("123 Part Number", style="kebab")    # 'field-123-part-number'
field_name("123 Part Number", style="camel")    # 'field123PartNumber'
field_name("123 Part Number", style="pascal")   # 'Field123PartNumber'
```

Opt out with `allow_leading_digit=True`, or supply a different `prefix`:

```python
field_name("1st Place", allow_leading_digit=True)    # '1_st_place'
field_name("1st", prefix="col")                      # 'col_1_st'
field_name("1st", prefix="col", style="kebab")       # 'col-1-st'
```

If `prefix` is empty or contains no usable alphanumeric content
(`""`, `"_"`, `"---"`, whitespace), LabelSmith falls back to `"field"` so
the result is always a safe identifier:

```python
field_name("123 Part", prefix="")        # 'field_123_part'
field_name("123 Part", prefix="---", style="kebab")   # 'field-123-part'
```

Multi-token prefixes are tokenized and re-styled along with the label, so
the whole result stays consistent:

```python
field_name("123 Part Number", prefix="my field", style="camel")
# 'myField123PartNumber'
field_name("123 Part Number", prefix="my field", style="pascal")
# 'MyField123PartNumber'
```

## Reserved words

Names that collide with Python reserved keywords get a trailing underscore so
they remain usable as identifiers:

```python
field_name("class")     # 'class_'
field_name("for")       # 'for_'
```

You can supply your own reserved set — useful for ORM column names, dataframe
columns, or framework-reserved attributes:

```python
field_name("id", reserved_words={"id", "type"})
# 'id_'
```

## Duplicate handling

`field_names` guarantees unique outputs. Suffix style follows the chosen
naming style so the output stays consistent:

```python
field_names(["Part Number", "Part Number", "Part Number"])
# ['part_number', 'part_number_2', 'part_number_3']

field_names(["Part Number", "Part Number"], style="kebab")
# ['part-number', 'part-number-2']

field_names(["Part Number", "Part Number"], style="camel")
# ['partNumber', 'partNumber2']

field_names(["Part Number", "Part Number"], style="pascal")
# ['PartNumber', 'PartNumber2']
```

`field_map` returns a dictionary, so when the *original* label is repeated
the key is disambiguated with an occurrence marker — the values still follow
`field_names` uniqueness rules:

```python
field_map(["Part Number", "Part Number", "Notes"])
# {
#     'Part Number': 'part_number',
#     'Part Number (2)': 'part_number_2',
#     'Notes': 'notes',
# }
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

LabelSmith ships with a `py.typed` marker so type checkers will read the
inline annotations directly from the installed package.

## Development

```bash
pip install -e ".[dev]"
python -m pytest
```

## License

MIT — see [LICENSE](LICENSE).

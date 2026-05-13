# LabelSmith v0.1.1

LabelSmith forges clean, code-safe field names from messy labels,
spreadsheet headers, form captions, and checksheet questions — with
no runtime dependencies and full type hints.

## Install

```bash
pip install labelsmith
```

## Highlights

* **First public PyPI release** of LabelSmith.
* **Clean field names from messy labels** — trims whitespace,
  decomposes Unicode to ASCII, strips punctuation and symbols, splits
  on case boundaries, and re-joins in the requested style.
* **Four output styles:** `snake`, `camel`, `pascal`, `kebab`.
* **Acronym preservation** in `camel` and `pascal` (new in 0.1.1):
  manufacturing acronyms like `AIAG`, `VDA`, `PFMEA`, `MACH` stay
  recognizable.
  * `field_name("AIAG/VDA Severity", style="pascal")` → `"AIAGVDASeverity"`
  * `field_name("OK / NG", style="camel")` → `"okNG"`
  * `field_name("N Gage Length (MACH)", style="pascal")` → `"NGageLengthMACH"`
* **Duplicate handling**: `field_names` returns unique results with
  style-appropriate numeric suffixes; `field_map` keeps every
  original label as a dictionary key with `" (N)"` disambiguation.
* **Reserved-word handling**: Python keywords and user-supplied
  reserved sets get a trailing underscore so the output stays a valid
  identifier.
* **Safe fallback behavior**: empty, whitespace-only, or
  punctuation-only labels return a styled `prefix` (default
  `"field"`). Labels that would start with a digit get the prefix
  woven in front, in style. Unusable prefixes (`""`, `"_"`, `"---"`,
  whitespace) fall back to `"field"` so the result is always a valid
  identifier.

## What's new since 0.1.0

* `camel` / `pascal` now preserve all-uppercase tokens as acronyms.
  See `CHANGELOG.md` for the full diff.

## Links

* PyPI: <https://pypi.org/project/labelsmith/0.1.1/>
* Changelog: <https://github.com/Razormate88/labelsmith/blob/main/CHANGELOG.md>
* Source: <https://github.com/Razormate88/labelsmith>
* Issues: <https://github.com/Razormate88/labelsmith/issues>

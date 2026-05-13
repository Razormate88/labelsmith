# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-13

### Added

- Initial public release.
- `field_name(label, *, style, prefix, allow_leading_digit, reserved_words)`
  for converting a single messy label into a clean, code-safe field name.
- `field_names(labels, ...)` for batch conversion that guarantees unique
  output names by appending style-aware numeric suffixes.
- `field_map(labels, ...)` for building an `{original_label: field_name}`
  dictionary that preserves every input, even when original labels collide.
- Support for `snake`, `camel`, `pascal`, and `kebab` styles.
- Unicode-aware normalization that folds accents and full-width digits to
  plain ASCII before tokenizing.
- Avoidance of Python reserved keywords and user-supplied reserved words by
  appending a trailing underscore.
- Style-aware leading-digit prefixing: when a label would produce a name that
  starts with a digit, the configured `prefix` is woven into the result using
  the chosen style's separator and casing (`field_123_part_number`,
  `field-123-part-number`, `field123PartNumber`, `Field123PartNumber`).
- Safe fallback for unusable prefixes: if `prefix` tokenizes to nothing
  (e.g. `""`, `"_"`, `"---"`, whitespace), both fallback paths fall back to
  `"field"` so the returned name is always a valid identifier.
- Empty/unusable labels now flow through the same styling pipeline: the
  prefix is rendered in the selected style and checked against reserved
  words, so `field_name("")` returns `"field"` for snake/kebab/camel,
  `"Field"` for pascal, and `field_name("", prefix="class")` returns
  `"class_"`.
- Inline type hints and a `py.typed` marker for downstream type checkers.

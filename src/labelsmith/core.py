"""Core implementation of the :mod:`labelsmith` public API."""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable

from .exceptions import UnsupportedStyleError
from .reserved import is_python_keyword
from .styles import SUPPORTED_STYLES, duplicate_suffix, join_tokens

# Tokens are runs of letters or digits, with extra alternatives that split
# camelCase / PascalCase / ACRONYM boundaries inside an otherwise unbroken
# input string.
_TOKEN_PATTERN = re.compile(
    r"[A-Z]?[a-z]+"        # capitalized or lowercase word
    r"|[A-Z]+(?![a-z])"    # run of uppercase not followed by lowercase
    r"|[0-9]+"             # run of digits
)

# Safety net used when the caller's ``prefix`` tokenizes to nothing
# (e.g. "", "_", "---", "   ") but a prefix is still needed to avoid a
# leading-digit identifier.
_FALLBACK_PREFIX_TOKEN = "field"


def _normalize_unicode(label: str) -> str:
    """Decompose ``label`` to NFKD and drop non-ASCII characters."""
    decomposed = unicodedata.normalize("NFKD", label)
    return decomposed.encode("ascii", "ignore").decode("ascii")


def _tokenize(label: str) -> list[str]:
    """Split ``label`` into clean alphanumeric tokens."""
    return _TOKEN_PATTERN.findall(_normalize_unicode(label.strip()))


def _validate_style(style: str) -> None:
    if style not in SUPPORTED_STYLES:
        raise UnsupportedStyleError(
            f"Unsupported style {style!r}. "
            f"Expected one of: {sorted(SUPPORTED_STYLES)}."
        )


def _needs_mangling(name: str, reserved_words: set[str] | None) -> bool:
    if is_python_keyword(name):
        return True
    return reserved_words is not None and name in reserved_words


def _prefix_tokens(prefix: str) -> list[str]:
    """Return the tokens that stand in for ``prefix`` in fallback paths.

    Used both when the cleaned label is empty (the prefix becomes the
    whole return value) and when the cleaned label would otherwise start
    with a digit (the prefix is prepended). When ``prefix`` contains no
    usable alphanumeric content (e.g. ``""``, ``"_"``, ``"---"``, or
    whitespace), falls back to a single ``"field"`` token so the result
    is always a safe identifier.
    """
    tokens = _tokenize(prefix)
    return tokens if tokens else [_FALLBACK_PREFIX_TOKEN]


def field_name(
    label: str,
    *,
    style: str = "snake",
    prefix: str = "field",
    allow_leading_digit: bool = False,
    reserved_words: set[str] | None = None,
) -> str:
    """Convert a single messy label into a clean, code-safe field name.

    The label is whitespace-trimmed, NFKD-normalized to ASCII, split on any
    non-alphanumeric characters and case boundaries, and re-joined using the
    requested ``style``.

    Args:
        label: Raw label text.
        style: One of ``"snake"``, ``"camel"``, ``"pascal"``, or ``"kebab"``.
        prefix: Used to keep the return value a valid identifier when the
            cleaned label cannot stand on its own:

            * If ``label`` tokenizes to nothing (empty, whitespace, or
              pure punctuation), the *prefix* is returned in the chosen
              ``style``.
            * If the cleaned ``label`` would otherwise start with a digit
              and ``allow_leading_digit`` is ``False``, the prefix is
              woven in front, again in the chosen style.

            If ``prefix`` itself contains no usable alphanumeric content
            (e.g. ``""``, ``"_"``, ``"---"``, whitespace), LabelSmith
            falls back to ``"field"`` so the returned name is always a
            safe identifier. Defaults to ``"field"``.
        allow_leading_digit: When ``True``, a result that begins with a
            digit is returned as-is instead of being prefixed.
        reserved_words: Optional collection of names that must not appear as
            the final field name. If the generated name is in this set, a
            trailing underscore is appended.

    Returns:
        A deterministic field name in the requested style.

    Raises:
        UnsupportedStyleError: If ``style`` is not a recognized value.
    """
    _validate_style(style)

    tokens = _tokenize(label)
    if not tokens:
        tokens = _prefix_tokens(prefix)
    elif not allow_leading_digit and tokens[0][0].isdigit():
        tokens = _prefix_tokens(prefix) + tokens

    name = join_tokens(tokens, style)

    if _needs_mangling(name, reserved_words):
        name = f"{name}_"

    return name


def field_names(
    labels: list[str] | tuple[str, ...],
    *,
    style: str = "snake",
    prefix: str = "field",
    allow_leading_digit: bool = False,
    reserved_words: set[str] | None = None,
) -> list[str]:
    """Convert a sequence of labels into a list of unique field names.

    Each label is run through :func:`field_name`. When two labels would
    produce the same name, a numeric suffix is appended using the chosen
    style's natural separator (``part_number``, ``part_number_2`` for
    snake_case; ``partNumber``, ``partNumber2`` for camelCase, and so on).

    See :func:`field_name` for the keyword arguments.

    Returns:
        A list of field names with the same length as ``labels``, in order,
        with every element guaranteed unique within the list.
    """
    _validate_style(style)

    emitted: set[str] = set()
    counts: dict[str, int] = {}
    result: list[str] = []

    for label in labels:
        base = field_name(
            label,
            style=style,
            prefix=prefix,
            allow_leading_digit=allow_leading_digit,
            reserved_words=reserved_words,
        )
        counts[base] = counts.get(base, 0) + 1
        occurrence = counts[base]

        if occurrence == 1 and base not in emitted:
            emitted.add(base)
            result.append(base)
            continue

        candidate = duplicate_suffix(base, occurrence, style)
        while candidate in emitted:
            occurrence += 1
            counts[base] = occurrence
            candidate = duplicate_suffix(base, occurrence, style)
        emitted.add(candidate)
        result.append(candidate)

    return result


def field_map(
    labels: list[str] | tuple[str, ...],
    *,
    style: str = "snake",
    prefix: str = "field",
    allow_leading_digit: bool = False,
    reserved_words: set[str] | None = None,
) -> dict[str, str]:
    """Map each input label to a unique field name.

    When the same *original* label appears multiple times the dictionary key
    is disambiguated with an occurrence marker — the second time a label
    occurs the key becomes ``f"{label} (2)"``, then ``f"{label} (3)"``, and
    so on — so every input is preserved in the result. The generated values
    follow the same uniqueness rules as :func:`field_names`.

    See :func:`field_name` for the keyword arguments.

    Returns:
        A dictionary with one entry per input label, preserving order.
    """
    materialized: list[str] = list(_as_list(labels))
    generated = field_names(
        materialized,
        style=style,
        prefix=prefix,
        allow_leading_digit=allow_leading_digit,
        reserved_words=reserved_words,
    )

    seen: dict[str, int] = {}
    out: dict[str, str] = {}
    for label, name in zip(materialized, generated):
        seen[label] = seen.get(label, 0) + 1
        occurrence = seen[label]
        key = label if occurrence == 1 else f"{label} ({occurrence})"
        out[key] = name
    return out


def _as_list(labels: Iterable[str]) -> list[str]:
    """Materialize ``labels`` once so we can iterate over it twice safely."""
    if isinstance(labels, list):
        return labels
    return list(labels)

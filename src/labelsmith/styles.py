"""Style constants and token-joining helpers for :mod:`labelsmith.core`."""

from __future__ import annotations

SNAKE = "snake"
CAMEL = "camel"
PASCAL = "pascal"
KEBAB = "kebab"

SUPPORTED_STYLES: frozenset[str] = frozenset({SNAKE, CAMEL, PASCAL, KEBAB})


def join_tokens(tokens: list[str], style: str) -> str:
    """Join cleaned alphanumeric ``tokens`` into a single name.

    Tokens are expected to already be alphanumeric and non-empty; callers
    in :mod:`labelsmith.core` produce them via the tokenizer.
    """
    if not tokens:
        return ""
    if style == SNAKE:
        return "_".join(token.lower() for token in tokens)
    if style == KEBAB:
        return "-".join(token.lower() for token in tokens)
    if style == CAMEL:
        first, *rest = tokens
        return first.lower() + "".join(token.capitalize() for token in rest)
    if style == PASCAL:
        return "".join(token.capitalize() for token in tokens)
    raise ValueError(f"Unsupported style: {style!r}")


def duplicate_suffix(base: str, occurrence: int, style: str) -> str:
    """Return ``base`` with a style-appropriate uniqueness suffix.

    The first occurrence is the bare ``base``; subsequent occurrences add
    ``_2``/``-2`` (snake/kebab) or ``2`` (camel/pascal), matching the style's
    natural separator.
    """
    if style == SNAKE:
        return f"{base}_{occurrence}"
    if style == KEBAB:
        return f"{base}-{occurrence}"
    return f"{base}{occurrence}"

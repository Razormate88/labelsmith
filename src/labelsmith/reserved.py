"""Reserved-word helpers used by :mod:`labelsmith.core`."""

from __future__ import annotations

import keyword


def is_python_keyword(name: str) -> bool:
    """Return ``True`` if ``name`` is a Python reserved keyword.

    Soft keywords such as ``match`` and ``case`` are intentionally excluded
    because they remain valid identifiers in regular code and mangling them
    would surprise users.
    """
    return keyword.iskeyword(name)

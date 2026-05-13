"""LabelSmith: clean, consistent, code-safe field names from messy labels.

Public API:

* :func:`field_name`  - convert a single label.
* :func:`field_names` - convert a sequence of labels with uniqueness.
* :func:`field_map`   - map original labels to unique field names.
"""

from __future__ import annotations

from .core import field_map, field_name, field_names
from .exceptions import LabelSmithError, UnsupportedStyleError

__all__ = [
    "LabelSmithError",
    "UnsupportedStyleError",
    "field_map",
    "field_name",
    "field_names",
]

__version__ = "0.1.0"

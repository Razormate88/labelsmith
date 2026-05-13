"""Exceptions raised by :mod:`labelsmith`."""

from __future__ import annotations


class LabelSmithError(Exception):
    """Base class for all :mod:`labelsmith` exceptions."""


class UnsupportedStyleError(LabelSmithError, ValueError):
    """Raised when an unrecognized ``style`` value is requested.

    Subclasses :class:`ValueError` so callers can keep using a plain
    ``except ValueError`` while still being able to catch the more specific
    type when they want to.
    """

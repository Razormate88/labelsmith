"""Tests for Python keyword handling and custom reserved-word avoidance."""

from __future__ import annotations

import keyword

import pytest

from labelsmith import field_name, field_names


PYTHON_KEYWORDS = sorted(keyword.kwlist)


class TestPythonKeywords:
    @pytest.mark.parametrize("kw", ["class", "for", "while", "return", "lambda"])
    def test_common_keywords_are_mangled(self, kw: str) -> None:
        assert field_name(kw) == f"{kw}_"

    def test_every_python_keyword_is_mangled_in_snake(self) -> None:
        for kw in PYTHON_KEYWORDS:
            # Many keywords have only lowercase ASCII letters and so survive
            # snake_case unchanged.
            result = field_name(kw)
            if keyword.iskeyword(result):
                pytest.fail(f"keyword {kw!r} was not mangled (got {result!r})")

    def test_keyword_followed_by_other_text_is_not_mangled(self) -> None:
        assert field_name("Pass Through") == "pass_through"

    def test_pascal_keeps_capitalized_keyword_and_mangles(self) -> None:
        # In pascal style, "true" tokens capitalize to "True", which is a
        # Python keyword and so must be mangled.
        assert field_name("true", style="pascal") == "True_"
        assert field_name("none", style="pascal") == "None_"

    def test_soft_keywords_are_not_mangled(self) -> None:
        # ``match`` and ``case`` are soft keywords — valid identifiers — and
        # therefore should pass through unchanged.
        assert field_name("match") == "match"
        assert field_name("case") == "case"


class TestCustomReservedWords:
    def test_custom_reserved_appends_underscore(self) -> None:
        assert field_name("id", reserved_words={"id"}) == "id_"

    def test_custom_reserved_after_styling(self) -> None:
        assert (
            field_name("Reserved Name", reserved_words={"reserved_name"})
            == "reserved_name_"
        )

    def test_unrelated_names_pass_through(self) -> None:
        assert field_name("Notes", reserved_words={"id", "type"}) == "notes"

    def test_custom_reserved_for_each_style(self) -> None:
        reserved = {"id", "Id", "ID"}
        assert field_name("Id", style="snake", reserved_words=reserved) == "id_"
        assert field_name("Id", style="camel", reserved_words=reserved) == "id_"
        assert field_name("Id", style="pascal", reserved_words=reserved) == "Id_"
        assert field_name("Id", style="kebab", reserved_words=reserved) == "id_"

    def test_python_keyword_takes_precedence(self) -> None:
        # Whether a name is a Python keyword OR in the custom set, the
        # outcome is the same: append a single underscore. We just verify
        # the suffix isn't doubled when both conditions are true.
        assert field_name("class", reserved_words={"class"}) == "class_"

    def test_reserved_words_propagate_through_field_names(self) -> None:
        assert field_names(
            ["class", "for", "Notes"]
        ) == ["class_", "for_", "notes"]

    def test_custom_reserved_words_propagate_through_field_names(self) -> None:
        assert field_names(
            ["id", "type", "Notes"], reserved_words={"id", "type"}
        ) == ["id_", "type_", "notes"]

"""Tests for ``labelsmith.field_names``."""

from __future__ import annotations

import pytest

from labelsmith import UnsupportedStyleError, field_names


class TestBasicBatch:
    def test_unique_inputs_are_unchanged(self) -> None:
        assert field_names(["Part Number", "Notes"]) == ["part_number", "notes"]

    def test_empty_input_returns_empty_list(self) -> None:
        assert field_names([]) == []

    def test_accepts_tuple_input(self) -> None:
        assert field_names(("Part Number", "Notes")) == ["part_number", "notes"]


class TestDuplicateHandling:
    def test_two_duplicates_snake(self) -> None:
        assert field_names(["Part Number", "Part Number"]) == [
            "part_number",
            "part_number_2",
        ]

    def test_three_duplicates_snake(self) -> None:
        assert field_names(["Part Number", "Part Number", "Part Number"]) == [
            "part_number",
            "part_number_2",
            "part_number_3",
        ]

    def test_duplicates_kebab(self) -> None:
        assert field_names(
            ["Part Number", "Part Number", "Part Number"], style="kebab"
        ) == ["part-number", "part-number-2", "part-number-3"]

    def test_duplicates_camel(self) -> None:
        assert field_names(
            ["Part Number", "Part Number", "Part Number"], style="camel"
        ) == ["partNumber", "partNumber2", "partNumber3"]

    def test_duplicates_pascal(self) -> None:
        assert field_names(
            ["Part Number", "Part Number", "Part Number"], style="pascal"
        ) == ["PartNumber", "PartNumber2", "PartNumber3"]

    def test_only_duplicates_get_suffixes(self) -> None:
        assert field_names(
            ["Part Number", "Notes", "Part Number", "Notes"]
        ) == ["part_number", "notes", "part_number_2", "notes_2"]

    def test_preexisting_suffix_does_not_collide(self) -> None:
        # If an input already maps to "part_number_2", a later duplicate of
        # "Part Number" must skip the taken suffix instead of overwriting it.
        result = field_names(["Part Number", "Part Number 2", "Part Number"])
        assert result == ["part_number", "part_number_2", "part_number_3"]
        assert len(set(result)) == len(result)


class TestStylesHonored:
    def test_snake_style(self) -> None:
        assert field_names(["Part Number"]) == ["part_number"]

    def test_camel_style(self) -> None:
        assert field_names(["Part Number"], style="camel") == ["partNumber"]

    def test_pascal_style(self) -> None:
        assert field_names(["Part Number"], style="pascal") == ["PartNumber"]

    def test_kebab_style(self) -> None:
        assert field_names(["Part Number"], style="kebab") == ["part-number"]


class TestPassthroughOptions:
    def test_reserved_words_apply_per_item(self) -> None:
        assert field_names(["class", "Notes"]) == ["class_", "notes"]

    def test_allow_leading_digit_propagates(self) -> None:
        assert field_names(["1st", "2nd"], allow_leading_digit=True) == [
            "1_st",
            "2_nd",
        ]

    def test_prefix_propagates_to_empty_labels(self) -> None:
        assert field_names(["", "***"], prefix="col") == ["col", "col_2"]

    def test_unusable_prefix_falls_back_to_field(self) -> None:
        # With an unusable prefix every empty label resolves to "field",
        # and dedup applies normally.
        assert field_names(["", "***", "---"], prefix="") == [
            "field",
            "field_2",
            "field_3",
        ]

    def test_styled_fallback_dedup_pascal(self) -> None:
        assert field_names(["", ""], style="pascal", prefix="my field") == [
            "MyField",
            "MyField2",
        ]


class TestErrors:
    def test_invalid_style_raises(self) -> None:
        with pytest.raises(UnsupportedStyleError):
            field_names(["Part Number"], style="screaming_snake")

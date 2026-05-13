"""Tests for ``labelsmith.field_map``."""

from __future__ import annotations

import pytest

from labelsmith import UnsupportedStyleError, field_map


class TestBasicMapping:
    def test_simple_mapping(self) -> None:
        assert field_map(["Part Number", "Notes"]) == {
            "Part Number": "part_number",
            "Notes": "notes",
        }

    def test_empty_input_returns_empty_dict(self) -> None:
        assert field_map([]) == {}

    def test_accepts_tuple_input(self) -> None:
        assert field_map(("Part Number",)) == {"Part Number": "part_number"}

    def test_preserves_input_order(self) -> None:
        result = field_map(["B Label", "A Label", "C Label"])
        assert list(result.keys()) == ["B Label", "A Label", "C Label"]
        assert list(result.values()) == ["b_label", "a_label", "c_label"]


class TestDuplicateOriginals:
    def test_two_identical_originals(self) -> None:
        assert field_map(["Part Number", "Part Number"]) == {
            "Part Number": "part_number",
            "Part Number (2)": "part_number_2",
        }

    def test_three_identical_originals(self) -> None:
        assert field_map(["Part Number", "Part Number", "Part Number"]) == {
            "Part Number": "part_number",
            "Part Number (2)": "part_number_2",
            "Part Number (3)": "part_number_3",
        }

    def test_mixed_duplicates_preserve_unique_originals(self) -> None:
        assert field_map(["Part Number", "Notes", "Part Number"]) == {
            "Part Number": "part_number",
            "Notes": "notes",
            "Part Number (2)": "part_number_2",
        }

    def test_duplicate_originals_kebab(self) -> None:
        assert field_map(["Part Number", "Part Number"], style="kebab") == {
            "Part Number": "part-number",
            "Part Number (2)": "part-number-2",
        }

    def test_duplicate_originals_camel(self) -> None:
        assert field_map(["Part Number", "Part Number"], style="camel") == {
            "Part Number": "partNumber",
            "Part Number (2)": "partNumber2",
        }


class TestPassthroughOptions:
    def test_reserved_word_mangled_in_value(self) -> None:
        assert field_map(["class"]) == {"class": "class_"}

    def test_allow_leading_digit(self) -> None:
        assert field_map(["1st"], allow_leading_digit=True) == {"1st": "1_st"}


class TestErrors:
    def test_invalid_style_raises(self) -> None:
        with pytest.raises(UnsupportedStyleError):
            field_map(["Part Number"], style="upper")

"""Tests for the four supported styles."""

from __future__ import annotations

import pytest

from labelsmith import UnsupportedStyleError, field_name, field_names


class TestSnake:
    def test_two_words(self) -> None:
        assert field_name("Part Number", style="snake") == "part_number"

    def test_default_is_snake(self) -> None:
        assert field_name("Part Number") == field_name("Part Number", style="snake")

    def test_uniqueness_suffix(self) -> None:
        assert field_names(["Foo", "Foo"], style="snake") == ["foo", "foo_2"]

    def test_leading_digit_prefix(self) -> None:
        assert (
            field_name("123 Part Number", style="snake")
            == "field_123_part_number"
        )

    def test_leading_digit_duplicates(self) -> None:
        assert field_names(
            ["123 Part Number", "123 Part Number"], style="snake"
        ) == ["field_123_part_number", "field_123_part_number_2"]


class TestCamel:
    def test_two_words(self) -> None:
        assert field_name("Part Number", style="camel") == "partNumber"

    def test_first_token_lowercased(self) -> None:
        assert field_name("PART NUMBER", style="camel") == "partNumber"

    def test_three_tokens(self) -> None:
        assert field_name("http response code", style="camel") == "httpResponseCode"

    def test_uniqueness_suffix_has_no_separator(self) -> None:
        assert field_names(["Foo", "Foo"], style="camel") == ["foo", "foo2"]

    def test_leading_digit_prefix(self) -> None:
        assert (
            field_name("123 Part Number", style="camel")
            == "field123PartNumber"
        )

    def test_leading_digit_duplicates(self) -> None:
        assert field_names(
            ["123 Part Number", "123 Part Number"], style="camel"
        ) == ["field123PartNumber", "field123PartNumber2"]


class TestPascal:
    def test_two_words(self) -> None:
        assert field_name("Part Number", style="pascal") == "PartNumber"

    def test_lowercase_input(self) -> None:
        assert field_name("part number", style="pascal") == "PartNumber"

    def test_uniqueness_suffix_has_no_separator(self) -> None:
        assert field_names(["Foo", "Foo"], style="pascal") == ["Foo", "Foo2"]

    def test_leading_digit_prefix(self) -> None:
        assert (
            field_name("123 Part Number", style="pascal")
            == "Field123PartNumber"
        )

    def test_leading_digit_duplicates(self) -> None:
        assert field_names(
            ["123 Part Number", "123 Part Number"], style="pascal"
        ) == ["Field123PartNumber", "Field123PartNumber2"]


class TestKebab:
    def test_two_words(self) -> None:
        assert field_name("Part Number", style="kebab") == "part-number"

    def test_three_tokens(self) -> None:
        assert field_name("http response code", style="kebab") == "http-response-code"

    def test_uniqueness_suffix_uses_dash(self) -> None:
        assert field_names(["Foo", "Foo"], style="kebab") == ["foo", "foo-2"]

    def test_leading_digit_prefix(self) -> None:
        assert (
            field_name("123 Part Number", style="kebab")
            == "field-123-part-number"
        )

    def test_leading_digit_duplicates(self) -> None:
        assert field_names(
            ["123 Part Number", "123 Part Number"], style="kebab"
        ) == ["field-123-part-number", "field-123-part-number-2"]


class TestUnsupportedStyle:
    @pytest.mark.parametrize(
        "style",
        ["screaming_snake", "Snake", "SNAKE", "", "upper", "lower"],
    )
    def test_unsupported_style_raises(self, style: str) -> None:
        with pytest.raises(UnsupportedStyleError):
            field_name("Part Number", style=style)

    def test_error_message_mentions_supported_styles(self) -> None:
        with pytest.raises(UnsupportedStyleError) as info:
            field_name("Part Number", style="bogus")
        message = str(info.value)
        for style in ("snake", "camel", "pascal", "kebab"):
            assert style in message

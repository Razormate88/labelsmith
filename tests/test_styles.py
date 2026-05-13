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
        # First token is always lowercased in camel. Subsequent tokens
        # follow the acronym-aware rule, so ``NUMBER`` (all-uppercase)
        # stays uppercase as an acronym.
        assert field_name("PART NUMBER", style="camel") == "partNUMBER"

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


class TestAcronymPreservation:
    """All-uppercase tokens stay as-is in camel/pascal style joins."""

    @pytest.mark.parametrize(
        ("label", "expected"),
        [
            ("AIAG/VDA Severity", "AIAGVDASeverity"),
            ("OK / NG", "OKNG"),
            ("Chart Method (X & MR)", "ChartMethodXMR"),
            ("PFMEA Cause(s)", "PFMEACauseS"),
            ("N Gage Length (MACH)", "NGageLengthMACH"),
        ],
    )
    def test_pascal_preserves_acronyms(self, label: str, expected: str) -> None:
        assert field_name(label, style="pascal") == expected

    @pytest.mark.parametrize(
        ("label", "expected"),
        [
            ("AIAG/VDA Severity", "aiagVDASeverity"),
            ("OK / NG", "okNG"),
            ("Chart Method (X & MR)", "chartMethodXMR"),
            ("PFMEA Cause(s)", "pfmeaCauseS"),
            ("N Gage Length (MACH)", "nGageLengthMACH"),
        ],
    )
    def test_camel_preserves_acronyms(self, label: str, expected: str) -> None:
        assert field_name(label, style="camel") == expected

    @pytest.mark.parametrize(
        ("label", "expected"),
        [
            ("AIAG/VDA Severity", "aiag_vda_severity"),
            ("OK / NG", "ok_ng"),
            ("Chart Method (X & MR)", "chart_method_x_mr"),
            ("PFMEA Cause(s)", "pfmea_cause_s"),
            ("N Gage Length (MACH)", "n_gage_length_mach"),
        ],
    )
    def test_snake_still_lowercases(self, label: str, expected: str) -> None:
        assert field_name(label, style="snake") == expected

    @pytest.mark.parametrize(
        ("label", "expected"),
        [
            ("AIAG/VDA Severity", "aiag-vda-severity"),
            ("OK / NG", "ok-ng"),
            ("Chart Method (X & MR)", "chart-method-x-mr"),
            ("PFMEA Cause(s)", "pfmea-cause-s"),
            ("N Gage Length (MACH)", "n-gage-length-mach"),
        ],
    )
    def test_kebab_still_lowercases(self, label: str, expected: str) -> None:
        assert field_name(label, style="kebab") == expected

    def test_camel_first_acronym_lowercased(self) -> None:
        # camelCase always lowercases the first token, even an acronym.
        assert field_name("AIAG", style="camel") == "aiag"
        assert field_name("OK", style="camel") == "ok"

    def test_pascal_first_acronym_preserved(self) -> None:
        # Pascal keeps the first token uppercase when it's an acronym.
        assert field_name("AIAG", style="pascal") == "AIAG"
        assert field_name("OK", style="pascal") == "OK"

    def test_http_response_code_pascal(self) -> None:
        # Tokens ["HTTP", "Response", "Code"]: HTTP stays uppercase.
        assert field_name("HTTPResponseCode", style="pascal") == "HTTPResponseCode"

    def test_http_response_code_camel(self) -> None:
        # First token "HTTP" is lowercased per camel rule; mixed-case
        # later tokens flow through capitalize.
        assert field_name("HTTPResponseCode", style="camel") == "httpResponseCode"

    def test_digit_tokens_are_unaffected(self) -> None:
        # Digits aren't capitalized either way; acronym preservation does
        # not interfere with the leading-digit prefix branch.
        assert field_name("123 ABC", style="pascal") == "Field123ABC"
        assert field_name("123 ABC", style="camel") == "field123ABC"

    def test_mixed_case_tokens_unchanged(self) -> None:
        # Tokens like "Cause" or "Severity" are not acronyms and keep
        # going through capitalize().
        assert field_name("Cause Severity", style="pascal") == "CauseSeverity"
        assert field_name("Cause Severity", style="camel") == "causeSeverity"

    def test_uniqueness_suffix_with_acronyms_pascal(self) -> None:
        assert field_names(["AIAG", "AIAG"], style="pascal") == ["AIAG", "AIAG2"]

    def test_uniqueness_suffix_with_acronyms_camel(self) -> None:
        assert field_names(["AIAG", "AIAG"], style="camel") == ["aiag", "aiag2"]

    def test_leading_digit_with_acronym_label_pascal(self) -> None:
        # Leading-digit prefix path: ["field", "123", "AIAG"] -> "Field123AIAG"
        assert field_name("123 AIAG", style="pascal") == "Field123AIAG"

    def test_leading_digit_with_acronym_label_camel(self) -> None:
        assert field_name("123 AIAG", style="camel") == "field123AIAG"


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

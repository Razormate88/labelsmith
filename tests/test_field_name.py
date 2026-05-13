"""Tests for ``labelsmith.field_name``."""

from __future__ import annotations

import pytest

from labelsmith import UnsupportedStyleError, field_name


class TestBasicConversion:
    def test_simple_two_words_to_snake(self) -> None:
        assert field_name("Part Number") == "part_number"

    def test_single_word_lowercased(self) -> None:
        assert field_name("Notes") == "notes"

    def test_already_clean_input(self) -> None:
        assert field_name("part_number") == "part_number"


class TestWhitespace:
    def test_trims_surrounding_whitespace(self) -> None:
        assert field_name("  Part Number  ") == "part_number"

    def test_collapses_repeated_whitespace(self) -> None:
        assert field_name("part   number") == "part_number"

    def test_mixed_whitespace_kinds(self) -> None:
        assert field_name("part\t \nnumber") == "part_number"


class TestPunctuationAndSymbols:
    def test_removes_punctuation(self) -> None:
        assert field_name("Part #1!") == "part_1"

    def test_handles_parentheses(self) -> None:
        assert field_name("Part (Number)") == "part_number"

    def test_handles_brackets(self) -> None:
        assert field_name("Part [Number]") == "part_number"

    def test_handles_slash_separator(self) -> None:
        assert field_name("part/number") == "part_number"

    def test_handles_dash_separator(self) -> None:
        assert field_name("part-number") == "part_number"

    def test_handles_underscore_separator(self) -> None:
        assert field_name("part_number") == "part_number"

    def test_handles_dot_separator(self) -> None:
        assert field_name("Order.Number") == "order_number"

    def test_strips_symbols(self) -> None:
        assert field_name("Op. #2 (mm)") == "op_2_mm"


class TestUnicode:
    def test_strips_accents(self) -> None:
        assert field_name("Café Name") == "cafe_name"

    def test_handles_umlauts(self) -> None:
        assert field_name("ümläut") == "umlaut"

    def test_em_dash_acts_as_separator(self) -> None:
        assert field_name("Café — Naïve") == "cafe_naive"

    def test_full_width_digits_normalize_to_ascii(self) -> None:
        # NFKD decomposes full-width digits to ASCII digits.
        assert field_name("Part １") == "part_1"

    def test_non_latin_script_yields_prefix(self) -> None:
        # Non-decomposable characters drop out, leaving an empty result.
        assert field_name("你好") == "field"


class TestEmptyOrUnusable:
    def test_empty_string_returns_default_prefix(self) -> None:
        assert field_name("") == "field"

    def test_whitespace_only_returns_prefix(self) -> None:
        assert field_name("   ") == "field"

    def test_punctuation_only_returns_prefix(self) -> None:
        assert field_name("!!!") == "field"
        assert field_name("###") == "field"

    def test_custom_prefix_used_when_empty(self) -> None:
        assert field_name("", prefix="col") == "col"


class TestEmptyFallbackUnusablePrefix:
    """An empty label paired with an unusable prefix falls back to ``"field"``."""

    @pytest.mark.parametrize(
        "label", ["", "   ", "###", "***", "---", "\t\n", "你好"],
    )
    @pytest.mark.parametrize(
        "prefix", ["", "_", "---", "   ", "\t\n", "###", "()"],
    )
    def test_snake_fallback(self, label: str, prefix: str) -> None:
        assert field_name(label, style="snake", prefix=prefix) == "field"

    def test_kebab_fallback(self) -> None:
        assert field_name("", style="kebab", prefix="_") == "field"

    def test_camel_fallback(self) -> None:
        assert field_name("", style="camel", prefix="---") == "field"

    def test_pascal_fallback(self) -> None:
        # Pascal still capitalizes the fallback token.
        assert field_name("", style="pascal", prefix="") == "Field"


class TestEmptyFallbackUsablePrefix:
    """An empty label with a usable prefix returns that prefix in style."""

    def test_snake_single_token(self) -> None:
        assert field_name("", style="snake", prefix="col") == "col"

    def test_snake_multi_token(self) -> None:
        assert field_name("", style="snake", prefix="my field") == "my_field"

    def test_kebab_multi_token(self) -> None:
        assert field_name("", style="kebab", prefix="my field") == "my-field"

    def test_camel_multi_token(self) -> None:
        assert field_name("", style="camel", prefix="my field") == "myField"

    def test_pascal_multi_token(self) -> None:
        assert field_name("", style="pascal", prefix="my field") == "MyField"

    def test_pascal_capitalizes_default_prefix(self) -> None:
        assert field_name("", style="pascal") == "Field"

    def test_kebab_default_prefix(self) -> None:
        assert field_name("", style="kebab") == "field"

    def test_camel_default_prefix(self) -> None:
        assert field_name("", style="camel") == "field"

    def test_prefix_punctuation_is_cleaned(self) -> None:
        assert field_name("", style="snake", prefix="(col)") == "col"

    def test_prefix_unicode_normalized(self) -> None:
        assert field_name("", style="snake", prefix="café") == "cafe"

    def test_non_latin_label_uses_styled_prefix(self) -> None:
        # The label drops out under NFKD->ASCII, then the styled prefix
        # carries the result.
        assert field_name("你好", style="pascal", prefix="my field") == "MyField"


class TestEmptyFallbackReservedWords:
    """Reserved-word handling applies to the styled fallback too."""

    def test_python_keyword_prefix_is_mangled(self) -> None:
        assert field_name("", prefix="class") == "class_"

    def test_python_keyword_after_styling(self) -> None:
        # Python keywords are case-sensitive: ``If`` is *not* a keyword,
        # but ``True`` is — pascal-casing ``"true"`` yields ``"True"``,
        # which still trips the keyword check.
        assert field_name("", style="pascal", prefix="true") == "True_"

    def test_custom_reserved_word_mangled(self) -> None:
        assert (
            field_name("", prefix="col", reserved_words={"col"}) == "col_"
        )

    def test_keyword_taking_precedence(self) -> None:
        # Even if reserved_words is provided, the Python-keyword check
        # already triggers mangling; a single trailing "_" is appended.
        assert (
            field_name("", prefix="class", reserved_words={"class_"})
            == "class_"
        )

    def test_mangling_runs_once_only(self) -> None:
        # Deliberate: the post-mangle name ("class_") is not re-checked
        # against the reserved set, so no looping or doubled suffix even
        # when the user's reserved set names the mangled form. Deterministic.
        result = field_name(
            "", prefix="class", reserved_words={"class_"}
        )
        assert result == "class_"
        assert not result.endswith("__")


class TestLeadingDigit:
    def test_default_prepends_prefix_and_underscore(self) -> None:
        assert field_name("1st Place") == "field_1_st_place"

    def test_pure_digit_label_uses_prefix(self) -> None:
        assert field_name("123") == "field_123"

    def test_allow_leading_digit_keeps_digit(self) -> None:
        assert field_name("1st Place", allow_leading_digit=True) == "1_st_place"

    def test_allow_leading_digit_with_pure_digits(self) -> None:
        assert field_name("123", allow_leading_digit=True) == "123"

    def test_custom_prefix_for_leading_digit(self) -> None:
        assert field_name("1st", prefix="col") == "col_1_st"


class TestLeadingDigitStyleAware:
    """The prefix is woven into the chosen style, not hard-coded with ``_``."""

    def test_snake(self) -> None:
        assert field_name("123 Part Number", style="snake") == "field_123_part_number"

    def test_kebab(self) -> None:
        assert field_name("123 Part Number", style="kebab") == "field-123-part-number"

    def test_camel(self) -> None:
        assert field_name("123 Part Number", style="camel") == "field123PartNumber"

    def test_pascal(self) -> None:
        assert field_name("123 Part Number", style="pascal") == "Field123PartNumber"

    def test_kebab_no_longer_mixes_underscore_and_dash(self) -> None:
        # Regression: previously emitted "field_1-st"; should be all dashes.
        assert field_name("1st", style="kebab") == "field-1-st"

    def test_camel_normalizes_prefix_to_lowercase(self) -> None:
        # ``prefix`` is treated as a token; camelCase lowercases the first.
        assert field_name("1st", style="camel", prefix="Col") == "col1St"

    def test_pascal_capitalizes_prefix(self) -> None:
        # Pascal capitalizes every token, including the prefix.
        assert field_name("1st", style="pascal", prefix="col") == "Col1St"

    def test_custom_prefix_kebab(self) -> None:
        assert (
            field_name("123 Part", style="kebab", prefix="col")
            == "col-123-part"
        )

    def test_allow_leading_digit_overrides_prefix(self) -> None:
        # No prefix is woven in when the caller has opted in to digit starts.
        assert (
            field_name("123 Part", style="pascal", allow_leading_digit=True)
            == "123Part"
        )


class TestLeadingDigitPrefixFallback:
    """Prefixes that tokenize to nothing fall back to ``"field"``."""

    @pytest.mark.parametrize(
        "prefix",
        ["", "_", "---", "   ", "\t\n", "###", "()"],
    )
    def test_snake_fallback(self, prefix: str) -> None:
        assert (
            field_name("123 Part Number", style="snake", prefix=prefix)
            == "field_123_part_number"
        )

    @pytest.mark.parametrize(
        "prefix",
        ["", "_", "---", "   ", "\t\n", "###", "()"],
    )
    def test_kebab_fallback(self, prefix: str) -> None:
        assert (
            field_name("123 Part Number", style="kebab", prefix=prefix)
            == "field-123-part-number"
        )

    @pytest.mark.parametrize(
        "prefix",
        ["", "_", "---", "   ", "\t\n", "###", "()"],
    )
    def test_camel_fallback(self, prefix: str) -> None:
        assert (
            field_name("123 Part Number", style="camel", prefix=prefix)
            == "field123PartNumber"
        )

    @pytest.mark.parametrize(
        "prefix",
        ["", "_", "---", "   ", "\t\n", "###", "()"],
    )
    def test_pascal_fallback(self, prefix: str) -> None:
        assert (
            field_name("123 Part Number", style="pascal", prefix=prefix)
            == "Field123PartNumber"
        )

    def test_fallback_not_applied_when_label_is_safe(self) -> None:
        # The fallback is only triggered by the leading-digit branch.
        # A non-digit label simply returns the prefix verbatim when empty.
        assert field_name("Part Number", style="snake", prefix="") == "part_number"

    def test_fallback_not_applied_when_allow_leading_digit(self) -> None:
        assert (
            field_name(
                "123 Part Number",
                style="snake",
                prefix="",
                allow_leading_digit=True,
            )
            == "123_part_number"
        )

    def test_fallback_when_prefix_is_only_unicode_combining_marks(self) -> None:
        # Combining marks alone drop out under NFKD->ASCII and so tokenize
        # to nothing, triggering the fallback.
        prefix = "́̈"
        assert (
            field_name("123 Part Number", style="snake", prefix=prefix)
            == "field_123_part_number"
        )


class TestLeadingDigitMultiTokenPrefix:
    """Valid prefixes with one or more tokens flow through style normally."""

    def test_snake_single_token_prefix(self) -> None:
        assert (
            field_name("123 Part Number", style="snake", prefix="column")
            == "column_123_part_number"
        )

    def test_kebab_single_token_prefix(self) -> None:
        assert (
            field_name("123 Part Number", style="kebab", prefix="column")
            == "column-123-part-number"
        )

    def test_camel_multi_token_prefix(self) -> None:
        assert (
            field_name("123 Part Number", style="camel", prefix="my field")
            == "myField123PartNumber"
        )

    def test_pascal_multi_token_prefix(self) -> None:
        assert (
            field_name("123 Part Number", style="pascal", prefix="my field")
            == "MyField123PartNumber"
        )

    def test_snake_multi_token_prefix(self) -> None:
        assert (
            field_name("123 Part Number", style="snake", prefix="my field")
            == "my_field_123_part_number"
        )

    def test_kebab_multi_token_prefix(self) -> None:
        assert (
            field_name("123 Part Number", style="kebab", prefix="my field")
            == "my-field-123-part-number"
        )

    def test_unicode_prefix_normalized(self) -> None:
        # The prefix runs through the same NFKD-to-ASCII pipeline.
        assert (
            field_name("123 Part", style="snake", prefix="café")
            == "cafe_123_part"
        )

    def test_prefix_with_punctuation_is_cleaned(self) -> None:
        assert (
            field_name("123 Part", style="snake", prefix="(my-col)")
            == "my_col_123_part"
        )


class TestReservedKeywords:
    def test_python_keyword_gets_underscore_suffix(self) -> None:
        assert field_name("class") == "class_"

    def test_for_keyword(self) -> None:
        assert field_name("for") == "for_"

    def test_keyword_after_styling(self) -> None:
        # "If" -> "if" -> reserved -> mangled.
        assert field_name("If") == "if_"

    def test_non_keyword_pass_phrase(self) -> None:
        # Multi-word phrase that includes a keyword shouldn't be mangled.
        assert field_name("Pass Through") == "pass_through"

    def test_pascal_preserves_case_and_mangles(self) -> None:
        # "True" remains "True" in pascal and is still a Python keyword.
        assert field_name("True", style="pascal") == "True_"


class TestCustomReservedWords:
    def test_custom_reserved_appends_underscore(self) -> None:
        assert (
            field_name("Reserved Name", reserved_words={"reserved_name"})
            == "reserved_name_"
        )

    def test_custom_reserved_short_name(self) -> None:
        assert field_name("id", reserved_words={"id"}) == "id_"

    def test_custom_reserved_does_not_match_other_names(self) -> None:
        assert field_name("Notes", reserved_words={"id"}) == "notes"

    def test_none_reserved_words_is_a_no_op(self) -> None:
        assert field_name("Notes", reserved_words=None) == "notes"


class TestStyleArgument:
    def test_invalid_style_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            field_name("Part Number", style="upper")

    def test_invalid_style_raises_unsupported_style_error(self) -> None:
        with pytest.raises(UnsupportedStyleError):
            field_name("Part Number", style="weird")

    def test_unsupported_style_error_is_value_error(self) -> None:
        assert issubclass(UnsupportedStyleError, ValueError)


class TestCamelCaseInput:
    def test_camel_case_input_splits(self) -> None:
        assert field_name("partNumber") == "part_number"

    def test_pascal_case_input_splits(self) -> None:
        assert field_name("PartNumber") == "part_number"

    def test_acronyms_split_cleanly(self) -> None:
        assert field_name("HTTPResponseCode") == "http_response_code"

    def test_all_caps_word(self) -> None:
        assert field_name("ALLCAPS") == "allcaps"

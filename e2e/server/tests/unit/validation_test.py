import pytest
import sys
from pathlib import Path

# Add server src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / "server"))

from src.component.validation import ( # type: ignore
    equal_value,
    validate_field,
    validate,
    build_validation_rules,
)


class TestEqualValue:
    """Test the equal_value function"""

    def test_equal_value_exact_match(self):
        """Test when received and expected values match exactly"""
        assert equal_value("qa", "qa") is True

    def test_equal_value_different_values(self):
        """Test when received and expected values don't match"""
        assert equal_value("qa", "sit") is False

    def test_equal_value_with_all_wildcard(self):
        """Test when expected value is 'all' (wildcard)"""
        assert equal_value("qa", "all") is True
        assert equal_value("loan", "all") is True
        assert equal_value("api", "all") is True

    def test_equal_value_case_sensitive(self):
        """Test that comparison is case-sensitive"""
        assert equal_value("QA", "qa") is False
        # Note: equal_value("All", "all") returns True because "all" is the wildcard
        assert equal_value("All", "all") is True

    def test_equal_value_with_empty_strings(self):
        """Test with empty strings"""
        assert equal_value("", "") is True
        assert equal_value("", "all") is True
        assert equal_value("qa", "") is False


class TestValidateField:
    """Test the validate_field function"""

    def test_validate_field_passes(self):
        """Test validation passes for matching values"""
        validations = [{"is_valid": equal_value}]
        result = validate_field("qa", "qa", validations)
        assert result is None

    def test_validate_field_fails(self):
        """Test validation fails for non-matching values"""
        validations = [{"is_valid": equal_value}]
        result = validate_field("qa", "sit", validations)
        assert result is not None
        assert "Expected: sit" in result
        assert "Received: qa" in result

    def test_validate_field_with_wildcard(self):
        """Test validation with wildcard 'all'"""
        validations = [{"is_valid": equal_value}]
        result = validate_field("loan", "all", validations)
        assert result is None

    def test_validate_field_multiple_validations(self):
        """Test with multiple validation rules"""
        def always_true(val, expected):
            return True

        def always_false(val, expected):
            return False

        validations = [
            {"is_valid": always_true},
            {"is_valid": always_false},
        ]
        result = validate_field("any", "any", validations)
        assert result is not None

    def test_validate_field_error_message_format(self):
        """Test that error message has the correct format"""
        validations = [{"is_valid": equal_value}]
        result = validate_field("received_val", "expected_val", validations)
        assert result == "Expected: expected_val, Received: received_val"


class TestBuildValidationRules:
    """Test the build_validation_rules function"""

    def test_build_validation_rules_structure(self):
        """Test that validation rules have correct structure"""
        rules = build_validation_rules()
        
        assert "environment" in rules
        assert "day" in rules
        assert "app" in rules
        assert "protocol" in rules

    def test_build_validation_rules_contains_validators(self):
        """Test that each rule contains validators"""
        rules = build_validation_rules()
        
        for key, validators in rules.items():
            assert isinstance(validators, list)
            assert len(validators) > 0
            for validator in validators:
                assert "is_valid" in validator
                assert callable(validator["is_valid"])


class TestValidate:
    """Test the validate function"""

    def test_validate_all_fields_match(self):
        """Test validation passes when all fields match"""
        received = {
            "environment": "qa",
            "app": "loan",
            "protocol": "ui",
        }
        expected = {
            "source": "remote",
            "environment": "qa",
            "app": "loan",
            "protocol": "ui",
        }
        result = validate(received, expected)
        assert result is None

    def test_validate_with_wildcard_all(self):
        """Test validation passes with wildcard 'all' values"""
        received = {
            "environment": "sit",
            "app": "clo",
            "protocol": "api",
        }
        expected = {
            "source": "remote",
            "environment": "all",
            "app": "all",
            "protocol": "all",
        }
        result = validate(received, expected)
        assert result is None

    def test_validate_environment_mismatch(self):
        """Test validation fails when environment doesn't match"""
        received = {
            "environment": "qa",
            "app": "loan",
            "protocol": "ui",
        }
        expected = {
            "source": "remote",
            "environment": "sit",
            "app": "loan",
            "protocol": "ui",
        }
        result = validate(received, expected)
        assert result is not None
        assert "Expected: sit" in result

    def test_validate_skips_source_field(self):
        """Test that source field is skipped in validation"""
        received = {
            "environment": "qa",
            "app": "loan",
            "protocol": "ui",
        }
        expected = {
            "source": "local",  # Different source, should be ignored
            "environment": "qa",
            "app": "loan",
            "protocol": "ui",
        }
        result = validate(received, expected)
        assert result is None

    def test_validate_app_mismatch(self):
        """Test validation returns error on app field mismatch"""
        received = {
            "environment": "sit",
            "app": "clo",
            "protocol": "api",
        }
        expected = {
            "source": "remote",
            "environment": "qa",
            "app": "loan",
            "protocol": "ui",
        }
        result = validate(received, expected)
        assert result is not None

    def test_validate_partial_matching_fields(self):
        """Test validation with some matching and some non-matching fields"""
        received = {
            "environment": "qa",  # Matches
            "app": "clo",  # Doesn't match
            "protocol": "ui",
        }
        expected = {
            "source": "remote",
            "environment": "qa",
            "app": "loan",
            "protocol": "ui",
        }
        result = validate(received, expected)
        assert result is not None

    def test_validate_empty_received_data(self):
        """Test validation with missing fields in received data"""
        received = {}
        expected = {
            "source": "remote",
            "environment": "qa",
            "app": "loan",
            "protocol": "ui",
        }
        result = validate(received, expected)
        # Should fail because received values will be None
        assert result is not None

    @pytest.mark.parametrize(
        "received,expected,should_pass",
        [
            (
                {"environment": "qa", "app": "loan", "protocol": "ui"},
                {"source": "remote", "environment": "qa", "app": "loan", "protocol": "ui"},
                True,
            ),
            (
                {"environment": "sit", "app": "clo", "protocol": "api"},
                {"source": "remote", "environment": "all", "app": "all", "protocol": "all"},
                True,
            ),
            (
                {"environment": "qa", "app": "loan", "protocol": "ui"},
                {"source": "remote", "environment": "sit", "app": "loan", "protocol": "ui"},
                False,
            ),
        ],
    )
    def test_validate_parametrized(self, received, expected, should_pass):
        """Parametrized tests for various validation scenarios"""
        result = validate(received, expected)
        if should_pass:
            assert result is None, f"Expected validation to pass but got error: {result}"
        else:
            assert result is not None, "Expected validation to fail but it passed"
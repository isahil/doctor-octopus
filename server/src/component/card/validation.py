from src.util.date import less_or_eqaul_to_date_time


def build_validation_rules():
    """Return a filter"""
    validation_rules = {
        "environment": [
            {"is_valid": equal_value},
        ],
        "app": [
            {"is_valid": equal_value},
        ],
        "protocol": [
            {"is_valid": equal_value},
        ],
        "day": [{"is_valid": less_or_eqaul_to_date_time}],
    }
    return validation_rules


def equal_value(received, expected):
    """Return True if the value is valid, otherwise False"""
    return received == expected
    

def validate_field(received_value, expected_value, validations):
        for validation in validations:  # validation = {'is_valid': <function is_valid>}
            valid = validation["is_valid"] # is_valid = True, False
            is_valid = valid(received_value, expected_value) # is_valid = True, False
            if not is_valid:
                error = f"Expected: {expected_value}, Received: {received_value}"
                return error
        return None

def validate(received_data, expected_data):
    """Validate the received_data based on the filter's expected_data value.
    Return True if the data matches the filter values, otherwise False"""
    validation_rules = build_validation_rules()
    for (expected_key, expected_value) in (expected_data.items()):  # key = "environment", "app", "protocol" | value = [{'is_valid': <function is_valid at 0x7f8b1c1f3d30>}]
        if expected_key == "source":
            continue
        received_value = received_data.get(expected_key) # received = "qa", "clo", "api"
        validations = validation_rules[expected_key] # validations = [{'is_valid': <function is_valid>}]
        for validation in validations:  # validation = {'is_valid': <function is_valid>}
            valid = validation["is_valid"] # is_valid = True, False
            is_valid = valid(received_value, expected_value) # is_valid = True, False
            if not is_valid:
                error = f"Expected: {expected_value}, Received: {received_value}"
                return error
    return None


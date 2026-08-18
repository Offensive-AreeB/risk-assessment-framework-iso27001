def validate_score_input(value: int) -> bool:
    """Validate that likelihood or impact value is between 1 and 5."""
    try:
        val = int(value)
        return 1 <= val <= 5
    except (ValueError, TypeError):
        return False

def get_validation_message(value: int, field_name: str) -> str:
    """Return a validation message for UI."""
    if not validate_score_input(value):
        return f"Invalid {field_name}. Must be an integer between 1 and 5."
    return ""

def validate_string_length(value: str, min_length: int = 1) -> bool:
    """Validate that a string is not empty and meets minimum length."""
    return isinstance(value, str) and len(value.strip()) >= min_length

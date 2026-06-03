"""
Tests for the input validation utilities.

Validators are pure functions: given an input string, they return
(is_valid, error_message). These tests verify both the happy path
(valid inputs pass) and the error cases (invalid inputs are rejected
with appropriate messages).
"""

from app.utils.validators import (
    validate_username,
    validate_email,
    validate_password,
    validate_project_name,
    validate_project_description,
    validate_task_title,
    validate_task_status,
    validate_task_priority,
    validate_task_due_date,
)


class TestUsernameValidation:
    """Tests for validate_username."""

    def test_valid_username(self):
        is_valid, error = validate_username("zohaib")
        assert is_valid is True
        assert error == ""

    def test_valid_username_with_underscore_and_numbers(self):
        is_valid, error = validate_username("zohaib_99")
        assert is_valid is True

    def test_empty_username_rejected(self):
        is_valid, error = validate_username("")
        assert is_valid is False
        assert "required" in error.lower()

    def test_too_short_username_rejected(self):
        is_valid, error = validate_username("ab")
        assert is_valid is False
        assert "3 characters" in error

    def test_username_starting_with_number_rejected(self):
        is_valid, error = validate_username("9zohaib")
        assert is_valid is False

    def test_username_with_special_chars_rejected(self):
        is_valid, error = validate_username("zoh@ib")
        assert is_valid is False


class TestEmailValidation:
    """Tests for validate_email."""

    def test_valid_email(self):
        is_valid, error = validate_email("zohaib@example.com")
        assert is_valid is True
        assert error == ""

    def test_empty_email_rejected(self):
        is_valid, error = validate_email("")
        assert is_valid is False

    def test_email_without_at_rejected(self):
        is_valid, error = validate_email("zohaibexample.com")
        assert is_valid is False

    def test_email_without_domain_rejected(self):
        is_valid, error = validate_email("zohaib@")
        assert is_valid is False


class TestPasswordValidation:
    """Tests for validate_password."""

    def test_valid_password(self):
        is_valid, error = validate_password("secret123")
        assert is_valid is True

    def test_too_short_password_rejected(self):
        is_valid, error = validate_password("abc12")
        assert is_valid is False
        assert "8 characters" in error

    def test_password_without_number_rejected(self):
        is_valid, error = validate_password("onlyletters")
        assert is_valid is False

    def test_password_without_letter_rejected(self):
        is_valid, error = validate_password("12345678")
        assert is_valid is False


class TestProjectValidation:
    """Tests for project name and description validators."""

    def test_valid_project_name(self):
        is_valid, error = validate_project_name("My Project")
        assert is_valid is True

    def test_empty_project_name_rejected(self):
        is_valid, error = validate_project_name("")
        assert is_valid is False

    def test_whitespace_only_project_name_rejected(self):
        is_valid, error = validate_project_name("   ")
        assert is_valid is False

    def test_empty_description_allowed(self):
        is_valid, error = validate_project_description("")
        assert is_valid is True


class TestTaskValidation:
    """Tests for task field validators."""

    def test_valid_task_title(self):
        is_valid, error = validate_task_title("Write tests")
        assert is_valid is True

    def test_empty_task_title_rejected(self):
        is_valid, error = validate_task_title("")
        assert is_valid is False

    def test_valid_status(self):
        is_valid, error = validate_task_status("todo")
        assert is_valid is True

    def test_invalid_status_rejected(self):
        is_valid, error = validate_task_status("banana")
        assert is_valid is False

    def test_valid_priority(self):
        is_valid, error = validate_task_priority("high")
        assert is_valid is True

    def test_invalid_priority_rejected(self):
        is_valid, error = validate_task_priority("urgent")
        assert is_valid is False

    def test_empty_due_date_allowed(self):
        is_valid, result = validate_task_due_date("")
        assert is_valid is True
        assert result is None

    def test_valid_due_date_parsed(self):
        is_valid, result = validate_task_due_date("2026-12-31")
        assert is_valid is True
        # result should be a date object
        assert result is not None

    def test_invalid_due_date_rejected(self):
        is_valid, result = validate_task_due_date("not-a-date")
        assert is_valid is False

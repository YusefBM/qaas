# Quiz App Tests

This directory contains comprehensive tests for the Quiz application using Python's `unittest` framework.

## Test Structure

The tests follow the same hierarchical structure as the main application:

```
quiz/tests/
├── __init__.py
├── README.md
├── test_runner.py
└── application/
    ├── __init__.py
    └── accept_invitation/
        ├── __init__.py
        └── test_accept_invitation_command_handler.py          # Unit tests
```

## Running Tests

### **Recommended: Using Django's Test Runner**

Django's built-in test runner is the recommended approach:

```bash
# Run all tests in the quiz app
python manage.py test quiz.tests

# Run all accept invitation tests
python manage.py test quiz.tests.application.accept_invitation

# Run specific test class
python manage.py test quiz.tests.application.accept_invitation.test_accept_invitation_command_handler.TestAcceptInvitationCommandHandler

# Run specific test method
python manage.py test quiz.tests.application.accept_invitation.test_accept_invitation_command_handler.TestAcceptInvitationCommandHandler.test_handle
```

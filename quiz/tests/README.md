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
        ├── test_accept_invitation_command_handler.py          # Unit tests
        └── test_accept_invitation_command_handler_integration.py  # Integration tests
```

## Test Types

### Unit Tests
- **Location**: `test_accept_invitation_command_handler.py`
- **Purpose**: Test the `AcceptInvitationCommandHandler` in isolation using mocks
- **Coverage**: 
  - Successful invitation acceptance
  - Already accepted invitation error handling
  - Expired invitation error handling
  - Invitation not found error handling
  - Database transaction rollback scenarios
  - Logging functionality
  - Response object creation and formatting

### Integration Tests
- **Location**: `test_accept_invitation_command_handler_integration.py`
- **Purpose**: Test the full flow with real database interactions
- **Coverage**:
  - End-to-end invitation acceptance with database
  - Real database constraint validation
  - Transaction integrity testing
  - Multi-user scenarios
  - Edge cases with null expiration dates

## Running Tests

### **Recommended: Using Django's Test Runner**

Django's built-in test runner is the recommended approach as it properly handles Django setup, database creation, and cleanup:

```bash
# Run all tests in the quiz app
python manage.py test quiz.tests

# Run all accept invitation tests
python manage.py test quiz.tests.application.accept_invitation

# Run specific test class
python manage.py test quiz.tests.application.accept_invitation.test_accept_invitation_command_handler.TestAcceptInvitationCommandHandler

# Run specific test method
python manage.py test quiz.tests.application.accept_invitation.test_accept_invitation_command_handler.TestAcceptInvitationCommandHandler.test_handle_successful_invitation_acceptance
```

### Using the Django Test Runner Script

For convenience, use the Django-specific test runner:

```bash
# Run all accept invitation tests
cd quiz/tests
python django_test_runner.py

# Run only unit tests
python django_test_runner.py --unit-only

# Run only integration tests
python django_test_runner.py --integration-only

# Run with different verbosity
python django_test_runner.py --verbosity 3
```

### Alternative: Custom Test Runner

The custom test runner provides unittest-based execution (note that Django must be properly configured):

```bash
# Run all tests for accept invitation
cd quiz/tests
python test_runner.py --type all

# Run only unit tests
python test_runner.py --type unit

# Run only integration tests
python test_runner.py --type integration
```

### Using Standard unittest

```bash
# From the project root
python -m unittest quiz.tests.application.accept_invitation.test_accept_invitation_command_handler

# Or with discovery
python -m unittest discover quiz/tests/application/accept_invitation
```

## Test Patterns and Best Practices

### Unit Test Patterns

1. **Arrange-Act-Assert**: All tests follow the AAA pattern for clarity
2. **Mocking**: External dependencies are mocked using `unittest.mock`
3. **Test Data**: UUIDs and test data are generated in `setUp()` method
4. **Exception Testing**: Comprehensive exception scenario coverage

### Integration Test Patterns

1. **TransactionTestCase**: Uses Django's `TransactionTestCase` for real database transactions
2. **Test Fixtures**: Real Django model instances created in `setUp()`
3. **Database State Verification**: Tests verify both response and database state
4. **Transaction Testing**: Includes rollback scenarios

### Naming Conventions

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<behavior_being_tested>`
- Integration test files: `test_<module_name>_integration.py`

## Dependencies

The tests require the following:

- Django test framework
- Python `unittest` module
- `unittest.mock` for unit tests
- Domain models and repositories from the application

## Test Data Management

### Unit Tests
- Use mocks and fake data
- UUIDs generated with `uuid4()`
- No database dependencies

### Integration Tests
- Create real model instances
- Use Django's database transaction handling
- Automatic cleanup after each test

## Extending the Test Suite

When adding new tests:

1. Follow the existing directory structure
2. Create both unit and integration tests when appropriate
3. Use descriptive test method names
4. Include docstrings explaining test purpose
5. Test both happy path and error scenarios
6. Update this README if adding new test patterns

## Test Coverage Goals

- **Unit Tests**: 100% code coverage of the command handler logic
- **Integration Tests**: All database interactions and business rules
- **Error Scenarios**: All exception paths covered
- **Edge Cases**: Boundary conditions and special cases

## Performance Considerations

- Unit tests should be fast (< 1ms each)
- Integration tests may be slower due to database operations
- Use `TransactionTestCase` only when testing transactions
- Use `TestCase` for faster tests when transactions aren't needed 
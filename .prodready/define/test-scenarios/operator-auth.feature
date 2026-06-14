Feature: Operator Authentication
  As an operator
  I want to securely log into the admin interface
  So that only I can manage my store's catalog

  Background:
    Given an operator account exists with email "owner@spiceshop.test" and a valid password

  Scenario: [US-001] - Successful login
    Given the operator is on the login page
    When they submit email "owner@spiceshop.test" with the correct password
    Then they are authenticated
    And they are redirected to the admin dashboard

  Scenario: [US-001] - Failed login with wrong password
    Given the operator is on the login page
    When they submit email "owner@spiceshop.test" with an incorrect password
    Then login is rejected
    And a generic error is shown that does not reveal which field was wrong

  Scenario: [US-001] - Password policy enforcement
    Given the operator is setting a new password
    When they enter a password shorter than 12 characters
    Then the password is rejected with a validation error
    When they enter a password longer than 64 characters
    Then the password is rejected with a validation error

  Scenario: [US-001] - Passwords are hashed with Argon2
    Given an operator sets a valid password
    When the password is persisted
    Then it is stored as an Argon2 hash
    And the plaintext password is never stored

  Scenario: [US-002] - Logout ends the session
    Given the operator is logged in
    When they log out
    Then their session is ended
    And visiting an admin page redirects them to the login page

  Scenario: [US-002] - Unauthenticated access is blocked
    Given a request to a management endpoint without authentication
    When the request is received
    Then it is rejected with an unauthorized response or redirect to login

Feature: Per-Category Custom Filters
  As an operator
  I want to define filters specific to each category and assign values to products
  So that shoppers can narrow products by attributes relevant to that category

  Background:
    Given the operator "owner@spiceshop.test" is logged into the admin interface
    And a category "Chili Peppers" exists

  Scenario: [US-007] - Define a choice filter with options
    When the operator adds a filter "Heat level" of type "choice" to "Chili Peppers"
    And adds the options "Mild", "Medium", and "Hot"
    Then the filter "Heat level" with those options is associated with "Chili Peppers"

  Scenario: [US-007] - Define a number filter with a unit
    When the operator adds a filter "Weight" of type "number" with unit "g"
    Then the filter "Weight" is associated with "Chili Peppers" and displays the unit "g"

  Scenario: [US-007] - Filters display in operator-defined order
    Given the filters "Heat level" and "Weight" exist on "Chili Peppers"
    When the operator orders "Weight" before "Heat level"
    Then the filters render in that order in admin and storefront

  Scenario: [US-008] - Assign a choice value to a product
    Given a product "Carolina Reaper" in "Chili Peppers"
    And a choice filter "Heat level" with option "Hot"
    When the operator sets "Heat level" to "Hot" for "Carolina Reaper"
    Then the product is recorded as matching "Heat level = Hot"

  Scenario: [US-008] - Reject non-numeric value for a number filter
    Given a product "Carolina Reaper" and a number filter "Weight"
    When the operator enters "abc" for "Weight"
    Then the value is rejected with a validation error

  Scenario: [US-009] - Deleting a filter warns about product values
    Given a filter "Heat level" has values assigned to products
    When the operator deletes "Heat level"
    Then they are warned that assigned product values will be removed
    And deletion only proceeds after confirmation

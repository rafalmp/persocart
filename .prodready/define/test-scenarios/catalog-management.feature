Feature: Catalog Management
  As an operator
  I want to manage categories and products
  So that shoppers have an organized catalog to browse

  Background:
    Given the operator "owner@spiceshop.test" is logged into the admin interface

  Scenario: [US-003] - Create a root category
    When the operator creates a category named "Spices" with no parent
    Then "Spices" appears as a top-level category in the tree
    And a unique slug is generated for it

  Scenario: [US-003] - Create a nested subcategory
    Given a category "Spices" exists
    When the operator creates a category named "Chili Peppers" with parent "Spices"
    Then "Chili Peppers" appears under "Spices" in the tree

  Scenario: [US-004] - Move a subtree to a new parent
    Given categories "Spices" and "Blends" exist
    And "Chili Peppers" is a child of "Spices"
    When the operator moves "Chili Peppers" under "Blends"
    Then "Chili Peppers" and its descendants appear under "Blends"

  Scenario: [US-004] - Deleting a non-empty category requires confirmation
    Given a category "Spices" contains products or subcategories
    When the operator attempts to delete "Spices"
    Then they are warned about the cascade
    And the deletion only proceeds after confirmation

  Scenario: [US-005] - Create a product in a category
    Given a category "Chili Peppers" exists
    When the operator creates a product "Carolina Reaper" with price "9.99" and an image
    Then the product appears in the "Chili Peppers" product list
    And exactly one image is stored for it

  Scenario: [US-005] - Reject a negative price
    Given a category "Chili Peppers" exists
    When the operator creates a product with price "-1.00"
    Then the product is rejected with a validation error

  Scenario: [US-006] - Deactivate a product hides it from shoppers
    Given an active product "Carolina Reaper" exists
    When the operator marks it inactive
    Then it no longer appears on the storefront
    But it is still listed in the admin interface

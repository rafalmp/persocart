Feature: Storefront Browsing and Filtering
  As a shopper
  I want to browse categories and filter products by category-specific attributes
  So that I can quickly find the products that match my needs

  Background:
    Given a published store with a category "Chili Peppers"
    And the category has a choice filter "Heat level" with options "Mild", "Medium", "Hot"
    And the following active products exist in "Chili Peppers":
      | name            | heat_level |
      | Jalapeno        | Medium     |
      | Carolina Reaper | Hot        |
      | Bell Pepper     | Mild       |

  Scenario: [US-010] - Browse the category tree
    Given a shopper opens the storefront
    When they view the category tree
    Then the category "Chili Peppers" is visible and navigable

  Scenario: [US-010] - View products in a category
    When the shopper selects the category "Chili Peppers"
    Then they see the products "Jalapeno", "Carolina Reaper", and "Bell Pepper"

  Scenario: [US-010] - Responsive layout on mobile
    Given the shopper uses a mobile viewport
    When the storefront renders
    Then the layout adapts responsively and remains usable

  Scenario: [US-011] - Apply a single filter value
    Given the shopper is viewing "Chili Peppers"
    When they apply "Heat level = Hot"
    Then only "Carolina Reaper" is shown

  Scenario: [US-011] - Multi-choice filter matches any selected value
    Given the category has a multi-choice filter applied
    When the shopper selects "Heat level" values "Mild" and "Hot"
    Then "Bell Pepper" and "Carolina Reaper" are shown
    And "Jalapeno" is not shown

  Scenario: [US-011] - Clearing filters restores the full list
    Given the shopper has applied "Heat level = Hot"
    When they clear all filters
    Then all products in "Chili Peppers" are shown again

  Scenario: [US-012] - View product detail
    Given the shopper is viewing "Chili Peppers"
    When they open "Carolina Reaper"
    Then they see its name, description, price, image, and filter values
    And the detail view is responsive and accessible

# Testing Guidelines

Documentation Version: 1.0

## Introduction

Testing is a fundamental part of DataNex AI.

Rather than testing individual functions in isolation, the project
uses Golden Tests to define and protect the expected behavior of the
AST Compiler.

Each compiler feature is represented by one or more Golden Tests.

As the compiler evolves, these tests form a growing regression suite
that ensures previously supported SQL generation continues to work
as expected.

## Purpose

The purpose of this test suite is to ensure that the AST Compiler
consistently generates the expected SQL for every supported query
pattern.

These tests serve as the official specification of the compiler's
behavior, allowing developers to validate changes with confidence.

Any intentional change to SQL generation must be accompanied by an
update to the corresponding Golden Test.

This policy ensures that new features and bug fixes do not
unintentionally alter the approved behavior of the AST Compiler.

## What is a Golden Test?

A Golden Test defines the expected SQL generated from a specific AST 
input. It serves as the official reference for how the AST Compiler
should behave for a particular query pattern.

Whenever the compiler is modified, the generated SQL is compared
against the corresponding Golden Test. If the outputs differ, the
change must be reviewed to determine whether it is an intentional
improvement or an unintended regression.

Golden Tests do not prevent change—they ensure that every change is
intentional, verified, and documented.

This philosophy allows DataNex AI to evolve with confidence while
preserving the stability and reliability of the AST Compiler.

## Project Test Structure

The AST Compiler test suite is organized as follows:

tests/
│
├── data/
│   └── test_cases.py
│
├── test_ast_compiler.py
│
└── testing_guidelines.md

Each file has a specific responsibility:

| File | Purpose |
|------|---------|
| `test_cases.py` | Stores the Golden Test cases, including AST input, schema, alias map, and expected SQL output. |
| `test_ast_compiler.py` | Executes the Golden Test suite by compiling each AST and comparing the generated SQL with the expected output.|
| `testing_guidelines.md` | Documents the testing philosophy, conventions, and best practices for maintaining the regression suite. |

This separation keeps test data, test execution, and documentation
independent, making the test suite easier to maintain as the project
continues to grow.

## Test Case Format

Every Golden Test follows a consistent structure to ensure readability,
maintainability, and predictable behavior across the entire regression
suite.

Each test case contains the following sections:

- ID
- Name
- Description
- Tags
- AST input
- Schema input
- Alias map
- Expected SQL output

Typical structure:

```python
{
    "id": "...",
    "name": "...",
    "description": "...",
    "tags": [...],
    "input": {
        "ast": {...},
        "schema": {...},
        "alias_map": {...}
    },
    "expected": {
        "sql": "..."
    }
}
```

The following sections describe the purpose and conventions of each
component in detail.

## Naming Conventions

Consistent naming improves readability and makes the regression suite
easier to navigate and maintain.

The following conventions should be followed throughout the entire Golden Test suite.

### Test ID

Each test case must have a unique identifier.

Format:

```text
AST-001
AST-002
AST-003
...
```

Test IDs are assigned sequentially as new Golden Tests are added and must never be reused.

### Test Name

The test name should clearly describe the SQL scenario being verified.

Recommended format:

<Category> - <Scenario>

Examples:

- Raw Select - Production Today
- Report - Total Production by Factory
- Report - Factories with Total Production > 1000
- Report - Top 10 Factories by Production

Use concise, descriptive names that make the purpose of the test
immediately understandable.

### Description

Descriptions should begin with:

Verify compilation...

Examples:

- Verify compilation of a raw SELECT for today.
- Verify compilation of a report with SUM aggregation grouped by factory.
- Verify compilation of a report using a HAVING clause.

Descriptions should explain what the test verifies, not how the
compiler works.

### Tags

Tags classify test cases by feature and make the test suite easier
to organize and search.

Guidelines:

- Use lowercase.
- Use short, descriptive keywords.
- Include only relevant tags.

Examples:

- raw
- report
- aggregation
- group_by
- having
- relative_period
- top_n
- join
- count
- avg
- max
- min

## Writing Expected SQL

The expected SQL represents the official output of the AST Compiler
for a given test case.

To ensure consistency across the regression suite, expected SQL should
follow the formatting rules below.

### Formatting Rules

- Use uppercase for SQL keywords (SELECT, FROM, WHERE, GROUP BY, etc.).
- Place each selected column on its own line.
- Indent columns and expressions consistently.
- Use table aliases whenever applicable.
- Preserve a consistent clause order.
- Use meaningful aliases for aggregated expressions.
- Remove unnecessary trailing spaces.

### Clause Order

Expected SQL should follow the standard clause order:

```text
SELECT
FROM
JOIN
WHERE
GROUP BY
HAVING
ORDER BY
```

When supported, LIMIT/FIRST should appear as part of the SELECT clause,
following the SQL dialect implemented by the compiler.

### Normalization

Before comparison, both the generated SQL and the expected SQL are
normalized to ignore insignificant formatting differences.

The comparison verifies the logical SQL structure rather than cosmetic
whitespace differences.

Expected SQL should always represent the approved output produced by
the AST Compiler.

Expected SQL should follow the SQL dialect supported by the
AST Compiler, including Informix-specific syntax such as
FIRST instead of LIMIT.

A Golden Test should be easy to read, easy to review, and immediately reveal the intended SQL behavior.

## Regression Policy

The regression suite protects the approved behavior of the AST
Compiler as the project evolves.

Whenever a bug is fixed or a new feature changes SQL generation, the
following process must be followed:

1. Add or update the corresponding Golden Test.
2. Verify that the new behavior is correct.
3. Run the complete regression suite.
4. Confirm that all existing Golden Tests continue to pass.

A change is considered complete only when both the implementation and
its corresponding Golden Test are updated together.

This policy ensures that improvements remain intentional, verified,
and fully documented.

The implementation and its Golden Tests are expected to evolve together throughout the lifetime of the project.

## Test Independence

Every Golden Test must be completely self-contained.

A test case must include all the information required to compile the
expected SQL without relying on any previous pipeline stage or external
state.

Each test must provide its own:

- AST input
- Schema input
- Alias map
- Expected SQL output

Golden Tests must never depend on:

- Previous test cases
- Prompt parsing
- Session state
- External services
- Runtime-generated data

Keeping each test independent makes the regression suite reliable,
repeatable, and easy to maintain.

A Golden Test should describe a complete compiler scenario, not just a single function call.

## Adding a New Test

When a new SQL feature is implemented or an existing behavior is
intentionally changed, a corresponding Golden Test should be added or
updated.

The recommended workflow is:

1. Implement or modify the compiler behavior.
2. Build the corresponding AST input.
3. Define the required schema and alias map.
4. Write the expected SQL output.
5. Add the new test case to `test_cases.py`.
6. Run the complete regression suite.
7. Verify that all Golden Tests pass before committing the changes.

Every approved compiler behavior should be accompanied by a Golden Test. 

## Running the Test Suite

Run the complete AST Compiler regression suite using:

```bash
python -m pytest tests/test_ast_compiler.py -v -s
```

The test suite should be executed:

- After adding a new Golden Test.
- After modifying the AST Compiler.
- Before committing changes.
- Before opening a pull request.

A successful test run confirms that the current implementation
remains consistent with the approved compiler behavior.

All Golden Tests should pass before changes are considered ready for review or release.

## Current Coverage

The current AST Compiler regression suite verifies the following SQL
features:

### Basic Queries

- Raw SELECT
- Table aliases
- ORDER BY

### Aggregation

- SUM
- AVG
- MAX
- MIN
- COUNT(*)
- COUNT(DISTINCT)

### Grouping

- GROUP BY
- HAVING

### Relative Date Filters

- Today
- Yesterday
- This Month
- This Year

### Result Limiting

- FIRST (Top N)

### Current Golden Tests

- AST-001 → AST-012

The regression suite will continue to expand as new compiler features
are implemented and approved.

This document is intended to evolve alongside the AST Compiler and its regression suite.
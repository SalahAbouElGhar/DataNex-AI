# DataNex AI Design Principles

These principles evolved with the project.

> **We do not optimize for speed. We optimize for understanding. Speed comes naturally afterward.**

**Version:** 1.1
**Status:** Living Document
**Author:** Salah Abou El-Ghar

---

## 1. Project Philosophy

DataNex AI is not merely an SQL generator.

**DataNex AI is a Business Reasoning Engine that translates business language into decisions, and then into SQL.**

The system should:

```text
Understand language
        ↓
Extract facts
        ↓
Understand business meaning
        ↓
Make business decisions
        ↓
Build query plans
        ↓
Generate IBM Informix SQL
```

SQL generation is the final expression of the reasoning process, not the primary goal.

The quality of the final SQL is determined long before SQL generation begins.


## 2. Core Architectural Principles

### 2.1 Single Responsibility

Every module has one clear architectural responsibility.

Every function has one focused responsibility within its layer.

Every business decision has one clear owner.

A function should answer one business or architectural question rather than several unrelated questions.

A module is complete when its responsibility is clear and stable, not when it contains every function that might eventually be useful.


### 2.2 Design Before Coding

Before implementing or changing a module or major function:

1. Define its purpose.
2. Define its required inputs.
3. Define its output contract.
4. Define its workflow.
5. Only then write the code.

> **Think First. Design Second. Code Third.**

### 2.3 One Public Entry Point

Where appropriate, a module should expose a clear public entry point for its primary responsibility while keeping implementation helpers internal.

The public entry point should represent the module's stable external contract.

Examples include:

* `build_business_decision()`
* `build_query_plan()`
* `compile_sql_ast()`

Public entry points should remain focused on orchestration or the primary responsibility of their module. Internal helper functions may support the workflow without becoming part of the module's external contract.


### 2.4 Architecture Evolves After Stability

Do not reorganize the architecture while core responsibilities are still being discovered or are still moving.

Allow implementations to evolve within stable responsibilities and contracts.

Refactoring should follow a stable milestone and an architecture review.

> **Refactor After Stability.**

---

## 3. Business Before SQL

Business concepts always come before SQL syntax.

Business Reasoning must not depend on SQL syntax.

SQL generation belongs to the Compiler layer.

```text
Business Meaning
      ↓
Query Planning
      ↓
AST
      ↓
SQL Compiler
```

There should be **no SQL inside Business Reasoning** and **no Business Logic inside the Compiler**.

---

## 4. Context Separation

DataNex maintains explicit boundaries between different types of context.

```text
Knowledge Context

Reasoning Context

Database Context
```


Each context has an owner and serves a defined architectural purpose.

Contexts are for organization. Parameters are for precision.

A context may contain other contexts without flattening their identities.

> **Never flatten information that still has an identity.**

---

## 5. Knowledge, Facts, and Decisions

These concepts must remain distinct.

### Knowledge

Knowledge defines the vocabulary and domain information available to the system.

Examples include business keywords and constants.

> **Business keywords are Knowledge, not Reasoning.**

### Facts

Facts describe what the reasoning layer discovered from the prepared context.

Examples:

```text
requested_measure
aggregation_function
group_dimensions
time_filter
ranking_strategy
intent
```

Every extracted fact should be independently testable.

A reasoning fact follows the pattern:

```text
Read Context
   ↓
Find Candidates
   ↓
Reason
   ↓
Return One Fact
```

### Decisions

Decisions interpret facts according to business rules.

```text
Facts
  ↓
Business Rules
  ↓
Business Decision
```

> **Facts describe reality. Decisions interpret reality.**

---

## 6. Reasoning Pipeline

Natural Language is normalized before facts are extracted.

Fact Extraction produces Reasoning Facts.

Business Reasoning consumes Reasoning Facts.

Business Reasoning should not reinterpret raw language when the required fact is already available.

```text
Natural Language
      ↓
Normalization
      ↓
Fact Extraction
      ↓
Reasoning Facts
      ↓
Business Reasoning
      ↓
Business Decision
```

Normalization prepares text. Reasoning understands it.

Reasoning layers must not perform normalization as part of their responsibility.

They consume prepared and normalized inputs supplied by upstream layers.


> **Reasoning consumes knowledge. It does not own knowledge.**

> **Never classify before understanding.**

> **Discovery provides candidates. Reasoning selects the intended one.**

---

## 7. Business Reasoning

Business Reasoning has one responsibility:

> **Make business decisions from prepared facts and context.**

It does not build SQL.

It does not resolve database columns.

It does not know database-specific implementation details.

The Business Decision speaks Business Language.

For example:

```text
production
factory
SUM
TOP 5
latest 5
```

rather than:

```text
qty
factory_id
prod_date
ORDER BY total_qty DESC
```

### Business Decision Contract

A Business Decision may contain concepts such as:

```text
business_objective
primary_entity
requires_measure
measure
aggregation
display_entities
grouping_entities
ranking
ordering
time_filter
defaults
```

The decision should describe **what the user wants**, not **how the database will execute it**.

---

## 8. Business Meaning vs Database Semantics

This boundary is fundamental to DataNex AI.

> **Business Reasoning determines business meaning; Query Planning resolves database semantics; AST represents the decided query structure; Compiler generates IBM Informix SQL.**


Example:

```text
Business Decision
    production
    factory
    measure_desc
       ↓
Query Plan
    qty
    factory_id
       ↓
AST
    total_qty DESC
       ↓
Informix SQL
```

Another example:

```text
Business Decision
    latest_n(5)
       ↓
Query Plan
    latest_date + prod_date
       ↓
AST
    prod_date DESC + FIRST 5
```

Business Reasoning should never need to know that `production` maps to `qty`, or that `latest` maps to `prod_date`.

---

## 9. Query Planning

Query Planning translates Business Decisions into database-aware query semantics.

It is the correct layer for resolving:

```text
Business Entity → Database Column
Business Measure → Database Measure Column
Business Ordering → Execution Ordering
Ranking / Selection → Ordering + Limit
```

Query Planning may know the schema, aliases, date columns, measures, relationships, and database-specific execution requirements.

It should not redefine the business meaning of the request.

---

## 10. AST and Compilation

The AST is the structured execution representation used before SQL generation.

The AST compiler is deterministic.

The Compiler converts database-aware AST structures into IBM Informix SQL.

```text
Query Plan
    ↓
AST
    ↓
Validation
    ↓
SQL Compiler
    ↓
IBM Informix SQL
```

The Compiler must not make new business decisions.

It should compile an already-decided query structure.

---

## 11. Ranking and Selection Semantics

Ranking and detail selection are related but not identical.

### Report Ranking

```text
top_n
    → measure DESC
    → FIRST N

bottom_n
    → measure ASC
    → FIRST N
```

### Detail Selection

```text
latest_n
    → date DESC
    → FIRST N

first_n
    → date ASC
    → FIRST N
```

This distinction is important because `top_n` and `bottom_n` normally operate on aggregated report results, while `latest_n` and `first_n` select detail records.

For example:

```text
latest 5 production transactions
```

must not automatically become:

```text
SUM(qty)
```

unless aggregation was explicitly requested.

---

## 12. Business Defaults

Business Defaults apply only when the user has not already specified a conflicting decision.

Examples currently established in Business Reasoning:

```text
REPORT + measure + grouping + no ranking
    → ordering = measure_desc

DETAIL + no ranking + no ordering
    → ordering = latest
```

When ranking is present, Business Defaults must not introduce a conflicting ordering.

Examples:

```text
top_n
bottom_n
latest_n
first_n
```

These are explicit selection/ranking decisions and must take precedence over default ordering behavior.

---

## 13. DataNex AI Testing Philosophy

> **We do not test functions alone. We test decisions and behavior.**

DataNex uses multiple levels of protection.

### Component / Golden Tests

Golden Tests protect deterministic AST-to-SQL compiler behavior.

Each Golden Test records an approved AST, schema, alias map, and expected SQL output.

### End-to-End Regression Tests

End-to-End regression tests protect the complete reasoning path:

```text
Prompt
  ↓
Reasoning Facts
  ↓
Business Decision
  ↓
Query Plan
  ↓
AST
  ↓
SQL
```

Current Ranking / Selection regression coverage includes:

```text
top 5 factories by production
bottom 5 factories by production
latest 5 production transactions
first 5 production transactions
```

A change is not considered safe merely because the SQL is syntactically valid. The generated SQL must preserve the intended business meaning.

---

## 14. Regression Safety

Every intentional change to approved behavior must be reflected in the appropriate regression test or Golden Test.

Regression tests should protect architectural contracts, not just output strings.

Important contracts include:

```text
Business meaning remains stable.
Business decisions remain database-independent.
Query planning resolves database semantics.
AST remains structurally valid.
SQL compilation remains deterministic.
```

A previously approved behavior should remain stable unless the change is intentional and documented.

---

## 15. Module Design Rules

Every new module should clearly define:

```text
Purpose
Public Entry Function
Inputs
Outputs
Internal Workflow
Private Helpers
```

A module should answer one architectural question.

A function should receive the minimum required input for its responsibility.

Variable names should reflect the stage of the pipeline, not only the underlying concept.

Code should tell the story of the data.

Each step should produce a clearer version of its input.

> **Never destroy the original input. Transform it step by step.**

---

## 16. Utility Design

Lower-level utilities perform focused work.

Higher-level utilities orchestrate lower-level utilities rather than duplicating their logic.

Collection functions should return a collection consistently according to their contract; use an empty collection instead of `None` when the contract defines a collection as output.

Normalization functions must not mutate their input. They return a new normalized representation.

> **Normalize objects without interpreting them.**

---

## 17. Development Workflow

DataNex development follows this sequence:

```text
Idea
  ↓
Discussion
  ↓
Design
  ↓
Agreement
  ↓
Implementation
  ↓
Testing
  ↓
Architecture Review
  ↓
Refactoring
  ↓
Stable Version
  ↓
Next Feature
```

The project should reach stability before major restructuring.

A good architecture is discovered as responsibilities become clear; it is not imposed for imaginary future requirements.

> **Separate when the boundary is already obvious. Delay when the boundary is still evolving.**

---

## 18. Architecture Evolution

Folders and modules should appear when real responsibilities emerge.

Do not build architecture for imaginary future requirements.

Separate by responsibility, not by size.

Architecture should guide the files; files should never dictate the architecture.

A system should be organized by the order of thinking, not merely by the order of execution.

> **Good architecture is discovered, not invented.**

As understanding grows, hidden responsibilities become visible.

When responsibilities become clear, architecture reveals itself.

---

## 19. Living Document

This is a Living Document.

Every major architectural decision should be reflected here.

The document may evolve as the implementation evolves, but changes should preserve the project's core principles.

> **The architecture serves the project. The project never serves the architecture.**

---

## 20. Final Principles

```text
One Function = One Clear Responsibility
One Decision = One Owner
One Module = One Responsibility

Knowledge is shared.
Reasoning consumes knowledge.
Facts describe what was discovered.
Decisions interpret what was discovered.

Business Reasoning decides business meaning.
Query Planning resolves database semantics.
AST represents the decided query structure.
Compiler generates IBM Informix SQL.

No SQL inside Business Reasoning.
No Business Logic inside the Compiler.

Think First.
Design Second.
Code Third.
Refactor After Stability.
```

DataNex AI starts with understanding the business, not with SQL.

The system is no longer being designed as a collection of isolated functions. It is being developed as a language that the entire system can understand consistently.

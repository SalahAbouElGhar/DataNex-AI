# ==========================================================
# Normalization Utilities
# ==========================================================
"""

Status:
-------
 Stable

Reference Module:
 Yes

Coding Standard:
 Approved

Version:
-------
 1.0

State:
-----
 Closed for current sprint.
"""
"""
Normalization Layer
===================

## Purpose

Provide common normalization utilities used across the
DataNex AI Reasoning Pipeline.

The purpose of this module is to standardize the representation
of data before it enters the reasoning process.

Normalization prepares the data.

Reasoning understands the data.

## Core Principles

* Normalization changes representation, never meaning.
* Reasoning interprets meaning.
* Utilities should be pure whenever possible.
* Utilities should be stateless.
* Utilities should be deterministic.
* Normalize according to the shape of the data.

## Normalization Levels

Value
Normalize a single textual value.

Collection
Normalize a collection of textual values.

Semantic Object
Normalize structured semantic objects.

## Public API

normalize_text()
Normalizes a single text value.

normalize_candidates()
Normalizes a collection of candidate values.

normalize_semantic_targets()
Normalizes semantic target objects.

## Responsibilities

This module is responsible for:

* Normalizing user text.
* Normalizing candidate collections.
* Normalizing semantic structures.
* Producing a consistent representation for the Reasoning Layer.

## Non-Responsibilities

This module does NOT:

* Perform business reasoning.
* Interpret user intent.
* Detect business synonyms.
* Perform semantic matching.
* Make business decisions.
* Generate SQL.
* Read database schema.
* Execute query planning.

## Design Philosophy

Normalization is the entrance gate to the Reasoning Layer.

Every reasoning function should receive normalized data,
allowing the reasoning process to focus entirely on business
understanding rather than data formatting.

The output of this module is always a cleaner representation
of the original input, while preserving its meaning completely.
"""

# --------------------------------------------------------
def normalize_text(text):
    """
    Normalize textual representation without changing its meaning.

    Input
    -----
    Raw Text

    Output
    ------
    Normalized Text

    Responsibilities
    ----------------
    - Remove leading spaces.
    - Remove trailing spaces.
    - Collapse multiple spaces.
    - Convert to lowercase.

    Does NOT
    --------
    - Change words.
    - Replace synonyms.
    - Interpret meaning.
    """

    if text is None:
        return ""

    normalized_text = text.strip()

    normalized_text = " ".join(normalized_text.split())

    normalized_text = normalized_text.lower()

    return normalized_text

# ----------------------------------
# Expected Behavior
# ----------------------------------

# normalize_text("  Total Production  ")
# -> "total production"

# normalize_text("TOTAL     QTY")
# -> "total qty"

# normalize_text("")
# -> ""

# normalize_text(None)
# -> ""
# --------------------------------------------------------
def normalize_candidates(candidates):
    """
    Purpose
    -------
    Normalize a collection of candidate values without
    changing their meaning.

    Input
    -----
    List of candidate values.

    Output
    ------
    Normalized candidate list.

    Responsibilities
    ----------------
    - Normalize every candidate using normalize_text().
    - Remove empty candidate values.
    - Remove duplicated candidate values.
    - Preserve the order of the first occurrence.
    - Preserve semantic meaning.

    Does NOT
    --------
    - Perform business reasoning.
    - Perform semantic matching.
    - Replace synonyms.
    - Rank candidates.
    - Select the requested candidate.
    """

    if not candidates:
        return []

    normalized_candidates = []

    for candidate in candidates:

        normalized_candidate = normalize_text(
            candidate
        )

        if not normalized_candidate:
            continue

        if normalized_candidate in normalized_candidates:
            continue

        normalized_candidates.append(
            normalized_candidate
        )

    return normalized_candidates


# ----------------------------------
# Expected Behavior
# ----------------------------------

# normalize_candidates(
#     [" Qty ", "PRICE", "qty", "", None]
# )
#
# ->
#
# ["qty", "price"]


# normalize_candidates([])
#
# ->
#
# []


# normalize_candidates(
#     ["Amount", "amount", "AMOUNT"]
# )
#
# ->
#
# ["amount"]


# ----------------------------------------------------------
# Semantic Target Object
# ----------------------------------------------------------
#
# Represents one semantic concept identified during
# the reasoning preparation stage.
#
# Structure
#
# {
#     "term": "<user semantic term>",
#
#     "matches": [
#         "<normalized candidate>",
#         ...
#     ]
# }
#
# Notes
# -----
# - "term" preserves the semantic concept requested
#   by the user.
#
# - "matches" contains all normalized candidate
#   columns associated with that semantic concept.
#
# - This object is normalized only.
#
# - Business interpretation is performed later
#   by the Reasoning Layer.
# ----------------------------------------------------------

def normalize_semantic_targets(semantic_targets):
    """
    Purpose
    --------
    Normalize semantic target objects without changing
    their meaning.

    Input
    -----
    List of Semantic Target Objects.

    Output
    ------
    Normalized Semantic Target Objects.

    Responsibilities
    ----------------
    - Normalize every semantic term.
    - Normalize every candidate match.
    - Remove empty values.
    - Remove duplicated matches.
    - Preserve the order of the first occurrence.
    - Preserve semantic meaning.

    Does NOT
    --------
    - Perform business reasoning.
    - Perform semantic interpretation.
    - Detect synonyms.
    - Rank semantic matches.
    - Select the best semantic target.

    Design Note
    -----------
    Acts as a Normalization Coordinator.

    Delegates normalization work to
    lower-level normalization utilities.

    """
    if not semantic_targets:
        return []

    normalized_targets = []

    for target in semantic_targets:
        normalized_term = normalize_text(
            target["term"]
        )
        normalized_matches = normalize_candidates(
            target["matches"]
        )

        normalized_target = {

            "term": normalized_term,

            "matches": normalized_matches
        }

        normalized_targets.append(
            normalized_target
        )

    return normalized_targets

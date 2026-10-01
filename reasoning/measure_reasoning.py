from utils.normalization import (
    normalize_text
    )
# --------------------------------------------------
# Measure Reasoning
# --------------------------------------------------

"""
Purpose
-------

Determine the business measure requested by the user.

## Responsibilities

* Analyze the user request.
* Identify the requested business measure.

## Input

Prompt
Knowledge Context

## Output

Requested Business Measure

This module DOES NOT:

* Read database schema.
* Generate SQL.
* Build Query Plans.
* Make Business Decisions.

This module is responsible only for identifying
the business measure requested by the user.
"""

# --------------------------------------------------
# Step 2 : Exact Semantic Matching
# --------------------------------------------------

def find_exact_measure_match(
normalized_prompt,
normalized_measures
):

    """
    Search for an exact business measure term
    inside the normalized user request.

    ```
    Input
    -----
    normalized_prompt
        Normalized user request.

    normalized_measures
        Normalized measure knowledge.

        Example:
        {
            "production": "qty",
            "sales": "sales_amt"
        }

    Output
    ------
    Business Measure Name

    or

    None

    Responsibilities
    ----------------
    - Search normalized measure names.
    - Return the first exact match.
    - Return None when no exact match exists.

    Does NOT
    --------
    - Normalize inputs.
    - Detect aliases.
    - Detect synonyms.
    - Rank candidates.
    """

    if not normalized_prompt:
        return None

    if not normalized_measures:
        return None

    prompt_tokens = normalized_prompt.split()

    for measure_name in normalized_measures:

        if measure_name in prompt_tokens:
            return measure_name

    return None


# --------------------------------------------------
# Expected Behavior
# --------------------------------------------------

# normalized_prompt =
# "show production by factory"
#
# normalized_measures =
# {
# "production": "qty",
# "sales": "sales_amt"
# }
#
# ->
#
# "production"

# normalized_prompt =
# "show factory by date"
#
# ->
#
# None

# --------------------------------------------------
# Step 3 : Business Synonym Matching
# --------------------------------------------------
def find_synonym_measure_matches(
    normalized_prompt,
    measure_synonyms
):
    """
    Find all business measures matched
    through user language / business synonyms.

    Input
    -----
    normalized_prompt
        Normalized user request.

    measure_synonyms
        Normalized measure synonyms.

        Example:
        {
            "sales": [
                "sales",
                "revenue",
                "income"
            ]
        }


    Returns
    -------
    List[str]
        Matched business measure names.

    Behavior
    --------
    - No match          -> []
    - One match         -> List[str]
    - Multiple matches  -> List[str]

    Does NOT
    --------
    - Normalize inputs.
    - Generate SQL.
    - Apply business rules.
    - Evaluate candidates.
    """


    if not normalized_prompt:
        return []

    if not measure_synonyms:
        return []

    prompt_tokens = normalized_prompt.split()

    matched_measures = []

    for measure_name, synonyms in measure_synonyms.items():

        for synonym in synonyms:

            if synonym in prompt_tokens:

                if measure_name not in matched_measures:
                    matched_measures.append(
                        measure_name
                    )

                break

    return matched_measures

# --------------------------------------------------
# Expected Behavior
# --------------------------------------------------

# measure_synonyms = {
# "sales": [
#   "sales",
#   "revenue",
#   "income"
#   ],

# "production": [
#   "production",
#   "output"
#   ]
# }

# normalized_prompt =
# "show revenue by customer"
#
# ->
#
# ["sales"]

# normalized_prompt =
# "show output by factory"
#
# ->
#
# ["production"]

# normalized_prompt =
# "show factory by date"
#
# ->
#
# []

# normalized_prompt =
# "show revenue and production"
#
# ->
#
# ["sales","production"]
# ---------------------------------------------------------
def calculate_measure_evidence(
    normalized_prompt,
    measure_name,
    measure_synonyms
):
    """
    Calculate semantic evidence for one measure.

    Returns
    -------
    int
        Number of measure synonyms found
        in the normalized prompt.
    """

    if not normalized_prompt:
        return 0

    if not measure_name:
        return 0

    synonyms = measure_synonyms.get(
        measure_name,
        []
    )

    prompt_tokens = normalized_prompt.split()

    score = 0

    for synonym in synonyms:

        if synonym in prompt_tokens:
            score += 1

    return score
# --------------------------------------------------------
def evaluate_measure_candidates(
    normalized_prompt,
    candidates,
    measure_synonyms
):
    """
    Evaluate ambiguous measure candidates.

    Input
    -----
    normalized_prompt
        Normalized user request.

    candidates
        Candidate business measures.

    measure_synonyms
        Business measure synonyms.

    Output
    ------
    Best business measure

    or

    None
    """

    if not normalized_prompt:
        return None

    if not candidates:
        return None

    # --------------------------------------------------
    # Calculate Evidence
    # --------------------------------------------------

    scores = {}

    for measure_name in candidates:

        scores[measure_name] = (
            calculate_measure_evidence(
                normalized_prompt,
                measure_name,
                measure_synonyms
            )
        )

    # --------------------------------------------------
    # Find Best Score
    # --------------------------------------------------

    max_score = max(
        scores.values()
    )

    # --------------------------------------------------
    # Best Candidates
    # --------------------------------------------------

    best_candidates = [
        measure_name
        for measure_name, score
        in scores.items()
        if score == max_score
    ]

    # --------------------------------------------------
    # Unique Best Candidate
    # --------------------------------------------------

    if len(best_candidates) == 1:
        return best_candidates[0]

    # --------------------------------------------------
    # Ambiguous
    # --------------------------------------------------

    return None

# --------------------------------------------------
# Resolve Requested Measure
# --------------------------------------------------
def resolve_requested_measure(
    prompt,
    knowledge_context
):
    """
    Determine the business measure requested by the user.

    Input
    -----
    Prompt
    Knowledge Context

    Output
    ------
    Requested Business Measure

    or

    None
    """

    # --------------------------------------------------
    # Step 1 : Normalize Prompt
    # --------------------------------------------------

    normalized_prompt = normalize_text(
        prompt
    )

    # --------------------------------------------------
    # Knowledge
    # --------------------------------------------------

    normalized_measures = knowledge_context.get(
        "measures",
        {}
    )

    normalized_measure_synonyms = (
        knowledge_context.get(
            "measure_synonyms",
            {}
        )
    )

    # --------------------------------------------------
    # Step 2 : Exact Semantic Matching
    # --------------------------------------------------

    exact_match = find_exact_measure_match(
        normalized_prompt,
        normalized_measures
    )

    if exact_match:
        return exact_match

    # --------------------------------------------------
    # Step 3 : Business Synonym Matching
    # --------------------------------------------------

    matched_measures = find_synonym_measure_matches(
        normalized_prompt,
        normalized_measure_synonyms
    )

    # --------------------------------------------------
    # Step 4 : Candidate Resolution
    # --------------------------------------------------

    if len(matched_measures) == 1:
        return matched_measures[0]

    if len(matched_measures) > 1:

        return evaluate_measure_candidates(
            normalized_prompt,
            matched_measures,
            normalized_measure_synonyms
        )

    # --------------------------------------------------
    # Step 5 : Return Unresolved
    # --------------------------------------------------

    return None

#Normalize
#    ↓
#Exact Match
#    ├── found → return
#    ↓
#Synonym Matching
#    ↓
#matched_measures
#    ↓
#Candidate Resolution
#    ├── 0 → Step 5 → None
#    ├── 1 → return
#    └── >1 → Evaluation later

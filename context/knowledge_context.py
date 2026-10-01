from schema.schema_utils import (
build_semantic_targets,
build_display_targets
)
from utils.normalization import (
    normalize_text,
    normalize_candidates,
)

# --------------------------------------------------
# Knowledge Context
# --------------------------------------------------

"""
Purpose
-------

Prepare all business knowledge required by
the Business Reasoning Engine.

## Responsibilities

* Build Semantic Targets.
* Build Display Targets.
* Normalize Measure Knowledge.
* Normalize Measure Synonyms.

## Input

Domain Configuration

## Output

Knowledge Context

This module DOES NOT:

* Read database schema.
* Analyze user requests.
* Perform Business Reasoning.
* Generate SQL.

Knowledge Context is a pure business knowledge
representation used by higher reasoning layers.
"""

def prepare_knowledge_context(
domain_config
):
    """
    Build the complete Knowledge Context.
    """

    # --------------------------------------------------
    # Semantic Targets
    # --------------------------------------------------

    semantic_targets = build_semantic_targets(
        domain_config
    )

    # --------------------------------------------------
    # Display Targets
    # --------------------------------------------------

    display_targets = build_display_targets(
        domain_config
    )

    # --------------------------------------------------
    # Measure Knowledge
    # --------------------------------------------------

    measures = domain_config.get(
        "measures",
        {}
    )

    normalized_measures = {
        normalize_text(measure): column
        for measure, column in measures.items()
    }

    # --------------------------------------------------
    # Measure Synonyms
    # --------------------------------------------------

    measure_synonyms = domain_config.get(
        "measure_synonyms",
        {}
    )

    normalized_measure_synonyms = {
        normalize_text(measure):
            normalize_candidates(synonyms)

        for measure, synonyms
        in measure_synonyms.items()
    }

    # --------------------------------------------------
    # Return Knowledge Context
    # --------------------------------------------------

    return {

        "semantic_targets":
            semantic_targets,

        "display_targets":
            display_targets,

        "measures":
            normalized_measures,

        "measure_synonyms":
            normalized_measure_synonyms
    }

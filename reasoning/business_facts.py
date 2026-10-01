def resolve_business_grouping_dimensions(
    prompt,
    business_terms
):
    """
    Determine the business dimensions requested by the user.

    Input
    -----
    prompt
        User's natural-language request.

    business_terms
        Business vocabulary and aliases.

        Example:
        {
            "factory": ["factory", "factories"],
            "product": ["product", "products"]
        }

    Returns
    -------
    List[str]
        Business dimension names.

    Examples
    --------
    "show production by factory"
        -> ["factory"]

    "show production by product"
        -> ["product"]

    "show production by factory and product"
        -> ["factory", "product"]

    "show production"
        -> []

    Does NOT
    --------
    - Resolve database columns.
    - Use semantic_targets.
    - Use display_targets.
    - Generate SQL.
    """

    if not prompt:
        return []

    if not business_terms:
        return []

    normalized_prompt = prompt.lower()

    prompt_tokens = normalized_prompt.split()

    dimensions = []

    for business_term, aliases in business_terms.items():

        for alias in aliases:

            if alias in prompt_tokens:

                if business_term not in dimensions:
                    dimensions.append(
                        business_term
                    )

                break

    return dimensions
# ------------------------------------------------------
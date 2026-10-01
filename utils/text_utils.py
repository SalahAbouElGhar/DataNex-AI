def contains_any(
    text,
    keywords
):
    """
    Return True if any keyword
    exists in the text.
    """

    if not text:
        return False

    if not keywords:
        return False

    return any(
        keyword in text
        for keyword in keywords
    )
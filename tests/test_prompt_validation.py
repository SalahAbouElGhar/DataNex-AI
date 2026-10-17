import pytest

from validators.validators import validate_prompt


@pytest.mark.parametrize(
    "prompt",
    [
        None,
        "",
        "   ",
        "\n\t",
        123,
    ],
)
def test_validate_prompt_rejects_invalid_input(prompt):
    error = validate_prompt(prompt)

    assert error, (
        f"Expected validation error for input: {prompt!r}"
    )


@pytest.mark.parametrize(
    "prompt",
    [
        "total production by factory",
        "اعرض إجمالي الإنتاج لكل مصنع",
    ],
)
def test_validate_prompt_accepts_nonempty_text(prompt):
    assert validate_prompt(prompt) is None
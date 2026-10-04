import pytest

import prompts
import schemas


def render_cover_letter(**overrides):
    values = {
        "company": "Acme",
        "position": "SWE",
        "job_description": "Build APIs",
        "resume": "Built APIs",
        "tone": prompts.COVER_LETTER_TONES["concise"],
        **overrides,
    }
    return prompts.COVER_LETTER.render(**values)


def test_render_fills_every_placeholder():
    rendered = render_cover_letter()
    assert "$" not in rendered
    assert "<job_description>\nBuild APIs\n</job_description>" in rendered


def test_render_missing_variable_raises():
    with pytest.raises(KeyError):
        prompts.COVER_LETTER.render(company="Acme")


def test_user_text_is_not_reinterpreted_as_template():
    # A "$tone" or "{braces}" inside a job posting is just text
    rendered = render_cover_letter(job_description="Pay is $100k, uses {json} and $tone")
    assert "Pay is $100k, uses {json} and $tone" in rendered


def test_long_input_is_truncated():
    rendered = render_cover_letter(resume="x" * (prompts.MAX_INPUT_CHARS + 500))
    assert "x" * prompts.MAX_INPUT_CHARS in rendered
    assert "x" * (prompts.MAX_INPUT_CHARS + 1) not in rendered


def test_every_tone_option_has_a_prompt():
    assert {tone.value for tone in schemas.CoverLetterTone} == set(prompts.COVER_LETTER_TONES)

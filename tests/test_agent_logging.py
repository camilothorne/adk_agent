import logging
from typing import cast

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse
from google.genai.types import Content, Part

from query_companion.agent import _NonTextPartsWarningFilter, _log_llm_response


def test_filters_only_genai_non_text_parts_warning() -> None:
    warning_filter = _NonTextPartsWarningFilter()
    known_warning = logging.LogRecord(
        "google_genai.types",
        logging.WARNING,
        __file__,
        1,
        "Warning: there are non-text parts in the response: ['function_call']",
        (),
        None,
    )
    other_warning = logging.LogRecord(
        "google_genai.types", logging.WARNING, __file__, 1, "other warning", (), None
    )

    assert not warning_filter.filter(known_warning)
    assert warning_filter.filter(other_warning)


def test_llm_text_response_is_logged_at_info(caplog) -> None:
    response = LlmResponse(
        content=Content(
            parts=[
                Part(text="User-facing answer."),
                Part(text="Private thought.", thought=True),
            ]
        )
    )

    with caplog.at_level(logging.INFO, logger="query_companion.agent"):
        _log_llm_response(
            callback_context=cast(CallbackContext, None),
            llm_response=response,
        )

    assert "INFO" in caplog.text
    assert "LLM response: User-facing answer." in caplog.text
    assert "Private thought" not in caplog.text
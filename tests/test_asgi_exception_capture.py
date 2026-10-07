import pytest

from query_companion.server import CaptureCompletedResponseCancelScopeError


def _http_scope() -> dict:
    return {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "method": "GET",
        "path": "/",
        "raw_path": b"/",
        "query_string": b"",
        "headers": [],
    }


@pytest.mark.asyncio
async def test_captures_cancel_scope_mismatch_after_response(caplog) -> None:
    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"done"})
        raise RuntimeError(
            "Attempted to exit a cancel scope that isn't the current tasks's "
            "current cancel scope"
        )

    sent = []

    async def send(message):
        sent.append(message)

    await CaptureCompletedResponseCancelScopeError(app)(_http_scope(), None, send)

    assert sent[-1]["body"] == b"done"
    assert "Captured AnyIO cancel-scope mismatch" in caplog.text


@pytest.mark.asyncio
async def test_reraises_cancel_scope_mismatch_before_response_completes() -> None:
    async def app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b"partial", "more_body": True})
        raise RuntimeError(
            "Attempted to exit cancel scope in a different task than it was entered in"
        )

    async def send(message):
        pass

    with pytest.raises(RuntimeError, match="different task"):
        await CaptureCompletedResponseCancelScopeError(app)(_http_scope(), None, send)


@pytest.mark.asyncio
async def test_reraises_unrelated_error_after_response_completes() -> None:
    async def app(scope, receive, send):
        await send({"type": "http.response.body", "body": b"done"})
        raise RuntimeError("unrelated error")

    async def send(message):
        pass

    with pytest.raises(RuntimeError, match="unrelated error"):
        await CaptureCompletedResponseCancelScopeError(app)(_http_scope(), None, send)
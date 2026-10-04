"""Thin wrapper around the Claude API.

Endpoints never import the Anthropic SDK directly — they ask FastAPI for an
`AIClient` through the `get_ai_client` dependency. That gives us one place
to handle errors, and lets tests swap in a fake client so the test suite
never makes real (paid, slow, non-deterministic) API calls.
"""

from functools import lru_cache

import anthropic
from fastapi import HTTPException

import config


class AIClient:
    def __init__(self, api_key: str, model: str, max_tokens: int):
        self._client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens

    def complete(self, system: str, prompt: str) -> str:
        """Send one prompt, return Claude's text reply."""
        try:
            message = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.RateLimitError:
            # Anthropic's own limit, not ours — tell the client to back off.
            raise HTTPException(status_code=503, detail="AI service is busy, try again shortly")
        except anthropic.APIError as error:
            # Bad key, outage, etc. Log the real reason server-side, but
            # don't leak provider internals to the browser.
            print(f"Claude API error: {error!r}")
            raise HTTPException(status_code=502, detail="AI service request failed")

        # A reply is a list of content blocks; we only ask for text.
        return "".join(block.text for block in message.content if block.type == "text").strip()


@lru_cache
def _build_client() -> AIClient:
    return AIClient(config.ANTHROPIC_API_KEY, config.ANTHROPIC_MODEL, config.AI_MAX_TOKENS)


def get_ai_client() -> AIClient:
    # Fail with a clear message instead of a stack trace when the key is
    # missing — the rest of the app (CRUD) still works without it.
    if not config.ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="AI features are not configured (missing ANTHROPIC_API_KEY)")
    return _build_client()

"""Per-IP rate limiting for cost-sensitive endpoints.

We use slowapi (a FastAPI/Starlette wrapper around the `limits` library) with an
in-process memory backend. That is sufficient for a single Cloud Run instance —
per-IP counters reset if a new instance is cold-started, but the goal here is
simply to defang trivial cost-runaway abuse against the public Cloud Run URL,
not to provide cluster-wide enforcement.

The key function honours `X-Forwarded-For` because Cloud Run terminates TLS at
its load balancer and forwards the real client IP in that header. Without this,
we'd key every request on the load-balancer's address and effectively rate-limit
everyone as a single user.
"""

from __future__ import annotations

from fastapi import Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded


def _client_ip(request: Request) -> str:
    """Return the real client IP, preferring the first `X-Forwarded-For` entry.

    Cloud Run sets `X-Forwarded-For: <client-ip>, <lb-ip>, ...`. We take the
    leftmost address since that's the original client. Falls back to
    `request.client.host` if the header is missing (e.g. local dev).
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # XFF can be a comma-separated chain of proxies; the originating client
        # is the first entry.
        first = forwarded.split(",")[0].strip()
        if first:
            return first
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


# Limits applied to cost-sensitive endpoints.
# The per-minute limit blunts burst abuse; the per-day limit caps sustained
# scraping so a single attacker can't quietly run up the Vertex AI bill.
GENERATE_LIMITS = ["5/minute", "50/day"]


# headers_enabled is left False because slowapi's header-injection path requires
# every limited endpoint to return a Starlette `Response` (or accept one as a
# parameter). Our handler returns a Pydantic model, so we forgo the
# `X-RateLimit-*` advisory headers in exchange for a clean handler signature.
# The 429 response still carries enough information for the client.
limiter = Limiter(key_func=_client_ip)


__all__ = ["limiter", "GENERATE_LIMITS", "RateLimitExceeded", "_client_ip"]

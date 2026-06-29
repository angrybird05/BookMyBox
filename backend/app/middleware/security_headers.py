"""
Security headers middleware for FastAPI responses.
Pure ASGI middleware — exceptions flow through naturally so outer middleware (e.g. CORS)
always gets to process the final response.
"""

from starlette.types import ASGIApp, Receive, Scope, Send


class SecurityHeadersMiddleware:
    """ASGI middleware that adds standard security headers to protect against common web vulnerabilities."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope["path"]

        async def send_with_headers(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # Prevent clickjacking
                headers.append((b"x-frame-options", b"DENY"))

                # Prevent MIME type sniffing
                headers.append((b"x-content-type-options", b"nosniff"))

                # XSS protection for older browsers
                headers.append((b"x-xss-protection", b"1; mode=block"))

                # Strict Transport Security (HSTS)
                headers.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains; preload"))

                # Referrer Policy
                headers.append((b"referrer-policy", b"strict-origin-when-cross-origin"))

                # Content Security Policy
                if path in ("/docs", "/redoc"):
                    headers.append((
                        b"content-security-policy",
                        b"default-src 'self'; "
                        b"script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; "
                        b"style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                        b"img-src 'self' data: https://fastapi.tiangolo.com;",
                    ))
                else:
                    headers.append((
                        b"content-security-policy",
                        b"default-src 'self'; frame-ancestors 'none';",
                    ))

                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)

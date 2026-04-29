import logging


logger = logging.getLogger(__name__)


class AccessAuditMiddleware:
    """
    Lightweight audit for forbidden access attempts on protected routes.
    """

    PROTECTED_PREFIXES = (
        "/teacher/",
        "/student-passport/",
        "/ai-learning-assistant/",
        "/api/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            response.status_code == 403
            and request.path.startswith(self.PROTECTED_PREFIXES)
        ):
            username = (
                request.user.username
                if getattr(request, "user", None) and request.user.is_authenticated
                else "anonymous"
            )
            logger.warning(
                "403 access denied: user=%s path=%s method=%s",
                username,
                request.path,
                request.method,
            )
        return response

